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

    # Webhook monitoring endpoints
    path('webhook/metrics/', views.webhook_metrics, name='webhook_metrics'),
    path('webhook/health/', views.webhook_health, name='webhook_health'),
    path('webhook/events/', views.webhook_events, name='webhook_events'),
    path('webhook/alerts/', views.webhook_alerts, name='webhook_alerts'),
    path('webhook/analytics/', views.webhook_analytics, name='webhook_analytics'),
    path('webhook/test/', views.test_webhook_security, name='test_webhook_security'),
]
