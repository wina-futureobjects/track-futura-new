from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'folders', views.TrackAccountFolderViewSet)
router.register(r'accounts', views.TrackAccountViewSet, basename='track-account')
router.register(r'reports', views.ReportFolderViewSet, basename='report-folder')

urlpatterns = [
    path('', include(router.urls)),
] 