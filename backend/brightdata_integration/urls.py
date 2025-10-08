"""
BrightData Integration URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for viewsets
router = DefaultRouter()
router.register(r'configs', views.BrightDataConfigViewSet)
router.register(r'batch-jobs', views.BrightDataBatchJobViewSet)
router.register(r'scraper-requests', views.BrightDataScraperRequestViewSet)

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Webhook endpoints
    path('webhook/', views.brightdata_webhook, name='brightdata_webhook'),
    path('notify/', views.brightdata_notify, name='brightdata_notify'),
    
    # Direct trigger endpoint (maps to the action in BrightDataScraperRequestViewSet)
    path('trigger-scraper/', views.BrightDataScraperRequestViewSet.as_view({'post': 'trigger_scraper'}), name='trigger_scraper'),
]