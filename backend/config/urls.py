"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.template.response import TemplateResponse
import os

# EMERGENCY IMPORTS - Simple fallback endpoints
from .emergency import emergency_root, emergency_health, emergency_favicon


def serve_brightdata_trigger(request):
    """Serve the BrightData trigger page"""
    static_file_path = os.path.join(settings.BASE_DIR, 'static', 'brightdata_trigger.html')
    if os.path.exists(static_file_path):
        with open(static_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    else:
        return HttpResponse('BrightData trigger page not found', status=404)

def serve_frontend(request):
    """Serve the frontend application"""    
    # Path to the frontend index.html file
    frontend_path = os.path.join(settings.STATIC_ROOT or os.path.join(settings.BASE_DIR, 'staticfiles'), 'index.html')
    
    try:
        with open(frontend_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        # Fallback to a simple welcome page if frontend files are not found
        return HttpResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>TrackFutura - React Frontend Loading...</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; text-align: center; }
                .building { background: #f39c12; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="building">⚠️ React Frontend Not Found</div>
                <h1>TrackFutura - Social Media Analytics Platform</h1>
                <p>The React frontend files are not available. Expected location: """ + frontend_path + """</p>
                <p>Debug Info:</p>
                <ul>
                    <li>STATIC_ROOT: """ + str(settings.STATIC_ROOT) + """</li>
                    <li>BASE_DIR: """ + str(settings.BASE_DIR) + """</li>
                    <li>DEBUG: """ + str(settings.DEBUG) + """</li>
                </ul>
                <p><a href="/admin/">Access Admin Panel</a> | <a href="/api/">View API Documentation</a></p>
            </div>
        </body>
        </html>
        """, content_type='text/html')

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

def api_status(request):
    """API status endpoint for backward compatibility"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse({
            'status': 'healthy',
            'message': 'TrackFutura API is running',
            'database': 'connected',
            'version': '1.0',
            'timestamp': request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'message': 'Database connection failed',
            'error': str(e)
        }, status=503)



urlpatterns = [
    # EMERGENCY ENDPOINTS - Simple fallbacks that always work
    path("emergency/", emergency_root, name="emergency_root"),
    path("emergency/health/", emergency_health, name="emergency_health"), 
    path("emergency/favicon.ico", emergency_favicon, name="emergency_favicon"),
    
    path("trigger/", serve_brightdata_trigger, name="brightdata_trigger"),  # BrightData trigger page at base URL
    path("brightdata-trigger/", serve_brightdata_trigger, name="brightdata_trigger_alt"),  # Alternative path
    path("", serve_frontend, name="frontend"),  # Serve frontend at root
    path("api/health/", health_check, name="health_check"),  # Health check endpoint
    path("favicon.ico", favicon_view, name="favicon"),  # Handle favicon
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/admin/", include("users.urls_admin")),
    path("api/reports/", include("reports.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("api/data-collector/", include("data_collector.urls")),
    path("api/query-builder/", include("query_builder.urls")),
    path("api/instagram_data/", include("instagram_data.urls")),
    path("api/instagram-data/", include("instagram_data.urls")),  # Support both formats
    path("api/facebook-data/", include("facebook_data.urls")),
    path("api/track-accounts/", include("track_accounts.urls")),
    path("api/linkedin-data/", include("linkedin_data.urls")),
    path("api/tiktok-data/", include("tiktok_data.urls")),
    path("api/apify/", include("apify_integration.urls")),
    path("api/brightdata/", include("brightdata_integration.urls")),  # New BrightData API
    path("api/chat/", include("chat.urls")),
    path("api/workflow/", include("workflow.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/", RedirectView.as_view(url="/api/users/", permanent=False)),
]

# Serve static files in development and frontend assets
if settings.DEBUG or True:  # Always serve static files for frontend
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.conf.urls.static import static
    
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Handle frontend assets explicitly
    urlpatterns += static('/assets/', document_root=os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'staticfiles', 'assets'))
    
    # Catch-all pattern for frontend routing (React Router)
    urlpatterns += [
        re_path(r'^(?!api|admin|static|media|assets).*$', serve_frontend, name="frontend_catchall"),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
