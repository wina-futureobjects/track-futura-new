from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'configs', views.BrightdataConfigViewSet)
router.register(r'requests', views.ScraperRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/', views.brightdata_webhook, name='brightdata_webhook'),
] 