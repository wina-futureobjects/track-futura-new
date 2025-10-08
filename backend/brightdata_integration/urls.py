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
    
    # Direct trigger endpoint (function-based view for better production compatibility)
    path('trigger-scraper/', views.trigger_scraper_endpoint, name='trigger_scraper'),
    
    # Results endpoints
    path('results/<str:snapshot_id>/', views.fetch_brightdata_results, name='fetch_brightdata_results'),
    path('job-results/<int:job_folder_id>/', views.brightdata_job_results, name='brightdata_job_results'),
]