#!/usr/bin/env python3
"""Quick Security Check for PipeGuard"""

import os
from dotenv import load_dotenv

def main():
    print('🔒 PipeGuard Security Status')
    print('=' * 40)
    
    # Load environment
    load_dotenv()
    
    issues = []
    passed = []
    
    # 1. Secret key check
    secret = os.getenv('SECRET_KEY')
    if not secret:
        issues.append('❌ Missing SECRET_KEY')
    elif len(secret) < 32:
        issues.append('⚠️ SECRET_KEY too short (minimum 32 chars)')
    else:
        passed.append('✅ SECRET_KEY: Secure (32+ characters)')
    
    # 2. Debug mode check
    debug = os.getenv('DEBUG', 'False').lower()
    if debug == 'true':
        issues.append('⚠️ DEBUG=True (should be False for production)')
    else:
        passed.append('✅ DEBUG: Disabled for production')
    
    # 3. GitHub token check
    github_token = os.getenv('GITHUB_TOKEN', '')
    if 'your_' in github_token.lower():
        issues.append('⚠️ GitHub token has placeholder value')
    elif not github_token:
        issues.append('⚠️ Missing GITHUB_TOKEN')
    else:
        passed.append('✅ GITHUB_TOKEN: Configured')
    
    # 4. GCP credentials check
    gcp_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    if 'your_' in gcp_creds.lower() or not gcp_creds:
        issues.append('⚠️ GCP credentials not configured')
    else:
        if os.path.exists(gcp_creds):
            passed.append('✅ GCP_CREDENTIALS: File exists')
        else:
            issues.append('❌ GCP credentials file not found')
    
    # 5. Check Flask dependencies
    try:
        import flask_limiter
        import flask_cors
        import bleach
        passed.append('✅ Security packages: All installed')
    except ImportError as e:
        issues.append(f'❌ Missing security package: {e}')
    
    # Display results
    print('\n📊 Security Assessment:')
    for item in passed:
        print(f'  {item}')
    
    if issues:
        print('\n🚨 Issues Found:')
        for item in issues:
            print(f'  {item}')
        
        print('\n🔧 Next Steps:')
        if any('placeholder' in issue for issue in issues):
            print('  1. Update .env with real GitHub credentials')
        if any('GCP' in issue for issue in issues):
            print('  2. Set up Google Cloud credentials')
        if any('SECRET_KEY' in issue for issue in issues):
            print('  3. Generate a secure secret key')
            
        print('\n📖 See REAL_ENVIRONMENT_SETUP.md for detailed instructions')
        
        return len(issues)
    else:
        print('\n🎉 All security checks passed!')
        print('✅ PipeGuard is secure and ready!')
        return 0

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
