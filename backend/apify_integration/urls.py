from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApifyConfigViewSet, ApifyBatchJobViewSet, ApifyScraperRequestViewSet, apify_webhook, apify_notify

router = DefaultRouter()
router.register(r'configs', ApifyConfigViewSet)
router.register(r'batch-jobs', ApifyBatchJobViewSet)
router.register(r'scraper-requests', ApifyScraperRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/', apify_webhook, name='apify_webhook'),
    path('notify/', apify_notify, name='apify_notify'),
]
