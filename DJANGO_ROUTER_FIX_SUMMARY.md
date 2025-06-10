# Django Router Registration Fix Summary

## Problem
The Django backend was failing to start with the following error:
```
django.core.exceptions.ImproperlyConfigured: Router with basename "brightdataconfig" is already registered. Please provide a unique basename for viewset "<class 'brightdata_integration.views.BrightdataConfigViewSet'>"
```

## Root Cause
In `backend/brightdata_integration/urls.py`, the same ViewSets were being registered multiple times in the DRF router without unique basenames:

```python
router.register(r'configs', views.BrightdataConfigViewSet)
router.register(r'config', views.BrightdataConfigViewSet)  # DUPLICATE!
router.register(r'requests', views.ScraperRequestViewSet)
router.register(r'scraper-requests', views.ScraperRequestViewSet)  # DUPLICATE!
```

## Solution
Added unique basenames for the alternative URL formats:

```python
router.register(r'configs', views.BrightdataConfigViewSet)
router.register(r'config', views.BrightdataConfigViewSet, basename='brightdataconfig-alt')
router.register(r'requests', views.ScraperRequestViewSet)
router.register(r'scraper-requests', views.ScraperRequestViewSet, basename='scraperrequest-alt')
```

## Result
- ✅ Django backend now starts successfully
- ✅ All API endpoints are working:
  - `http://localhost:8000/api/brightdata/config/` → 200 OK
  - `http://localhost:8000/api/instagram_data/folders/` → 200 OK
  - `http://localhost:8000/api/brightdata/scraper-requests/` → 200 OK
- ✅ Both URL formats now work (configs/config, requests/scraper-requests)

## Files Modified
- `backend/brightdata_integration/urls.py` - Added unique basenames for duplicate router registrations

## Key Lesson
When registering the same ViewSet multiple times in a DRF router (for URL compatibility), each registration must have a unique basename to avoid conflicts.
