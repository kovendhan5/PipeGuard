#!/usr/bin/env python3
"""
Comprehensive Security Audit for PipeGuard
Validates all security configurations and best practices.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from dotenv import load_dotenv

def print_status(message, status="info"):
    """Print colored status messages."""
    colors = {
        "success": "\033[92m✅",
        "error": "\033[91m❌", 
        "warning": "\033[93m⚠️",
        "info": "\033[94mℹ️",
        "critical": "\033[95m🚨"
    }
    reset = "\033[0m"
    print(f"{colors.get(status, '')} {message}{reset}")

def check_environment_security():
    """Check environment configuration security."""
    print_status("Checking environment security...", "info")
    issues = []
    
    # Load environment variables
    load_dotenv()
    
    # Check critical environment variables
    critical_vars = {
        'SECRET_KEY': 'Flask secret key for session security',
        'GITHUB_TOKEN': 'GitHub API authentication',
        'GOOGLE_APPLICATION_CREDENTIALS': 'GCP service account credentials'
    }
    
    for var, purpose in critical_vars.items():
        value = os.getenv(var)
        if not value:
            issues.append(f"Missing {var} ({purpose})")
        elif 'your_' in value.lower() or 'replace' in value.lower():
            issues.append(f"{var} has placeholder value")
        elif var == 'SECRET_KEY' and len(value) < 32:
            issues.append(f"{var} is too short (minimum 32 characters)")
    
    # Check debug mode
    debug_mode = os.getenv('DEBUG', 'False').lower()
    if debug_mode == 'true':
        issues.append("DEBUG mode is enabled (should be False for production)")
    
    return issues

def check_file_security():
    """Check file permissions and security."""
    print_status("Checking file security...", "info")
    issues = []
    
    # Check .env file exists and is properly protected
    env_file = Path('.env')
    if not env_file.exists():
        issues.append(".env file missing")
    
    # Check .gitignore protects sensitive files
    gitignore = Path('.gitignore')
    if gitignore.exists():
        gitignore_content = gitignore.read_text()
        required_ignores = ['.env', 'credentials/', '*.json']
        for ignore_pattern in required_ignores:
            if ignore_pattern not in gitignore_content:
                issues.append(f"Missing {ignore_pattern} in .gitignore")
    else:
        issues.append(".gitignore file missing")
    
    # Check credentials directory
    creds_dir = Path('credentials')
    if creds_dir.exists():
        creds_files = list(creds_dir.glob('*'))
        if creds_files:
            print_status(f"Found {len(creds_files)} credential files", "warning")
    
    return issues

def check_code_security():
    """Check code for security issues."""
    print_status("Checking code security...", "info")
    issues = []
    
    # Check for hardcoded secrets
    dangerous_patterns = [
        'password =', 'token =', 'secret =', 'key =',
        'sk_', 'ghp_', 'gcp_', 'aws_'
    ]
    
    python_files = list(Path('.').glob('*.py'))
    for py_file in python_files:
        if py_file.name.startswith('test_'):
            continue
            
        content = py_file.read_text()
        for pattern in dangerous_patterns:
            if pattern in content.lower():
                # Check if it's actually hardcoded (not from environment)
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if pattern in line.lower() and 'os.environ' not in line and 'getenv' not in line:
                        if not line.strip().startswith('#'):
                            issues.append(f"Potential hardcoded secret in {py_file.name}:{i+1}")
    
    # Check for debug=True in production code
    for py_file in python_files:
        if py_file.name.startswith('test_'):
            continue
            
        content = py_file.read_text()
        if 'debug=True' in content and 'os.environ' not in content:
            issues.append(f"Hardcoded debug=True in {py_file.name}")
    
    return issues

def check_dependencies():
    """Check for security-related dependencies."""
    print_status("Checking security dependencies...", "info")
    issues = []
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        security_packages = [
            'Flask-Limiter',  # Rate limiting
            'Flask-CORS',     # CORS protection
            'bleach',         # HTML sanitization
            'python-dotenv'   # Environment variables
        ]
        
        for package in security_packages:
            if package not in requirements:
                issues.append(f"Missing security package: {package}")
    
    except FileNotFoundError:
        issues.append("requirements.txt not found")
    
    return issues

def check_flask_security():
    """Check Flask application security configuration."""
    print_status("Checking Flask security configuration...", "info")
    issues = []
    
    try:
        # Import app to check configuration
        import app
        flask_app = app.app
        
        # Check security headers
        with flask_app.test_client() as client:
            response = client.get('/')
            headers = response.headers
            
            required_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block'
            }
            
            for header, expected in required_headers.items():
                if header not in headers:
                    issues.append(f"Missing security header: {header}")
        
        # Check session configuration
        session_config = {
            'SESSION_COOKIE_SECURE': 'Session cookies not secure',
            'SESSION_COOKIE_HTTPONLY': 'Session cookies accessible via JavaScript',
            'SESSION_COOKIE_SAMESITE': 'Missing CSRF protection'
        }
        
        for config, warning in session_config.items():
            if not flask_app.config.get(config):
                issues.append(warning)
                
    except Exception as e:
        issues.append(f"Could not check Flask configuration: {e}")
    
    return issues

def check_network_security():
    """Check network and API security."""
    print_status("Checking network security...", "info")
    issues = []
    
    try:
        import app
        flask_app = app.app
        
        # Test rate limiting
        with flask_app.test_client() as client:
            # Make multiple requests to test rate limiting
            responses = []
            for _ in range(35):  # Should exceed rate limit
                responses.append(client.get('/'))
            
            # Check if rate limiting kicked in
            status_codes = [r.status_code for r in responses[-5:]]
            if 429 not in status_codes:  # 429 = Too Many Requests
                issues.append("Rate limiting may not be working properly")
                
    except Exception as e:
        issues.append(f"Could not test rate limiting: {e}")
    
    return issues

def generate_security_report(all_issues):
    """Generate a comprehensive security report."""
    print_status("Generating security report...", "info")
    
    report = f"""# 🔒 PipeGuard Security Audit Report
