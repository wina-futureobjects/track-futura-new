from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .unified_api import unified_data_storage_api

router = DefaultRouter()
router.register(r'sources', views.TrackSourceViewSet, basename='track-source')
# Keep accounts endpoint for backward compatibility - point to same viewset
router.register(r'accounts', views.TrackSourceViewSet, basename='track-account')
router.register(r'source-folders', views.SourceFolderViewSet, basename='source-folder')
router.register(r'reports', views.ReportFolderViewSet, basename='report-folder')
router.register(r'report-folders', views.UnifiedRunFolderViewSet, basename='unified-run-folder')

urlpatterns = [
    path('', include(router.urls)),
    path('fix-folder-4/', views.fix_folder_4_api, name='fix-folder-4'),
    # 🎯 UNIFIED DATA STORAGE API - Single endpoint for all folders
    path('unified-folders/', unified_data_storage_api, name='unified_data_storage_api'),
] 