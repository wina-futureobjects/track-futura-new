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
    
    # EMERGENCY DEBUG ENDPOINT - Shows all available runs
    path('debug/available-runs/', lambda request: __import__('brightdata_integration.emergency_run_debug', fromlist=['emergency_run_info']).emergency_run_info(request), name='available_runs_debug'),
    
    # EMERGENCY FIX - Create folder 286 on production
    path('debug/create-folder-286/', views.emergency_create_folder_286, name='create_folder_286'),
    
    # UPDATE FOLDER 286 - Add Instagram/Facebook subfolders to existing folder
    path('update-286/', views.update_folder_286_structure, name='update_folder_286'),
    
    # FIX REAL DATA - Link actual BrightData snapshots to proper folders  
    path('fix-real-data/', views.fix_real_brightdata_structure, name='fix_real_data'),
    
    # CLEAN STRUCTURE - Remove test data and create proper platform structure
    path('clean-structure/', views.clean_folder_structure, name='clean_structure'),
    
    # FOLDER STRUCTURE - Create complete folder structure with Instagram/Facebook
    path('setup-folders/', views.create_complete_folder_structure, name='create_folder_structure'),
    
    # Webhook endpoints
    path('webhook/', views.brightdata_webhook, name='brightdata_webhook'),
    path('notify/', views.brightdata_notify, name='brightdata_notify'),
    
    # Direct trigger endpoint (function-based view for better production compatibility)
    path('trigger-scraper/', views.trigger_scraper_endpoint, name='trigger_scraper'),
    
    # Results endpoints
    path('results/<str:snapshot_id>/', views.fetch_brightdata_results, name='fetch_brightdata_results'),
    path('job-results/<int:job_folder_id>/', views.brightdata_job_results, name='brightdata_job_results'),

    # CRITICAL: Direct /run/ endpoint for data storage - MUST BE FIRST (more specific pattern)
    path('data-storage/run/<str:run_id>/', views.data_storage_run_endpoint, name='data_storage_run_endpoint'),
    
    # 🚨 PRODUCTION FIX: Add /run/ redirect to /job-results/ for immediate fix
    path('run/<str:run_id>/', views.run_redirect_endpoint, name='run_redirect_endpoint'),
    
    # New human-friendly endpoints (less specific pattern comes after)
    path('data-storage/<str:folder_name>/<int:scrape_num>/', views.data_storage_folder_scrape, name='data_storage_folder_scrape'),
    
    # Run info lookup endpoint for continuity
    path('run-info/<str:run_id>/', views.run_info_lookup, name='run_info_lookup'),
    path('data-storage/<str:folder_name>/<int:scrape_num>/<str:platform>/', views.data_storage_folder_scrape_platform, name='data_storage_folder_scrape_platform'),
    path('data-storage/<str:folder_name>/<int:scrape_num>/<str:platform>/post/', views.data_storage_folder_scrape_platform_post, name='data_storage_folder_scrape_platform_post'),
    path('data-storage/<str:folder_name>/<int:scrape_num>/<str:platform>/post/<str:account>/', views.data_storage_folder_scrape_platform_post_account, name='data_storage_folder_scrape_platform_post_account'),
]