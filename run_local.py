#!/usr/bin/env python3
"""
Enhanced local development runner for PipeGuard Pro.
This script sets up the environment for local testing with advanced features.
"""

import os
import sys
import time
import threading
from datetime import datetime

def setup_environment():
    """Set up environment variables for local development."""
    print("🔧 Setting up secure local development environment...")
    
    # Import secure setup
    try:
        from secure_setup import setup_development_env
        setup_development_env()
    except ImportError:
        # Fallback to basic setup
        import secrets
        os.environ['SECRET_KEY'] = secrets.token_urlsafe(32)
        os.environ.setdefault('DEBUG', 'False')  # Secure by default
        os.environ.setdefault('GITHUB_TOKEN', 'demo_token_for_local_dev')
        os.environ.setdefault('GITHUB_USER', 'demo_user')
        os.environ.setdefault('GITHUB_REPO', 'demo_repo')
    
    os.environ.setdefault('FLASK_HOST', '0.0.0.0')
    os.environ.setdefault('FLASK_PORT', '8080')
    
    # Advanced monitoring settings
    os.environ.setdefault('DURATION_WARNING_THRESHOLD', '120')
    os.environ.setdefault('DURATION_CRITICAL_THRESHOLD', '300')
    os.environ.setdefault('FAILURE_RATE_WARNING', '0.1')
    os.environ.setdefault('FAILURE_RATE_CRITICAL', '0.2')
    os.environ.setdefault('AUTO_REFRESH_INTERVAL', '30')
    
    print("✅ Environment configured securely for local development")

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'flask', 'pytest', 'google-cloud-firestore', 
        'requests', 'python-dotenv', 'functions-framework'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def display_banner():
    """Display the PipeGuard Pro banner."""
    banner = """
    ██████╗ ██╗██████╗ ███████╗ ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗     ██████╗ ██████╗  ██████╗ 
    ██╔══██╗██║██╔══██╗██╔════╝██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗    ██╔══██╗██╔══██╗██╔═══██╗
    ██████╔╝██║██████╔╝█████╗  ██║  ███╗██║   ██║███████║██████╔╝██║  ██║    ██████╔╝██████╔╝██║   ██║
    ██╔═══╝ ██║██╔═══╝ ██╔══╝  ██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║    ██╔═══╝ ██╔══██╗██║   ██║
    ██║     ██║██║     ███████╗╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝    ██║     ██║  ██║╚██████╔╝
    ╚═╝     ╚═╝╚═╝     ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝     ╚═╝     ╚═╝  ╚═╝ ╚═════╝ 
    """
    print("\033[96m" + banner + "\033[0m")
    print("\033[92m" + "🚀 Advanced CI/CD Pipeline Monitoring System" + "\033[0m")
    print("\033[93m" + "=" * 80 + "\033[0m")

def show_menu():
    """Display the interactive menu."""
    print("\n🎯 Choose an option:")
    print("1. 🌐 Start Dashboard Server (Recommended)")
    print("2. 🧪 Run Tests")
    print("3. 📊 Test Monitor Function")
    print("4. 🔍 Verify Installation")
    print("5. 🛠️  Advanced Features Demo")
    print("6. 📧 Test Notifications")
    print("7. 📈 Performance Analysis Demo")
    print("8. ❌ Exit")
    return input("\nEnter your choice (1-8): ").strip()

def start_dashboard():
    """Start the Flask dashboard server."""
    print("\n🌐 Starting PipeGuard Pro Dashboard...")
    print("📊 Features available:")
    print("  • Real-time pipeline monitoring")
    print("  • Advanced performance analytics")
    print("  • Anomaly detection with AI insights")
    print("  • Interactive charts and visualizations")
    print("  • Auto-refresh capabilities")
    print("\n🔗 Dashboard will be available at: http://localhost:8080")
    print("⏰ Starting in 3 seconds... Press Ctrl+C to stop anytime")
    
    try:
        time.sleep(3)
        from app import app
        app.run(
            host=os.environ.get('FLASK_HOST', '0.0.0.0'),
            port=int(os.environ.get('FLASK_PORT', 8080)),
            debug=os.environ.get('DEBUG', 'True').lower() == 'true'
        )
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")

def run_tests():
    """Run the test suite."""
    print("\n🧪 Running PipeGuard Pro test suite...")
    os.system('python -m pytest test_app.py -v --tb=short')

def test_monitor():
    """Test the monitor pipeline function."""
    print("\n📊 Testing monitor pipeline function...")
    os.system('python test_monitor.py')

def verify_installation():
    """Verify the installation."""
    print("\n🔍 Verifying PipeGuard Pro installation...")
    os.system('python verify.py')