Generated: {os.popen('date').read().strip()}

## 📊 Security Assessment Summary

**Overall Status**: {"🚨 CRITICAL ISSUES FOUND" if any(all_issues.values()) else "✅ SECURE"}

"""
    
    categories = {
        'Environment Security': all_issues.get('environment', []),
        'File Security': all_issues.get('files', []),
        'Code Security': all_issues.get('code', []),
        'Dependencies': all_issues.get('dependencies', []),
        'Flask Security': all_issues.get('flask', []),
        'Network Security': all_issues.get('network', [])
    }
    
    for category, issues in categories.items():
        status = "✅ SECURE" if not issues else f"⚠️ {len(issues)} ISSUES"
        report += f"- **{category}**: {status}\n"
    
    report += "\n## 🔍 Detailed Findings\n\n"
    
    for category, issues in categories.items():
        report += f"### {category}\n\n"
        if not issues:
            report += "✅ No issues found\n\n"
        else:
            for issue in issues:
                report += f"- ❌ {issue}\n"
            report += "\n"
    
    report += """## 🛠️ Remediation Steps

### High Priority (Fix Immediately)
1. Set all required environment variables with real values
2. Ensure DEBUG=False in production
3. Verify all sensitive files are in .gitignore
4. Install missing security packages

### Medium Priority (Fix Before Deployment)
1. Review and fix any hardcoded secrets
2. Validate all security headers are present
3. Test rate limiting functionality
4. Verify session security configuration

### Best Practices
1. Rotate secrets regularly
2. Use least-privilege access for service accounts
3. Monitor security logs
4. Keep dependencies updated

## 📋 Security Checklist

- [ ] All environment variables configured
- [ ] Debug mode disabled for production
- [ ] Sensitive files protected by .gitignore
- [ ] Security packages installed
- [ ] No hardcoded secrets in code
- [ ] Security headers configured
- [ ] Rate limiting active
- [ ] Session security enabled

---
**Security Audit Complete** 🔒
"""
    
    try:
        with open('SECURITY_AUDIT_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report)
        print_status("Security report saved: SECURITY_AUDIT_REPORT.md", "success")
    except Exception as e:
        print_status(f"Could not save report: {e}", "error")

def main():
    """Run comprehensive security audit."""
    print("🔒 PipeGuard Comprehensive Security Audit")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    all_issues = {}
    
    # Run all security checks
    checks = [
        ('environment', check_environment_security),
        ('files', check_file_security),
        ('code', check_code_security),
        ('dependencies', check_dependencies),
        ('flask', check_flask_security),
        ('network', check_network_security)
    ]
    
    total_issues = 0
    
    for check_name, check_func in checks:
        try:
            issues = check_func()
            all_issues[check_name] = issues
            total_issues += len(issues)
            
            if issues:
                print_status(f"{check_name.title()}: {len(issues)} issues found", "warning")
                for issue in issues[:3]:  # Show first 3 issues
                    print(f"  • {issue}")
                if len(issues) > 3:
                    print(f"  • ... and {len(issues) - 3} more")
            else:
                print_status(f"{check_name.title()}: Secure", "success")
                
        except Exception as e:
            print_status(f"{check_name.title()}: Check failed - {e}", "error")
            all_issues[check_name] = [f"Check failed: {e}"]
            total_issues += 1
    
    # Generate report
    generate_security_report(all_issues)
    
    print("\n" + "=" * 50)
    print(f"📊 Security Audit Complete")
    print(f"🔍 Total Issues Found: {total_issues}")
    
    if total_issues == 0:
        print_status("🎉 PipeGuard is SECURE and ready for production!", "success")
        return True
    elif total_issues <= 5:
        print_status("⚠️ Minor security issues found. Review and fix before deployment.", "warning")
        return False
    else:
        print_status("🚨 CRITICAL security issues found. Fix immediately!", "critical")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
