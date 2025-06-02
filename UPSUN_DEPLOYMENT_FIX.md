# Upsun Deployment Issues & Fixes

## Issues Identified

Your Upsun deployment was showing several errors that have been fixed:

### 1. DataDog Tracing API Key Errors
```
portError: Server returned 400, check your API key. Ignoring.
WARNING:ddtrace.profiling.scheduler:Unable to export profile: ddtrace.profiling.exporter.ExportError: Server returned 400, check your API key. Ignoring.
```

**Root Cause**: Upsun was auto-injecting DataDog tracing without a valid API key.

**Fix Applied**: Added environment variables to disable DataDog tracing in production:
```python
# Disable DataDog tracing if auto-injected by Upsun
os.environ['DD_TRACE_ENABLED'] = 'false'
os.environ['DD_PROFILING_ENABLED'] = 'false'
```

### 2. CSRF Trusted Origins Error
```
WARNING:django.security.csrf:Forbidden (Origin checking failed - https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site does not match any trusted origins.)
```

**Root Cause**: Django's CSRF protection was blocking requests from the Upsun deployment URL.

**Fix Applied**: Updated CSRF_TRUSTED_ORIGINS and ALLOWED_HOSTS to include the specific Upsun URLs:
```python
# Added specific Upsun URLs to trusted origins
upsun_url = "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site"
frontend_url = "https://upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site"

# Added to ALLOWED_HOSTS
upsun_hosts = [
    'api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site',
    'upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site'
]
```

### 3. Root URL 404 Error
```
WARNING:django.request:Not Found: /
```

**Root Cause**: No URL pattern was defined for the root path `/`.

**Fix Applied**: Added a root URL handler that returns API status:
```python
def api_status(request):
    """Simple API status endpoint for root path"""
    return JsonResponse({
        'status': 'Track-Futura API is running',
        'version': '1.0',
        'endpoints': {
            'users': '/api/users/',
            'reports': '/api/reports/',
            'analytics': '/api/analytics/',
            'admin': '/admin/',
        }
    })

urlpatterns = [
    path("", api_status, name="api_status"),
    # ... other patterns
]
```

### 4. Missing Favicon Error
```
WARNING:django.request:Not Found: /favicon.ico
```

**Root Cause**: Browsers automatically request `/favicon.ico` but no handler was defined.

**Fix Applied**: Added a favicon handler that returns empty response:
```python
def favicon_view(request):
    """Return empty response for favicon to prevent 404s"""
    return HttpResponse(status=204)  # No Content

urlpatterns = [
    path("favicon.ico", favicon_view, name="favicon"),
    # ... other patterns
]
```

## Files Modified

1. **`backend/config/settings.py`**:
   - Added DataDog tracing disable flags
   - Updated CSRF_TRUSTED_ORIGINS with specific Upsun URLs
   - Updated ALLOWED_HOSTS with specific Upsun hostnames

2. **`backend/config/urls.py`**:
   - Added root URL handler for API status
   - Added favicon handler to prevent 404s
   - Imported HttpResponse for proper responses

## Testing the Fixes

After deploying these changes to Upsun, you should see:

1. ✅ No more DataDog tracing errors
2. ✅ No more CSRF forbidden errors on admin login
3. ✅ No more 404 errors for root path
4. ✅ No more 404 errors for favicon.ico

## Additional Recommendations

### 1. Add a Real Favicon
Copy a proper `favicon.ico` file to your static directory and update the URL pattern:
```python
path("favicon.ico", RedirectView.as_view(url="/static/favicon.ico", permanent=True)),
```

### 2. Environment Variables
Consider setting these environment variables in your Upsun configuration:
```yaml
variables:
  env:
    DD_TRACE_ENABLED: "false"
    DD_PROFILING_ENABLED: "false"
    DJANGO_SETTINGS_MODULE: "config.settings"
    DEBUG: "False"
```

### 3. Monitor Deployment
After deployment, check the logs to confirm all errors are resolved:
```bash
upsun logs -f
```

### 4. Test Admin Access
Try accessing the Django admin at your deployment URL:
```
https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/admin/
```

## Deployment Status

The fixes have been applied and are ready for deployment. The next deployment should resolve all the identified issues. 