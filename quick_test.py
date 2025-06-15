#!/usr/bin/env python3
"""
Quick test to see if the Flask app can start and respond.
"""

import os
import sys

# Set up mock environment
os.environ['GITHUB_TOKEN'] = 'mock_token'
os.environ['GITHUB_USER'] = 'test_user'
os.environ['GITHUB_REPO'] = 'test_repo'

try:
    from app import app
    
    print("Testing Flask app...")
    with app.test_client() as client:
        response = client.get("/")
        print(f"Status Code: {response.status_code}")
        print(f"Response contains 'PipeGuard': {'PipeGuard' in response.get_data(as_text=True)}")
        
        if response.status_code == 200:
            print("✅ Flask app is working correctly!")
            print("\nTo run the app locally:")
            print("python run_local.py")
            print("Then visit: http://localhost:8080")
        else:
            print("❌ Flask app returned an error")
            
except Exception as e:
    print(f"Error: {e}")
    print("❌ Flask app failed to start")
