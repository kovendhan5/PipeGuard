#!/usr/bin/env python3
"""
Simple verification script to check if PipeGuard components work.
"""

import sys
import os

def check_imports():
    """Check if all required modules can be imported."""
    print("Checking imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import pytest
        print("✅ Pytest imported successfully")
    except ImportError as e:
        print(f"❌ Pytest import failed: {e}")
        return False
    
    try:
        from google.cloud import firestore
        print("✅ Google Cloud Firestore imported successfully")
    except ImportError as e:
        print(f"❌ Google Cloud Firestore import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ Python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ Python-dotenv import failed: {e}")
        return False
        
    return True

def check_app():
    """Check if the Flask app can be created."""
    print("\nChecking Flask app...")
    
    try:
        # Set up mock environment to avoid connection issues
        os.environ.setdefault('GITHUB_TOKEN', 'mock_token')
        os.environ.setdefault('GITHUB_USER', 'test_user')
        os.environ.setdefault('GITHUB_REPO', 'test_repo')
        
        from app import app
        
        with app.test_client() as client:
            response = client.get("/")
            if response.status_code == 200:
                print("✅ Flask app responds successfully")
                print(f"   Response contains PipeGuard: {'PipeGuard' in response.get_data(as_text=True)}")
                return True
            else:
                print(f"❌ Flask app returned status code: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def main():
    """Run all checks."""
    print("=" * 50)
    print("       PipeGuard Verification Script")
    print("=" * 50)
    
    imports_ok = check_imports()
    app_ok = check_app()
    
    print("\n" + "=" * 50)
    if imports_ok and app_ok:
        print("🎉 All checks passed! PipeGuard is ready to run.")
        print("\nNext steps:")
        print("1. Run: python run_local.py")
        print("2. Visit: http://localhost:8080")
    else:
        print("❌ Some checks failed. Please install missing dependencies.")
        print("\nTry running: pip install -r requirements.txt")
    print("=" * 50)

if __name__ == "__main__":
    main()
