#!/usr/bin/env python3
"""
Quick Security Verification for PipeGuard
Checks core security features before real environment setup.
"""

import os
import sys
from dotenv import load_dotenv

def main():
    print('🔐 PipeGuard Security Verification')
    print('=' * 40)
    
    # Load environment
    load_dotenv()
    
    issues = []
    passed = []
    
    # Check secret key
    secret = os.getenv('SECRET_KEY')
    if secret and len(secret) >= 32:
        passed.append('✅ Secret key: Strong ({} chars)'.format(len(secret)))
    else:
        issues.append('⚠️  Secret key: Weak or missing')
    
    # Check security packages
    try:
        import flask_limiter, flask_cors, bleach
        passed.append('✅ Security packages: All installed')
    except ImportError as e:
        issues.append(f'❌ Missing security package: {e}')
    
    # Import and check app configuration
    try:
        import app
        
        # Check HTTPS settings
        if app.app.config.get('SESSION_COOKIE_SECURE'):
            passed.append('✅ Session security: HTTPS enforced')
        else:
            issues.append('⚠️  Session security: HTTPS not enforced')
        
        # Check debug mode
        if not app.app.debug:
            passed.append('✅ Debug mode: Disabled (production safe)')
        else:
            issues.append('⚠️  Debug mode: Enabled (disable for production)')
            
        # Check rate limiting
        if hasattr(app, 'limiter'):
            passed.append('✅ Rate limiting: Configured')
        else:
            issues.append('⚠️  Rate limiting: Not configured')
              # Check input validation
        if hasattr(app, 'validate_and_sanitize_input'):
            passed.append('✅ Input validation: Implemented')
        else:
            issues.append('⚠️  Input validation: Not found')
            
    except Exception as e:
        issues.append(f'❌ App configuration error: {e}')
    
    # Check .env security
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
            if 'your_' in env_content.lower() or 'placeholder' in env_content.lower():
                issues.append('⚠️  .env file contains placeholder values')
            else:
                passed.append('✅ .env file: Real values configured')
    else:
        issues.append('❌ .env file: Missing')
    
    # Check .gitignore security
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            gitignore = f.read()
            if '.env' in gitignore and 'credentials/' in gitignore:
                passed.append('✅ .gitignore: Secrets properly excluded')
            else:
                issues.append('⚠️  .gitignore: May expose secrets')
    
    # Print results
    print('\\n📋 Security Check Results:')
    for item in passed:
        print(f'  {item}')
    
    if issues:
        print('\\n🚨 Security Issues Found:')
        for item in issues:
            print(f'  {item}')
    
    print('\\n' + '=' * 40)
    if len(issues) == 0:
        print('🎉 Security Status: EXCELLENT - Ready for real environment!')
        return True
    elif len(issues) <= 2:
        print('✅ Security Status: GOOD - Minor issues to address')
        return True
    else:
        print('❌ Security Status: NEEDS IMPROVEMENT - Address issues before production')
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
