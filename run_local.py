#!/usr/bin/env python3
"""
Local development runner for PipeGuard.
This script sets up the environment for local testing without requiring Google Cloud credentials.
"""

import os
import sys
from unittest.mock import patch, MagicMock

def setup_mock_environment():
    """Set up mock environment variables for local development."""
    os.environ.setdefault('GITHUB_TOKEN', 'mock_token_for_local_dev')
    os.environ.setdefault('GITHUB_USER', 'test_user')
    os.environ.setdefault('GITHUB_REPO', 'test_repo')
    
def run_local_server():
    """Run the Flask app locally with mocked dependencies."""
    print("Starting PipeGuard in local development mode...")
    print("Note: This will use mock data since no real Google Cloud credentials are configured.")
    
    setup_mock_environment()
    
    # Import after setting up environment
    from app import app
    
    print("Starting Flask development server on http://localhost:8080")
    print("Press Ctrl+C to stop the server")
    
    app.run(host="0.0.0.0", port=8080, debug=True)

if __name__ == "__main__":
    run_local_server()
