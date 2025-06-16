"""
Advanced monitoring features for PipeGuard.
Includes real-time notifications, performance analysis, and predictive insights.
"""

import os
import json
import smtplib
from email.mime.text import MIMEText as MimeText
from email.mime.multipart import MIMEMultipart as MimeMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any
import statistics


class PipelineAnalyzer:
    """Advanced pipeline performance analyzer."""
    
    def __init__(self):
        self.performance_thresholds = {
            'duration_warning': 120,  # seconds
            'duration_critical': 300,  # seconds
            'failure_rate_warning': 0.1,  # 10%
            'failure_rate_critical': 0.2,  # 20%
        }
    
    def analyze_performance_trends(self, runs: List[Dict]) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        if not runs:
            return {"error": "No runs data available"}
        
        # Sort runs by timestamp
        sorted_runs = sorted(runs, key=lambda x: x.get('timestamp', ''))
        
        # Calculate moving averages
        durations = [run.get('duration', 0) for run in sorted_runs]
        success_rates = self._calculate_rolling_success_rates(sorted_runs)
        
        return {
            "duration_trend": self._calculate_trend(durations),
            "success_rate_trend": self._calculate_trend(success_rates),
            "performance_score": self._calculate_performance_score(sorted_runs),
            "recommendations": self._generate_recommendations(sorted_runs),
            "prediction": self._predict_next_run_performance(sorted_runs)
        }
    
    def _calculate_rolling_success_rates(self, runs: List[Dict], window_size: int = 5) -> List[float]:
        """Calculate rolling success rates."""
        success_rates = []
        for i in range(len(runs)):
            start_idx = max(0, i - window_size + 1)
            window_runs = runs[start_idx:i+1]
            successes = sum(1 for run in window_runs if run.get('status') == 'success')
            success_rate = successes / len(window_runs) if window_runs else 0
            success_rates.append(success_rate)
        return success_rates
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values."""
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend calculation
        x = list(range(len(values)))
        n = len(values)
        
        if n == 0:
            return "stable"
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        # Calculate slope
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
        
        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "degrading"
        else:
            return "stable"
    
    def _calculate_performance_score(self, runs: List[Dict]) -> int:
        """Calculate overall performance score (0-100)."""
        if not runs:
            return 50
        
        recent_runs = runs[-10:]  # Last 10 runs
        
        # Success rate component (40%)
        successes = sum(1 for run in recent_runs if run.get('status') == 'success')
        success_rate = successes / len(recent_runs)
        success_score = success_rate * 40
        
        # Duration component (30%)
        durations = [run.get('duration', 0) for run in recent_runs]
        avg_duration = statistics.mean(durations) if durations else 0
        duration_score = max(0, (180 - avg_duration) / 180) * 30  # Good if under 3 minutes
        
        # Consistency component (30%)
        duration_std = statistics.stdev(durations) if len(durations) > 1 else 0
        consistency_score = max(0, (60 - duration_std) / 60) * 30  # Good if low variance
        
        total_score = success_score + duration_score + consistency_score
        return int(min(100, max(0, total_score)))
    
    def _generate_recommendations(self, runs: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on pipeline performance."""
        recommendations = []
        
        if not runs:
            return ["No data available for analysis"]
        
        recent_runs = runs[-10:]
        
        # Analyze failure patterns
        failures = [run for run in recent_runs if run.get('status') == 'failure']
        failure_rate = len(failures) / len(recent_runs)
        
        if failure_rate > self.performance_thresholds['failure_rate_critical']:
            recommendations.append("🚨 Critical: High failure rate detected. Review recent changes and test coverage.")
        elif failure_rate > self.performance_thresholds['failure_rate_warning']:
            recommendations.append("⚠️ Warning: Increased failure rate. Monitor test stability.")
        
        # Analyze duration patterns
        durations = [run.get('duration', 0) for run in recent_runs]
        avg_duration = statistics.mean(durations) if durations else 0
        
        if avg_duration > self.performance_thresholds['duration_critical']:
            recommendations.append("🚨 Critical: Build times are very slow. Consider optimizing build process.")
        elif avg_duration > self.performance_thresholds['duration_warning']:
            recommendations.append("⚠️ Warning: Build times are increasing. Review build efficiency.")
        
        # Analyze consistency
        if len(durations) > 1:
            duration_std = statistics.stdev(durations)
            if duration_std > 60:  # High variance
                recommendations.append("📊 Build times are inconsistent. Investigate resource allocation.")
        
        if not recommendations:
            recommendations.append("✅ Pipeline performance looks good! Keep up the excellent work.")
        
        return recommendations
    
    def _predict_next_run_performance(self, runs: List[Dict]) -> Dict[str, Any]:
        """Predict next run performance based on recent trends."""
        if len(runs) < 3:
            return {"error": "Insufficient data for prediction"}
        
        recent_runs = runs[-5:]  # Last 5 runs for prediction
        durations = [run.get('duration', 0) for run in recent_runs]
        
        # Simple prediction based on recent average and trend
        avg_duration = statistics.mean(durations)
        trend = self._calculate_trend(durations)
        
        predicted_duration = avg_duration
        confidence = "medium"
        
        if trend == "improving":
            predicted_duration *= 0.9  # Expect 10% improvement
            confidence = "high"
        elif trend == "degrading":
            predicted_duration *= 1.1  # Expect 10% degradation
            confidence = "high"
        
        # Predict success probability based on recent performance
        recent_successes = sum(1 for run in recent_runs if run.get('status') == 'success')
        success_probability = recent_successes / len(recent_runs)
        
        return {
            "predicted_duration": round(predicted_duration, 1),
            "success_probability": round(success_probability * 100, 1),
            "confidence": confidence,
            "trend": trend
        }


