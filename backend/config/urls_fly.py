"""
URL configuration for Fly.io deployment - serves both API and frontend
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os


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

def health_check(request):
    """Health check endpoint for Docker container monitoring"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)

def favicon_view(request):
    """Return empty response for favicon to prevent 404s"""
    return HttpResponse(status=204)  # No Content

def frontend_view(request, path=''):
    """Serve frontend index.html for React Router"""
    frontend_dist = os.path.join(settings.BASE_DIR.parent, 'frontend', 'dist')
    index_path = os.path.join(frontend_dist, 'index.html')

    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    else:
        return HttpResponse('Frontend not built', status=404)


urlpatterns = [
    # API endpoints
    path("api/health/", health_check, name="health_check"),
    path("api/status/", api_status, name="api_status"),
    path("favicon.ico", favicon_view, name="favicon"),
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/admin/", include("users.urls_admin")),
    path("api/reports/", include("reports.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("api/data-collector/", include("data_collector.urls")),
    path("api/query-builder/", include("query_builder.urls")),
    path("api/instagram_data/", include("instagram_data.urls")),
    path("api/instagram-data/", include("instagram_data.urls")),
    path("api/facebook-data/", include("facebook_data.urls")),
    path("api/track-accounts/", include("track_accounts.urls")),
    path("api/linkedin-data/", include("linkedin_data.urls")),
    path("api/tiktok-data/", include("tiktok_data.urls")),
    path("api/brightdata/", include("brightdata_integration.urls")),
    path("api/chat/", include("chat.urls")),
    path("api/workflow/", include("workflow.urls")),
    path("api/dashboard/", include("dashboard.urls")),

    # Serve static files and frontend assets
    re_path(r'^assets/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.BASE_DIR.parent, 'frontend', 'dist', 'assets')}),

    # Catch-all for React Router (must be last)
    re_path(r'^(?!api/).*$', frontend_view, name='frontend'),
]

# Serve static files in production
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)