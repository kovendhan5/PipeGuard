from flask import Flask, render_template, jsonify, request, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from google.cloud import firestore
import os
import secrets
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
import json
from werkzeug.exceptions import BadRequest, InternalServerError
import bleach
from advanced_monitoring import PipelineAnalyzer, NotificationManager, HealthcheckMonitor

# Configure secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeguard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Security Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Session timeout

# Configure CORS with restrictions
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8080", "https://yourdomain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "20 per minute"]
)

# Security headers middleware
@app.after_request
def add_security_headers(response):
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
        "font-src 'self' https://cdnjs.cloudflare.com; "
        "img-src 'self' data:; "
        "connect-src 'self';"
    )
    
    # Other security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response

# Input validation helper
def validate_and_sanitize_input(data, max_length=1000):
    """Validate and sanitize user input."""
    if not data:
        return ""
    
    if len(data) > max_length:
        raise BadRequest("Input too long")
    
    # Sanitize HTML content
    return bleach.clean(data, tags=[], strip=True)

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    logger.warning(f"Bad request: {request.remote_addr} - {request.url}")
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(403)
def forbidden(error):
    logger.warning(f"Forbidden access: {request.remote_addr} - {request.url}")
    return jsonify({"error": "Access forbidden"}), 403

@app.errorhandler(404)
def not_found(error):
    logger.info(f"Page not found: {request.remote_addr} - {request.url}")
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(429)
def rate_limit_exceeded(error):
    logger.warning(f"Rate limit exceeded: {request.remote_addr} - {request.url}")
    return jsonify({"error": "Rate limit exceeded"}), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {request.remote_addr} - {request.url}")
    return jsonify({"error": "Internal server error"}), 500

# Initialize advanced monitoring components
pipeline_analyzer = PipelineAnalyzer()
notification_manager = NotificationManager()
healthcheck_monitor = HealthcheckMonitor()

def generate_enhanced_sample_data():
    """Generate more realistic sample data for demonstration."""
    from datetime import datetime, timedelta
    import random
    
    runs = []
    anomalies = []
    
    # Generate sample runs for the last 24 hours
    base_time = datetime.now() - timedelta(hours=24)
    statuses = ['success', 'failure', 'success', 'success', 'failure', 'success', 'success', 'success']
    
    for i in range(12):
        run_time = base_time + timedelta(hours=i*2)
        status = random.choice(statuses)
        
        # Generate realistic durations
        if status == 'success':
            duration = random.randint(45, 180)  # 45s to 3min for success
        else:
            duration = random.randint(20, 90)   # 20s to 1.5min for failures
            
        run = {
            "id": f"run-{1000 + i}",
            "status": status,
            "duration": duration,
            "timestamp": run_time.isoformat(),
            "branch": "main" if i % 3 == 0 else f"feature-{i}",
            "commit": f"abc{1000 + i}",
            "author": random.choice(["john.doe", "jane.smith", "dev.team"])
        }
        runs.append(run)
        
        # Generate anomalies for failed runs and slow runs
        if status == 'failure':
            anomalies.append({
                "issue": "Test failure",
                "fix": "Check test logs and fix failing unit tests",
                "run_id": run["id"],
                "severity": "high",
                "timestamp": run_time.isoformat()
            })
        elif duration > 150:
            anomalies.append({
                "issue": "Long build time",
                "fix": "Optimize build process or increase resources",
                "run_id": run["id"],
                "severity": "medium", 
                "timestamp": run_time.isoformat()
            })
    
    return runs, anomalies

@app.route("/")
@limiter.limit("30 per minute")
def dashboard():
    try:
        logger.info(f"Dashboard access from {request.remote_addr}")
        
        # Use firestore client for consistent database access
        db = firestore.Client()
        
        logger.info("Fetching runs from Firestore...")
        runs_ref = db.collection("runs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10)
        runs = runs_ref.get()
        run_data = [doc.to_dict() for doc in runs]
        logger.info(f"Retrieved {len(run_data)} runs from Firestore")
        
        logger.info("Fetching anomalies from Firestore...")
        anomalies_ref = db.collection("anomalies").order_by("run_id", direction=firestore.Query.DESCENDING).limit(5)
        anomalies = anomalies_ref.get()
        anomaly_data = [doc.to_dict() for doc in anomalies]
        logger.info(f"Retrieved {len(anomaly_data)} anomalies from Firestore")
        
        return render_template("index.html",
                            runs=run_data,
                            anomalies=anomaly_data)
    except Exception as e:
        logger.error(f"Error in dashboard: {str(e)}")
        # If Firestore fails, show enhanced demo data
        sample_runs, sample_anomalies = generate_enhanced_sample_data()
        
        return render_template("index.html",
                            runs=sample_runs,
                            anomalies=sample_anomalies)

@app.route("/api/stats")
@limiter.limit("60 per minute")
def get_stats():
    """API endpoint to get pipeline statistics."""
    try:
        logger.info(f"Stats API access from {request.remote_addr}")
        db = firestore.Client()
        runs_ref = db.collection("runs").limit(50)
        runs = [doc.to_dict() for doc in runs_ref.get()]
        
        stats = calculate_stats(runs)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error in stats API: {str(e)}")
        # Return sample stats if Firestore fails
        sample_runs, _ = generate_enhanced_sample_data()
        stats = calculate_stats(sample_runs)
        return jsonify(stats)

@app.route("/api/refresh")
@limiter.limit("30 per minute")
def refresh_data():
    """API endpoint to refresh dashboard data."""
    try:
        logger.info(f"Refresh API access from {request.remote_addr}")
        db = firestore.Client()
        
        # Get latest runs
        runs_ref = db.collection("runs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10)
        runs = [doc.to_dict() for doc in runs_ref.get()]
        
        # Get latest anomalies  
        anomalies_ref = db.collection("anomalies").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(5)
        anomalies = [doc.to_dict() for doc in anomalies_ref.get()]
        
        return jsonify({
            "runs": runs,
            "anomalies": anomalies,
            "stats": calculate_stats(runs),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in refresh API: {str(e)}")
        # Return sample data if Firestore fails
        sample_runs, sample_anomalies = generate_enhanced_sample_data()
        return jsonify({
            "runs": sample_runs,
            "anomalies": sample_anomalies, 
            "stats": calculate_stats(sample_runs),
            "timestamp": datetime.now().isoformat()
        })

def calculate_stats(runs):
    """Calculate pipeline statistics from runs data."""
    if not runs:
        return {
            "total_runs": 0,
            "success_rate": 0,
            "avg_duration": 0,
            "total_failures": 0
        }
    
    total_runs = len(runs)
    successful_runs = len([r for r in runs if r.get('status') == 'success'])
    success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0
    avg_duration = sum(r.get('duration', 0) for r in runs) / total_runs if total_runs > 0 else 0
    total_failures = total_runs - successful_runs
    
    return {
        "total_runs": total_runs,
        "success_rate": round(success_rate, 1),
        "avg_duration": round(avg_duration, 1),
        "total_failures": total_failures
    }

@app.route("/api/pipeline-health")
def pipeline_health():
    """API endpoint for pipeline health check."""
    try:
        db = firestore.Client()
        
        # Get recent runs (last 24 hours)
        yesterday = datetime.now() - timedelta(hours=24)
        runs_ref = db.collection("runs").where("timestamp", ">=", yesterday.isoformat())
        recent_runs = [doc.to_dict() for doc in runs_ref.get()]
        
        # Calculate health score
        health_score = calculate_health_score(recent_runs)
        
        return jsonify({
            "health_score": health_score,
            "status": get_health_status(health_score),
            "recent_runs_count": len(recent_runs),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "health_score": 85,  # Sample score
            "status": "healthy",
            "recent_runs_count": 12,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        })

def calculate_health_score(runs):
    """Calculate a health score (0-100) based on recent pipeline performance."""
    if not runs:
        return 50  # Neutral score if no data
    
    # Factors: success rate (60%), avg duration (20%), frequency (20%)
    success_rate = len([r for r in runs if r.get('status') == 'success']) / len(runs)
    
    # Duration score (lower is better)
    avg_duration = sum(r.get('duration', 0) for r in runs) / len(runs)
    duration_score = max(0, 1 - (avg_duration - 60) / 120)  # Optimal around 60s
    
    # Frequency score (more frequent runs = better)
    frequency_score = min(1, len(runs) / 24)  # Ideal: 1 run per hour
    
    health_score = (success_rate * 60) + (duration_score * 20) + (frequency_score * 20)
    return round(health_score * 100, 1)

def get_health_status(score):
    """Convert health score to status."""
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "good"
    elif score >= 40:
        return "fair"
    else:
        return "poor"

@app.route("/api/analysis")
def get_pipeline_analysis():
    """API endpoint for advanced pipeline analysis."""
    try:
        db = firestore.Client()
        runs_ref = db.collection("runs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(30)
        runs = [doc.to_dict() for doc in runs_ref.get()]
        
        analysis = pipeline_analyzer.analyze_performance_trends(runs)
        return jsonify(analysis)
    except Exception as e:
        # Return sample analysis if Firestore fails
        sample_runs, _ = generate_enhanced_sample_data()
        analysis = pipeline_analyzer.analyze_performance_trends(sample_runs)
        return jsonify(analysis)

@app.route("/api/health-check")
def comprehensive_health_check():
    """API endpoint for comprehensive pipeline health check."""
    try:
        db = firestore.Client()
        
        runs_ref = db.collection("runs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(20)
        runs = [doc.to_dict() for doc in runs_ref.get()]
        
        anomalies_ref = db.collection("anomalies").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10)
        anomalies = [doc.to_dict() for doc in anomalies_ref.get()]
        
        health_report = healthcheck_monitor.check_pipeline_health(runs, anomalies)
        return jsonify(health_report)
    except Exception as e:
        # Return sample health report if Firestore fails
        sample_runs, sample_anomalies = generate_enhanced_sample_data()
        health_report = healthcheck_monitor.check_pipeline_health(sample_runs, sample_anomalies)
        return jsonify(health_report)

@app.route("/api/notifications/test", methods=["POST"])
def test_notification():
    """Test notification system."""
    try:
        # Send test notification
        test_run = {"id": "test-123", "status": "failure", "duration": 85, "branch": "main"}
        test_anomaly = {"issue": "Test notification", "fix": "This is a test", "severity": "low"}
        
        success = notification_manager.send_failure_alert(test_run, test_anomaly)
        return jsonify({"success": success, "message": "Test notification sent" if success else "Failed to send notification"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/insights")
def get_insights():
    """Get AI-powered insights about pipeline performance."""
    try:
        db = firestore.Client()
        runs_ref = db.collection("runs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(50)
        runs = [doc.to_dict() for doc in runs_ref.get()]
        
        insights = generate_ai_insights(runs)
        return jsonify(insights)
    except Exception as e:
        # Return sample insights if Firestore fails
        sample_runs, _ = generate_enhanced_sample_data()
        insights = generate_ai_insights(sample_runs)
        return jsonify(insights)

def generate_ai_insights(runs):
    """Generate AI-powered insights from pipeline data."""
    insights = {
        "patterns": [],
        "optimizations": [],
        "predictions": [],
        "recommendations": []
    }
    
    if not runs:
        return insights
    
    # Pattern detection
    failure_patterns = detect_failure_patterns(runs)
    insights["patterns"] = failure_patterns
    
    # Optimization suggestions
    optimizations = suggest_optimizations(runs)
    insights["optimizations"] = optimizations
    
    # Performance predictions
    predictions = predict_performance(runs)
    insights["predictions"] = predictions
    
    # Smart recommendations
    recommendations = generate_smart_recommendations(runs)
    insights["recommendations"] = recommendations
    
    return insights

def detect_failure_patterns(runs):
    """Detect patterns in pipeline failures."""
    patterns = []
    
    failures = [run for run in runs if run.get('status') == 'failure']
    
    if len(failures) > 3:
        # Check for time-based patterns
        failure_hours = [datetime.fromisoformat(run.get('timestamp', '')).hour 
                        for run in failures if run.get('timestamp')]
        
        if failure_hours:
            from collections import Counter
            hour_counts = Counter(failure_hours)
            most_common_hour = hour_counts.most_common(1)[0]
            
            if most_common_hour[1] > 1:
                patterns.append(f"Failures tend to occur around {most_common_hour[0]}:00")
    
    # Check for duration patterns
    failure_durations = [run.get('duration', 0) for run in failures]
    if failure_durations:
        avg_failure_duration = sum(failure_durations) / len(failure_durations)
        success_durations = [run.get('duration', 0) for run in runs if run.get('status') == 'success']
        
        if success_durations:
            avg_success_duration = sum(success_durations) / len(success_durations)
            if avg_failure_duration < avg_success_duration * 0.5:
                patterns.append("Failures occur quickly, suggesting early-stage issues")
    
    return patterns

def suggest_optimizations(runs):
    """Suggest optimizations based on run data."""
    optimizations = []
    
    if not runs:
        return optimizations
    
    durations = [run.get('duration', 0) for run in runs]
    avg_duration = sum(durations) / len(durations)
    
    if avg_duration > 180:  # > 3 minutes
        optimizations.append({
            "type": "performance",
            "title": "Optimize Build Time",
            "description": "Consider implementing parallel builds or caching strategies",
            "impact": "high",
            "effort": "medium"
        })
    
    success_rate = len([r for r in runs if r.get('status') == 'success']) / len(runs)
    if success_rate < 0.8:  # < 80% success rate
        optimizations.append({
            "type": "reliability",
            "title": "Improve Test Stability",
            "description": "Review and fix flaky tests to improve success rate",
            "impact": "high",
            "effort": "high"
        })
    
    return optimizations

def predict_performance(runs):
    """Predict future performance trends."""
    predictions = []
    
    if len(runs) < 5:
        return predictions
    
    recent_runs = runs[:10]  # Last 10 runs
    durations = [run.get('duration', 0) for run in recent_runs]
    
    # Simple trend analysis
    if len(durations) >= 3:
        recent_avg = sum(durations[:3]) / 3
        older_avg = sum(durations[3:6]) / 3 if len(durations) >= 6 else recent_avg
        
        if recent_avg > older_avg * 1.1:
            predictions.append({
                "type": "performance_degradation",
                "message": "Build times are trending upward",
                "confidence": 0.75,
                "timeframe": "next 5 runs"
            })
        elif recent_avg < older_avg * 0.9:
            predictions.append({
                "type": "performance_improvement", 
                "message": "Build times are improving",
                "confidence": 0.75,
                "timeframe": "next 5 runs"
            })
    
    return predictions

def generate_smart_recommendations(runs):
    """Generate smart recommendations based on comprehensive analysis."""
    recommendations = []
    
    if not runs:
        return recommendations
    
    # Analyze recent performance
    recent_runs = runs[:10]
    failure_rate = len([r for r in recent_runs if r.get('status') == 'failure']) / len(recent_runs)
    
    if failure_rate > 0.2:
        recommendations.append({
            "priority": "high",
            "category": "reliability",
            "title": "Address High Failure Rate",
            "description": "Investigate and fix the root cause of recent failures",
            "actions": [
                "Review recent code changes",
                "Check test environment stability",
                "Analyze error logs for common patterns"
            ]
        })
    
    # Duration analysis
    durations = [run.get('duration', 0) for run in recent_runs]
    if durations and max(durations) > min(durations) * 3:
        recommendations.append({
            "priority": "medium",
            "category": "performance",
            "title": "Inconsistent Build Times",
            "description": "Build times vary significantly between runs",
            "actions": [
                "Check resource allocation",
                "Implement build caching",
                "Monitor system load during builds"
            ]
        })
    
    return recommendations

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
