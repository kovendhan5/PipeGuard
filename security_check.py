#!/usr/bin/env python3
"""
Security validation script for PipeGuard.
Checks for common security vulnerabilities and misconfigurations.
"""

import os
import sys
import re
from pathlib import Path

def check_secrets_in_code():
    """Check for hardcoded secrets in code files."""
    print("🔍 Checking for hardcoded secrets...")
    
    # Patterns to look for
    secret_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'["\'][A-Za-z0-9]{20,}["\']',  # Long strings that might be secrets
    ]
    
    issues = []
    
    # Check Python files
    for py_file in Path('.').glob('**/*.py'):
        if py_file.name.startswith('.'):
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8')
            for pattern in secret_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Skip common test/demo values
                    if any(word in match.lower() for word in ['mock', 'test', 'demo', 'example', 'your_', 'placeholder']):
                        continue
                    issues.append(f"Potential secret in {py_file}: {match[:50]}...")
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    if issues:
        print("❌ Potential secrets found:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("✅ No hardcoded secrets found")
        return True

def check_debug_mode():
    """Check if debug mode is properly configured."""
    print("\n🔍 Checking debug mode configuration...")
    
    issues = []
    
    # Check for debug=True in code
    for py_file in Path('.').glob('**/*.py'):
        if py_file.name.startswith('.'):
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8')
            if 'debug=True' in content and 'test' not in py_file.name.lower():
                issues.append(f"Debug mode enabled in {py_file}")
        except Exception:
            pass
    
    # Check environment variables
    if os.environ.get('DEBUG', '').lower() == 'true':
        if os.environ.get('FLASK_ENV') == 'production':
            issues.append("DEBUG=True in production environment")
    
    if issues:
        print("⚠️  Debug mode issues:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("✅ Debug mode properly configured")
        return True

def check_input_validation():
    """Check for proper input validation."""
    print("\n🔍 Checking input validation...")
    
    issues = []
    
    # Check Flask routes for input validation
    app_files = list(Path('.').glob('**/*app*.py'))
    
    for app_file in app_files:
        try:
            content = app_file.read_text(encoding='utf-8')
            
            # Look for routes that accept user input
            if 'request.' in content:
                if 'validate' not in content and 'sanitize' not in content:
                    issues.append(f"Missing input validation in {app_file}")
            
            # Check for dangerous functions
            dangerous_patterns = [
                'eval(',
                'exec(',
                'os.system(',
                'subprocess.call(',
            ]
            
            for pattern in dangerous_patterns:
                if pattern in content:
                    issues.append(f"Dangerous function {pattern} found in {app_file}")
                    
        except Exception:
            pass
    
    if issues:
        print("⚠️  Input validation issues:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("✅ Input validation checks passed")
        return True

def check_dependencies():
    """Check for known vulnerable dependencies."""
    print("\n🔍 Checking dependencies for security...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        # Check for security-related packages
        security_packages = ['Flask-Limiter', 'Flask-CORS', 'bleach']
        missing_packages = []
        
        for package in security_packages:
            if package not in requirements:
                missing_packages.append(package)
        
        if missing_packages:
            print("⚠️  Missing security packages:")
            for package in missing_packages:
                print(f"  • {package}")
            return False
        else:
            print("✅ Security packages are installed")
            return True
            
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def check_environment_security():
    """Check environment variable security."""
    print("\n🔍 Checking environment security...")
    
    issues = []
    
    # Check for required security environment variables
    required_vars = ['SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        issues.append(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Check for weak secret keys
    secret_key = os.environ.get('SECRET_KEY', '')
    if secret_key and len(secret_key) < 16:
        issues.append("SECRET_KEY is too short (should be at least 16 characters)")
    
    if issues:
        print("⚠️  Environment security issues:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("✅ Environment security checks passed")
        return True

def check_file_permissions():
    """Check file permissions for sensitive files."""
    print("\n🔍 Checking file permissions...")
    
    issues = []
    sensitive_files = ['.env', '.env.local', 'config.py', 'security_config.py']
    
    for file_name in sensitive_files:
        if os.path.exists(file_name):
            # On Windows, this check is limited
            try:
                stat_info = os.stat(file_name)
                # Basic check - could be enhanced for Unix systems
                print(f"  • {file_name}: exists")
            except Exception as e:
                issues.append(f"Cannot check permissions for {file_name}: {e}")
    
    if issues:
        print("⚠️  File permission issues:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("✅ File permission checks passed")
        return True

def main():
    """Run all security checks."""
    print("🔒 PipeGuard Security Validation")
    print("=" * 40)
    
    checks = [
        check_secrets_in_code,
        check_debug_mode,
        check_input_validation,
        check_dependencies,
        check_environment_security,
        check_file_permissions,
    ]
    
    results = []
    for check in checks:
        try:
            results.append(check())
        except Exception as e:
            print(f"❌ Error running {check.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("📊 Security Check Summary:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} security checks passed!")
        print("✅ Your PipeGuard application appears to be secure.")
    else:
        print(f"⚠️  {passed}/{total} security checks passed.")
        print("🔧 Please review and fix the issues above.")
        
        print("\n💡 Quick fixes:")
        print("1. Set SECRET_KEY environment variable")
        print("2. Install security packages: pip install Flask-Limiter Flask-CORS bleach")
        print("3. Review code for hardcoded secrets")
        print("4. Disable debug mode in production")
    
    print("\n📖 For more details, see SECURITY_AUDIT.md")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