class NotificationManager:
    """Manages notifications for pipeline events."""
    
    def __init__(self):
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_USERNAME', ''),
            'password': os.getenv('EMAIL_PASSWORD', ''),
            'from_email': os.getenv('FROM_EMAIL', ''),
        }
    
    def send_failure_alert(self, run_data: Dict, anomaly_data: Dict):
        """Send email alert for pipeline failures."""
        if not self.email_config['username']:
            print("Email configuration not found. Skipping notification.")
            return False
        
        subject = f"🚨 Pipeline Failure Alert - Run #{run_data.get('id', 'Unknown')}"
        
        body = f"""
        Pipeline Failure Detected!
        
        Run Details:
        - Run ID: {run_data.get('id', 'Unknown')}
        - Status: {run_data.get('status', 'Unknown')}
        - Duration: {run_data.get('duration', 'Unknown')} seconds
        - Branch: {run_data.get('branch', 'Unknown')}
        - Timestamp: {run_data.get('timestamp', 'Unknown')}
        
        Anomaly Details:
        - Issue: {anomaly_data.get('issue', 'Unknown')}
        - Suggested Fix: {anomaly_data.get('fix', 'No suggestion available')}
        - Severity: {anomaly_data.get('severity', 'Unknown')}
        
        Please investigate and resolve the issue promptly.
        
        View Dashboard: http://localhost:8080
        """
        
        return self._send_email(subject, body)
    
    def send_performance_summary(self, stats: Dict, recommendations: List[str]):
        """Send daily performance summary."""
        if not self.email_config['username']:
            print("Email configuration not found. Skipping notification.")
            return False
        
        subject = "📊 Daily Pipeline Performance Summary"
        
        recommendations_text = "\n".join(f"- {rec}" for rec in recommendations)
        
        body = f"""
        Daily Pipeline Performance Summary
        
        Statistics:
        - Total Runs: {stats.get('total_runs', 0)}
        - Success Rate: {stats.get('success_rate', 0)}%
        - Average Duration: {stats.get('avg_duration', 0)} seconds
        - Total Failures: {stats.get('total_failures', 0)}
        
        Recommendations:
        {recommendations_text}
        
        View Dashboard: http://localhost:8080
        """
        
        return self._send_email(subject, body)
    
    def _send_email(self, subject: str, body: str) -> bool:
        """Send email notification."""
        try:
            msg = MimeMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = self.email_config['username']  # Send to self for demo
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            
            server.send_message(msg)
            server.quit()
            
            print(f"Email notification sent: {subject}")
            return True
            
        except Exception as e:
            print(f"Failed to send email notification: {e}")
            return False


class HealthcheckMonitor:
    """Monitors overall pipeline health and generates alerts."""
    
    def __init__(self):
        self.analyzer = PipelineAnalyzer()
        self.notifier = NotificationManager()
    
    def check_pipeline_health(self, runs: List[Dict], anomalies: List[Dict]) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        
        # Analyze performance trends
        performance_analysis = self.analyzer.analyze_performance_trends(runs)
        
        # Calculate health metrics
        health_metrics = {
            "overall_health": self._calculate_overall_health(runs, anomalies),
            "performance_analysis": performance_analysis,
            "alert_level": self._determine_alert_level(runs, anomalies),
            "last_updated": datetime.now().isoformat(),
        }
        
        # Generate alerts if needed
        self._generate_alerts_if_needed(health_metrics, runs, anomalies)
        
        return health_metrics
    
    def _calculate_overall_health(self, runs: List[Dict], anomalies: List[Dict]) -> str:
        """Calculate overall pipeline health status."""
        if not runs:
            return "unknown"
        
        recent_runs = runs[-10:]  # Last 10 runs
        recent_anomalies = anomalies[-5:]  # Last 5 anomalies
        
        # Check recent failures
        recent_failures = sum(1 for run in recent_runs if run.get('status') == 'failure')
        failure_rate = recent_failures / len(recent_runs)
        
        # Check severe anomalies
        severe_anomalies = sum(1 for anomaly in recent_anomalies 
                             if anomaly.get('severity') in ['high', 'critical'])
        
        if failure_rate > 0.3 or severe_anomalies > 2:
            return "critical"
        elif failure_rate > 0.1 or severe_anomalies > 0:
            return "warning"
        else:
            return "healthy"
    
    def _determine_alert_level(self, runs: List[Dict], anomalies: List[Dict]) -> str:
        """Determine appropriate alert level."""
        health = self._calculate_overall_health(runs, anomalies)
        
        if health == "critical":
            return "high"
        elif health == "warning":
            return "medium"
        else:
            return "low"
    
    def _generate_alerts_if_needed(self, health_metrics: Dict, runs: List[Dict], anomalies: List[Dict]):
        """Generate alerts based on health metrics."""
        alert_level = health_metrics.get('alert_level', 'low')
        
        if alert_level in ['high', 'medium'] and runs:
            latest_run = runs[0] if runs else {}
            latest_anomaly = anomalies[0] if anomalies else {}
            
            # Send failure alert for high-priority issues
            if alert_level == 'high':
                self.notifier.send_failure_alert(latest_run, latest_anomaly)
            
            print(f"Alert generated: {alert_level} priority - {health_metrics.get('overall_health', 'unknown')} health")
