from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from common.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

class DashboardStatsView(APIView):
    def get(self, request, project_id=None):
        try:
            days_back = int(request.GET.get('days_back', 30))
            dashboard_service = DashboardService(project_id=project_id)
            stats = dashboard_service.get_project_stats(days_back=days_back)
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return Response(
                {'error': 'Failed to retrieve dashboard statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DashboardActivityTimelineView(APIView):
    def get(self, request, project_id=None):
        try:
            days_back = int(request.GET.get('days_back', 30))
            dashboard_service = DashboardService(project_id=project_id)
            timeline = dashboard_service.get_activity_timeline(days_back=days_back)
            return Response(timeline, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting activity timeline: {e}")
            return Response(
                {'error': 'Failed to retrieve activity timeline'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DashboardPlatformDistributionView(APIView):
    def get(self, request, project_id=None):
        try:
            dashboard_service = DashboardService(project_id=project_id)
            distribution = dashboard_service.get_platform_distribution()
            return Response(distribution, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting platform distribution: {e}")
            return Response(
                {'error': 'Failed to retrieve platform distribution'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DashboardRecentActivityView(APIView):
    def get(self, request, project_id=None):
        try:
            limit = int(request.GET.get('limit', 5))
            dashboard_service = DashboardService(project_id=project_id)
            activity = dashboard_service.get_recent_activity(limit=limit)
            return Response(activity, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return Response(
                {'error': 'Failed to retrieve recent activity'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DashboardTopPerformersView(APIView):
    def get(self, request, project_id=None):
        try:
            limit = int(request.GET.get('limit', 3))
            dashboard_service = DashboardService(project_id=project_id)
            performers = dashboard_service.get_top_performers(limit=limit)
            return Response(performers, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting top performers: {e}")
            return Response(
                {'error': 'Failed to retrieve top performers'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DashboardWeeklyGoalsView(APIView):
    def get(self, request, project_id=None):
        try:
            dashboard_service = DashboardService(project_id=project_id)
            goals = dashboard_service.get_weekly_goals()
            return Response(goals, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting weekly goals: {e}")
            return Response(
                {'error': 'Failed to retrieve weekly goals'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )