"""
EMERGENCY SIMPLE VIEWS - Most basic possible Django endpoints
"""
from django.http import HttpResponse, JsonResponse

def emergency_root(request):
    """Ultra simple root endpoint"""
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head><title>TrackFutura Emergency Mode</title></head>
    <body>
        <h1>🟢 TrackFutura Emergency Mode Active</h1>
        <p>Website is running in emergency mode.</p>
        <p>Time: Django server is responding</p>
        <ul>
            <li><a href="/emergency/health/">Health Check</a></li>
            <li><a href="/admin/">Admin Panel</a></li>
            <li><a href="/api/users/">API Users</a></li>
        </ul>
    </body>
    </html>
    """)

def emergency_health(request):
    """Ultra simple health endpoint"""
    return JsonResponse({"status": "ok", "message": "Emergency mode active"})

def emergency_favicon(request):
    """Empty favicon to prevent 404s"""
    return HttpResponse(status=204)