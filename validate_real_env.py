#!/usr/bin/env python3
"""
Real Environment Validator for PipeGuard
Tests all real service connections and configurations.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from google.cloud import firestore
from google.oauth2 import service_account

def print_status(message, status="info"):
    """Print colored status messages."""
    colors = {
        "success": "\033[92m✅",
        "error": "\033[91m❌", 
        "warning": "\033[93m⚠️",
        "info": "\033[94mℹ️"
    }
    reset = "\033[0m"
    print(f"{colors.get(status, '')} {message}{reset}")

def validate_environment_file():
    """Check if .env file exists and has required variables."""
    print_status("Checking environment configuration...", "info")
    
    if not os.path.exists('.env'):
        print_status("Missing .env file. Run 'python secure_setup.py' first.", "error")
        return False
    
    load_dotenv()
    
    required_vars = [
        'GITHUB_TOKEN', 'GITHUB_USER', 'GITHUB_REPO',
        'GOOGLE_APPLICATION_CREDENTIALS', 'GOOGLE_CLOUD_PROJECT',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or 'your_' in value.lower() or 'replace_this' in value.lower():
            missing_vars.append(var)
    
    if missing_vars:
        print_status(f"Missing or placeholder values: {', '.join(missing_vars)}", "error")
        print_status("Please update your .env file with real values.", "warning")
        return False
    
    print_status("Environment file validation passed", "success")
    return True

def validate_github_connection():
    """Test GitHub API connection."""
    print_status("Testing GitHub API connection...", "info")
    
    token = os.getenv('GITHUB_TOKEN')
    user = os.getenv('GITHUB_USER')
    repo = os.getenv('GITHUB_REPO')
    
    # Test basic API access
    url = f'https://api.github.com/repos/{user}/{repo}'
    headers = {'Authorization': f'token {token}'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            repo_data = response.json()
            print_status(f"Connected to repository: {repo_data['full_name']}", "success")
            
            # Test Actions API
            actions_url = f'{url}/actions/runs'
            actions_response = requests.get(actions_url, headers=headers, timeout=10)
            
            if actions_response.status_code == 200:
                runs_data = actions_response.json()
                run_count = len(runs_data.get('workflow_runs', []))
                print_status(f"Found {run_count} workflow runs", "success")
                return True
            else:
                print_status(f"Actions API error: {actions_response.status_code}", "error")
                return False
                
        elif response.status_code == 404:
            print_status("Repository not found. Check GITHUB_USER and GITHUB_REPO.", "error")
            return False
        elif response.status_code == 401:
            print_status("Invalid GitHub token. Check GITHUB_TOKEN.", "error")
            return False
        else:
            print_status(f"GitHub API error: {response.status_code}", "error")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status(f"GitHub connection failed: {e}", "error")
        return False

def validate_google_cloud_connection():
    """Test Google Cloud Firestore connection."""
    print_status("Testing Google Cloud connection...", "info")
    
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    
    # Check credentials file exists
    if not os.path.exists(credentials_path):
        print_status(f"Credentials file not found: {credentials_path}", "error")
        return False
    
    # Validate credentials file format
    try:
        with open(credentials_path, 'r') as f:
            creds_data = json.load(f)
            if 'project_id' not in creds_data:
                print_status("Invalid service account key format", "error")
                return False
    except json.JSONDecodeError:
        print_status("Invalid JSON in credentials file", "error")
        return False
    
    # Test Firestore connection
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        db = firestore.Client(project=project_id)
        
        # Try to list collections (this tests authentication)
        collections = list(db.collections())
        print_status(f"Firestore connected. Found {len(collections)} collections", "success")
        
        # Test write access by creating a test document
        test_ref = db.collection('_test').document('connection_test')
        test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP, 'test': True})
        
        # Clean up test document
        test_ref.delete()
        print_status("Firestore write/delete permissions verified", "success")
        return True
        
    except Exception as e:
        print_status(f"Google Cloud connection failed: {e}", "error")
        return False

def validate_application_setup():
    """Test application dependencies and configuration."""
    print_status("Validating application setup...", "info")
    
    # Test imports
    try:
        import flask
        import google.cloud.firestore
        import requests
        print_status("All required packages installed", "success")
    except ImportError as e:
        print_status(f"Missing package: {e}", "error")
        return False
      # Test Flask app can start
    try:
        import app
        print_status("Flask application configuration valid", "success")
        return True
    except Exception as e:
        print_status(f"Flask app configuration error: {e}", "error")
        return False

def main():
    """Run all validation tests."""
    print("🔍 PipeGuard Real Environment Validator")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    tests = [
        ("Environment Configuration", validate_environment_file),
        ("GitHub API Connection", validate_github_connection),
        ("Google Cloud Connection", validate_google_cloud_connection),
        ("Application Setup", validate_application_setup)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_status(f"Test failed with exception: {e}", "error")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print_status("🎉 All tests passed! Your real environment is ready.", "success")
        print_status("Run 'python run_local.py' to start with real data.", "info")
        return True
    else:
        print_status("❌ Some tests failed. Check the setup guide.", "error")
        print_status("See REAL_ENVIRONMENT_SETUP.md for detailed instructions.", "info")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
