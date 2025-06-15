#!/usr/bin/env python3
"""
Test script for the monitor_pipeline function.
This allows testing the GitHub API integration without deploying to Cloud Functions.
"""

import os
from unittest.mock import MagicMock

def test_monitor_pipeline():
    """Test the monitor_pipeline function with real or mock data."""
    print("Testing monitor_pipeline function...")
    
    # Set up environment variables (use real ones if available)
    if not os.environ.get('GITHUB_TOKEN'):
        print("Warning: No GITHUB_TOKEN found. Using mock token.")
        os.environ['GITHUB_TOKEN'] = 'mock_token'
    
    os.environ.setdefault('GITHUB_USER', 'kovendhan5')
    os.environ.setdefault('GITHUB_REPO', 'PipeGuard')
    
    # Create a mock request object
    mock_request = MagicMock()
    mock_request.method = 'GET'
    
    # Import and test the function
    from monitor_pipeline import monitor_pipeline
    
    try:
        result = monitor_pipeline(mock_request)
        print(f"Monitor pipeline result: {result}")
        return True
    except Exception as e:
        print(f"Error testing monitor_pipeline: {e}")
        return False

if __name__ == "__main__":
    success = test_monitor_pipeline()
    if success:
        print("✅ Monitor pipeline test completed successfully!")
    else:
        print("❌ Monitor pipeline test failed!")
        exit(1)
