#!/usr/bin/env python3
"""
Quick start script for PipeGuard Dashboard
"""

import os
import sys

# Set up environment for demo
os.environ['SECRET_KEY'] = 'demo_secret_key_for_testing'
os.environ['DEBUG'] = 'False'
os.environ['GITHUB_TOKEN'] = 'demo_token'
os.environ['GITHUB_USER'] = 'demo_user'
os.environ['GITHUB_REPO'] = 'demo_repo'

try:
    from app import app
    
    print("🚀 Starting PipeGuard Dashboard...")
    print("📊 Features: Real-time monitoring, AI analytics, performance insights")
    print("🔗 Dashboard URL: http://localhost:8080")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    )
    
except KeyboardInterrupt:
    print("\n👋 Dashboard stopped by user")
except Exception as e:
    print(f"❌ Error starting dashboard: {e}")
    print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
