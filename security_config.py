"""
Security configuration for PipeGuard.
This module contains security settings and validation functions.
"""

import os
import secrets
import hashlib
from datetime import timedelta

class SecurityConfig:
    """Security configuration class."""
    
    # Session Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "100 per hour"
    
    # CORS Settings
    CORS_ORIGINS = [
        "http://localhost:8080",
        "https://pipeguard.uc.r.appspot.com"
    ]
    
    # Content Security Policy
    CSP_POLICY = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net",
        'style-src': "'self' 'unsafe-inline' https://cdnjs.cloudflare.com",
        'font-src': "'self' https://cdnjs.cloudflare.com",
        'img-src': "'self' data:",
        'connect-src': "'self'",
    }
    
    # Input Validation
    MAX_INPUT_LENGTH = 1000
    ALLOWED_TAGS = []  # No HTML tags allowed
    
    # API Security
    API_RATE_LIMITS = {
        'dashboard': "30 per minute",
        'api_stats': "60 per minute", 
        'api_refresh': "30 per minute",
        'api_analysis': "20 per minute",
        'api_health': "20 per minute",
        'api_insights': "10 per minute",
        'api_notifications': "5 per minute"
    }

def generate_secure_secret():
    """Generate a cryptographically secure secret key."""
    return secrets.token_urlsafe(32)

def hash_sensitive_data(data):
    """Hash sensitive data for logging."""
    return hashlib.sha256(data.encode()).hexdigest()[:8]

def validate_environment():
    """Validate security-related environment variables."""
    issues = []
    
    # Check for required security settings
    if not os.environ.get('SECRET_KEY'):
        issues.append("SECRET_KEY not set - sessions will not be secure")
    
    # Check for debug mode in production
    if os.environ.get('FLASK_ENV') == 'production' and os.environ.get('DEBUG', '').lower() == 'true':
        issues.append("DEBUG mode enabled in production - security risk")
    
    # Check for HTTPS configuration
    if os.environ.get('FLASK_ENV') == 'production' and not os.environ.get('HTTPS_REDIRECT'):
        issues.append("HTTPS not enforced in production")
    
    return issues

def get_security_headers():
    """Get recommended security headers."""
    return {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    }