def demo_advanced_features():
    """Demonstrate advanced features."""
    print("\n🛠️  PipeGuard Pro Advanced Features Demo")
    print("=" * 50)
    
    try:
        from advanced_monitoring import PipelineAnalyzer, HealthcheckMonitor
        
        # Demo data
        sample_runs = [
            {"id": "run-1", "status": "success", "duration": 125, "timestamp": "2025-06-15T10:00:00"},
            {"id": "run-2", "status": "failure", "duration": 45, "timestamp": "2025-06-15T11:00:00"},
            {"id": "run-3", "status": "success", "duration": 110, "timestamp": "2025-06-15T12:00:00"},
        ]
        
        analyzer = PipelineAnalyzer()
        monitor = HealthcheckMonitor()
        
        print("📈 Performance Analysis:")
        analysis = analyzer.analyze_performance_trends(sample_runs)
        for key, value in analysis.items():
            print(f"  • {key}: {value}")
        
        print("\n🏥 Health Check:")
        health = monitor.check_pipeline_health(sample_runs, [])
        print(f"  • Overall Health: {health.get('overall_health', 'Unknown')}")
        print(f"  • Alert Level: {health.get('alert_level', 'Unknown')}")
        
        print("\n✅ Advanced features are working correctly!")
        
    except Exception as e:
        print(f"❌ Error demonstrating advanced features: {e}")

def test_notifications():
    """Test the notification system."""
    print("\n📧 Testing notification system...")
    print("⚠️  Note: Email notifications require proper SMTP configuration")
    
    try:
        from advanced_monitoring import NotificationManager
        
        notifier = NotificationManager()
        test_run = {"id": "test-123", "status": "failure", "duration": 85}
        test_anomaly = {"issue": "Test notification", "fix": "This is a test"}
        
        # This will only work if email is configured
        success = notifier.send_failure_alert(test_run, test_anomaly)
        
        if success:
            print("✅ Test notification sent successfully!")
        else:
            print("⚠️  Test notification failed (likely due to missing email config)")
            print("   Configure SMTP settings in .env file for real notifications")
            
    except Exception as e:
        print(f"❌ Error testing notifications: {e}")

def performance_analysis_demo():
    """Demonstrate performance analysis capabilities."""
    print("\n📈 Performance Analysis Demo")
    print("=" * 40)
    
    try:
        from app import generate_ai_insights
        
        # Generate sample data for demo
        sample_runs = []
        for i in range(20):
            status = "success" if i % 4 != 0 else "failure"  # 75% success rate
            duration = 90 + (i * 5) + (10 if status == "failure" else 0)
            
            sample_runs.append({
                "id": f"run-{i+1}",
                "status": status,
                "duration": duration,
                "timestamp": f"2025-06-15T{10 + i}:00:00"
            })
        
        insights = generate_ai_insights(sample_runs)
        
        print("🔍 AI-Powered Insights:")
        print(f"  • Patterns Detected: {len(insights.get('patterns', []))}")
        print(f"  • Optimization Suggestions: {len(insights.get('optimizations', []))}")
        print(f"  • Performance Predictions: {len(insights.get('predictions', []))}")
        print(f"  • Smart Recommendations: {len(insights.get('recommendations', []))}")
        
        if insights.get('patterns'):
            print("\n📊 Detected Patterns:")
            for pattern in insights['patterns']:
                print(f"    • {pattern}")
        
        if insights.get('optimizations'):
            print("\n🚀 Optimization Suggestions:")
            for opt in insights['optimizations']:
                print(f"    • {opt.get('title', 'Unknown')}: {opt.get('description', 'No description')}")
        
        print("\n✅ Performance analysis completed!")
        
    except Exception as e:
        print(f"❌ Error in performance analysis demo: {e}")

def main():
    """Main function to run the enhanced local development environment."""
    display_banner()
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: Please run this script from the PipeGuard project directory")
        sys.exit(1)
    
    setup_environment()
    
    if not check_dependencies():
        print("\n💡 Run 'pip install -r requirements.txt' to install missing dependencies")
        sys.exit(1)
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            start_dashboard()
        elif choice == '2':
            run_tests()
        elif choice == '3':
            test_monitor()
        elif choice == '4':
            verify_installation()
        elif choice == '5':
            demo_advanced_features()
        elif choice == '6':
            test_notifications()
        elif choice == '7':
            performance_analysis_demo()
        elif choice == '8':
            print("\n👋 Thank you for using PipeGuard Pro!")
            break
        else:
            print("\n❌ Invalid choice. Please select 1-8.")
        
        if choice != '1':  # Don't pause after starting dashboard
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
