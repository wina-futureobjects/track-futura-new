from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('stats/<str:project_id>/', views.DashboardStatsView.as_view(), name='dashboard-stats-project'),
    path('activity-timeline/', views.DashboardActivityTimelineView.as_view(), name='dashboard-activity-timeline'),
    path('activity-timeline/<str:project_id>/', views.DashboardActivityTimelineView.as_view(), name='dashboard-activity-timeline-project'),
    path('platform-distribution/', views.DashboardPlatformDistributionView.as_view(), name='dashboard-platform-distribution'),
    path('platform-distribution/<str:project_id>/', views.DashboardPlatformDistributionView.as_view(), name='dashboard-platform-distribution-project'),
    path('recent-activity/', views.DashboardRecentActivityView.as_view(), name='dashboard-recent-activity'),
    path('recent-activity/<str:project_id>/', views.DashboardRecentActivityView.as_view(), name='dashboard-recent-activity-project'),
    path('top-performers/', views.DashboardTopPerformersView.as_view(), name='dashboard-top-performers'),
    path('top-performers/<str:project_id>/', views.DashboardTopPerformersView.as_view(), name='dashboard-top-performers-project'),
    path('weekly-goals/', views.DashboardWeeklyGoalsView.as_view(), name='dashboard-weekly-goals'),
    path('weekly-goals/<str:project_id>/', views.DashboardWeeklyGoalsView.as_view(), name='dashboard-weekly-goals-project'),
]