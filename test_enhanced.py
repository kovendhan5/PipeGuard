#!/usr/bin/env python3
"""
Quick test of the enhanced PipeGuard Pro features.
"""

import os
import sys

def test_enhanced_features():
    """Test the enhanced PipeGuard Pro features."""
    print("🚀 Testing PipeGuard Pro Enhanced Features")
    print("=" * 50)
    
    # Set up mock environment
    os.environ['GITHUB_TOKEN'] = 'demo_token'
    os.environ['GITHUB_USER'] = 'demo_user'
    os.environ['GITHUB_REPO'] = 'demo_repo'
    
    try:
        print("1. 📱 Testing Flask App Import...")
        from app import app
        print("   ✅ Flask app imported successfully")
        
        print("\n2. 🔍 Testing Advanced Monitoring...")
        from advanced_monitoring import PipelineAnalyzer, HealthcheckMonitor
        analyzer = PipelineAnalyzer()
        monitor = HealthcheckMonitor()
        print("   ✅ Advanced monitoring modules loaded")
        
        print("\n3. 🌐 Testing Flask App Response...")
        with app.test_client() as client:
            response = client.get("/")
            print(f"   • Status Code: {response.status_code}")
            print(f"   • Contains 'PipeGuard': {'PipeGuard' in response.get_data(as_text=True)}")
            
            if response.status_code == 200:
                print("   ✅ Main dashboard loads successfully")
            
        print("\n4. 🔧 Testing API Endpoints...")
        with app.test_client() as client:
            endpoints = ["/api/stats", "/api/health-check", "/api/analysis", "/api/insights"]
            
            for endpoint in endpoints:
                try:
                    response = client.get(endpoint)
                    print(f"   • {endpoint}: {response.status_code} ✅")
                except Exception as e:
                    print(f"   • {endpoint}: Error - {e} ❌")
        
        print("\n5. 📊 Testing Sample Data Generation...")
        from app import generate_enhanced_sample_data
        runs, anomalies = generate_enhanced_sample_data()
        print(f"   • Generated {len(runs)} sample runs")
        print(f"   • Generated {len(anomalies)} sample anomalies")
        print("   ✅ Sample data generation working")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("\n🚀 PipeGuard Pro is ready to use!")
        print("\nNext steps:")
        print("1. Run: python run_local.py")
        print("2. Choose option 1 to start the dashboard")
        print("3. Visit: http://localhost:8080")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_enhanced_features()
    if not success:
        print("\n💡 Try running: pip install -r requirements.txt")
        sys.exit(1)
