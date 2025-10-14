"""
Web Unlocker URLs Configuration
Direct endpoints for Web Unlocker functionality
"""

from django.urls import path
from .web_unlocker_views import WebUnlockerAPIView

urlpatterns = [
    # Web Unlocker main endpoint - handles POST requests for scraping
    path('', WebUnlockerAPIView.as_view(), name='web_unlocker_api'),
    
    # Alternative endpoint names for flexibility
    path('scrape/', WebUnlockerAPIView.as_view(), name='web_unlocker_scrape'),
    path('run/', WebUnlockerAPIView.as_view(), name='web_unlocker_run'),
]