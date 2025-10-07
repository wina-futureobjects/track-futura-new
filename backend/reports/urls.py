from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReportTemplateViewSet,
    GeneratedReportViewSet,
    EngagementMetricsReportView,
    SentimentAnalysisReportView,
    ContentAnalysisReportView,
    TrendAnalysisReportView,
    CompetitiveAnalysisReportView,
    UserBehaviorReportView,
    EnhancedPDFAnalysisView
)

router = DefaultRouter()
router.register(r'templates', ReportTemplateViewSet)
router.register(r'generated', GeneratedReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Template-specific endpoints
    path('engagement-metrics/<int:report_id>/', EngagementMetricsReportView.as_view(), name='engagement-metrics'),
    path('sentiment-analysis/<int:report_id>/', SentimentAnalysisReportView.as_view(), name='sentiment-analysis'),
    path('content-analysis/<int:report_id>/', ContentAnalysisReportView.as_view(), name='content-analysis'),
    path('trend-analysis/<int:report_id>/', TrendAnalysisReportView.as_view(), name='trend-analysis'),
    path('competitive-analysis/<int:report_id>/', CompetitiveAnalysisReportView.as_view(), name='competitive-analysis'),
    path('user-behavior/<int:report_id>/', UserBehaviorReportView.as_view(), name='user-behavior'),
    # Enhanced PDF analysis with LLM
    path('enhance-pdf-analysis/', EnhancedPDFAnalysisView.as_view(), name='enhance-pdf-analysis'),
] 