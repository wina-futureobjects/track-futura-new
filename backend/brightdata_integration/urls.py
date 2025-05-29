from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'configs', views.BrightdataConfigViewSet)
router.register(r'requests', views.ScraperRequestViewSet)
router.register(r'batch-jobs', views.BatchScraperJobViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/', views.brightdata_webhook, name='brightdata_webhook'),
    path('notify/', views.brightdata_notify, name='brightdata_notify'),
    path('comments/scrape/', views.scrape_comments, name='scrape_comments'),
] 