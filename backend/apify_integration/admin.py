from django.contrib import admin
from .models import ApifyConfig, ApifyBatchJob, ApifyScraperRequest, ApifyNotification, ApifyWebhookEvent

admin.site.register(ApifyConfig)
admin.site.register(ApifyBatchJob)
admin.site.register(ApifyScraperRequest)
admin.site.register(ApifyNotification)
admin.site.register(ApifyWebhookEvent)
