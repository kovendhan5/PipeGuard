#!/usr/bin/env python3
"""
Secure setup script for PipeGuard.
Generates secure environment variables and validates configuration.
"""

import os
import secrets
import sys

def generate_secure_env():
    """Generate a secure .env file with proper settings."""
    print("🔐 Generating secure environment configuration...")
    
    # Generate secure secret key
    secret_key = secrets.token_urlsafe(32)
    
    env_content = f"""# PipeGuard Secure Configuration
# Generated on {os.popen('date').read().strip()}

# ======================
# Security Configuration
# ======================
SECRET_KEY={secret_key}
DEBUG=False
FLASK_ENV=production

# ======================
# GitHub Configuration
# ======================
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_USER=your_github_username
GITHUB_REPO=your_repository_name

# ======================
# Google Cloud Configuration
# ======================
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
GOOGLE_CLOUD_PROJECT=your-gcp-project-id

# ======================
# Email Notifications (Optional)
# ======================
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_or_token
FROM_EMAIL=pipeguard-alerts@yourcompany.com

# ======================
# Advanced Monitoring
# ======================
DURATION_WARNING_THRESHOLD=120
DURATION_CRITICAL_THRESHOLD=300
FAILURE_RATE_WARNING=0.1
FAILURE_RATE_CRITICAL=0.2
AUTO_REFRESH_INTERVAL=30

# ======================
# Application Settings
# ======================
FLASK_HOST=0.0.0.0
FLASK_PORT=8080
MAX_RUNS_DISPLAY=20
MAX_ANOMALIES_DISPLAY=10
API_RATE_LIMIT=100
LOG_LEVEL=INFO
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Secure .env file generated")
    print(f"🔑 Generated SECRET_KEY: {secret_key[:16]}...")
    print("⚠️  Please update GitHub credentials and other settings in .env file")
    
    return secret_key

def setup_development_env():
    """Set up environment for secure development."""
    print("🛠️  Setting up secure development environment...")
    
    # Set secure environment variables for this session
    secret_key = secrets.token_urlsafe(32)
    os.environ['SECRET_KEY'] = secret_key
    os.environ['DEBUG'] = 'False'  # Secure by default
    os.environ['FLASK_ENV'] = 'development'
    
    # Set safe demo values
    os.environ.setdefault('GITHUB_TOKEN', 'demo_token_for_local_dev')
    os.environ.setdefault('GITHUB_USER', 'demo_user')
    os.environ.setdefault('GITHUB_REPO', 'demo_repo')
    
    print("✅ Development environment configured securely")
    return secret_key

def validate_security():
    """Validate current security configuration."""
    print("🔍 Validating security configuration...")
    
    issues = []
    
    # Check SECRET_KEY
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        issues.append("SECRET_KEY not set")
    elif len(secret_key) < 16:
        issues.append("SECRET_KEY too short (should be 32+ characters)")
    
    # Check DEBUG mode
    debug_mode = os.environ.get('DEBUG', '').lower()
    if debug_mode == 'true':
        env = os.environ.get('FLASK_ENV', '')
        if env == 'production':
            issues.append("DEBUG=True in production environment")
    
    # Check for demo/test tokens in production
    github_token = os.environ.get('GITHUB_TOKEN', '')
    if 'demo' in github_token.lower() or 'test' in github_token.lower():
        env = os.environ.get('FLASK_ENV', '')
        if env == 'production':
            issues.append("Demo/test tokens used in production")
    
    if issues:
        print("⚠️  Security validation issues:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("✅ Security validation passed")
        return True

def main():
    """Main setup function."""
    print("🔒 PipeGuard Secure Setup")
    print("=" * 30)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--generate-env':
        # Generate .env file
        generate_secure_env()
    else:
        # Set up development environment
        setup_development_env()
    
    # Validate security
    validate_security()
    
    print("\n🎯 Security Setup Complete!")
    print("\nNext steps:")
    print("1. Review and update .env file with your actual credentials")
    print("2. Run: python security_check.py")
    print("3. Run: python run_local.py")

if __name__ == "__main__":
    main()
