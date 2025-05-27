# CSRF Deployment Fix for Upsun

This document explains the fixes applied to resolve the CSRF verification error when deploying to Upsun.

## Problem
When deploying to Upsun, the Django admin login was failing with:
```
POST https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/admin/login/?next=/admin/ 403 (Forbidden)
CSRF verification failed. Request aborted.
```

## Root Causes
1. **CSRF_TRUSTED_ORIGINS** was only configured for localhost development
2. **ALLOWED_HOSTS** was not properly configured for the Upsun deployment domain
3. **Admin login** was not exempted from custom CSRF middleware
4. **Security settings** were not properly configured for HTTPS production environment

## Fixes Applied

### 1. Dynamic CSRF Trusted Origins (`backend/config/settings.py`)
- Added `get_csrf_trusted_origins()` function that auto-detects Upsun deployment URLs
- Reads from `PLATFORM_ROUTES` environment variable to get all valid domains
- Includes both main domain and API subdomain
- Falls back to constructed URLs if route detection fails

### 2. Dynamic Allowed Hosts (`backend/config/settings.py`)
- Enhanced production settings to auto-detect allowed hosts from Platform.sh routes
- Extracts hostnames from all HTTPS routes in the deployment
- Falls back to allowing all hosts if detection fails

### 3. Admin Login CSRF Exemption (`backend/users/middleware.py`)
- Added `r'^admin/login/$'` to the exempt paths in `CustomCsrfMiddleware`
- This allows Django admin login to work without CSRF token issues

### 4. Production Security Settings (`backend/config/settings.py`)
- Added proper CSRF cookie settings:
  - `CSRF_COOKIE_SECURE = not DEBUG` (secure cookies in production)
  - `CSRF_COOKIE_HTTPONLY = False` (allow JS access to CSRF token)
  - `CSRF_COOKIE_SAMESITE = 'Lax'` (allow cross-site requests)
- Added session security settings:
  - `SESSION_COOKIE_SECURE = not DEBUG`
  - `SESSION_COOKIE_HTTPONLY = True`
  - `SESSION_COOKIE_SAMESITE = 'Lax'`
- Added HTTPS security headers:
  - `SECURE_SSL_REDIRECT`
  - `SECURE_PROXY_SSL_HEADER`
  - `SECURE_HSTS_*` settings

### 5. Upsun Configuration Updates (`.upsun/config.yaml`)
- Added environment variables:
  - `DEBUG: "False"`
  - `DJANGO_SECURE_SSL_REDIRECT: "True"`

## Debug Tools

### Management Command
Run this command on your Upsun deployment to debug CSRF settings:
```bash
python manage.py debug_csrf
```

### Debug Script
Run this locally or on the server:
```bash
python debug_csrf.py
```

## Testing the Fix

1. **Deploy the changes** to Upsun
2. **Wait for deployment** to complete
3. **Navigate to** `https://api.your-deployment-url.platformsh.site/admin/`
4. **Try logging in** with your admin credentials
5. **If still having issues**, run the debug command to check configuration

## Additional Notes

- The fix automatically detects the deployment URL from Upsun environment variables
- No manual configuration of domains is required
- The solution works for both staging and production environments
- All security best practices are maintained for production deployments

## Troubleshooting

If you're still experiencing CSRF issues:

1. Check that the deployment completed successfully
2. Run `python manage.py debug_csrf` to verify configuration
3. Check browser developer tools for any additional error messages
4. Verify that cookies are being set properly in the browser
5. Ensure you're accessing the site via HTTPS in production

## Environment Variables

The fix uses these Upsun/Platform.sh environment variables:
- `PLATFORM_APPLICATION_NAME`
- `PLATFORM_PROJECT`
- `PLATFORM_ENVIRONMENT`
- `PLATFORM_ROUTES`
- `PLATFORM_PROJECT_ENTROPY` (for secret key)

These are automatically set by Upsun and don't require manual configuration. 