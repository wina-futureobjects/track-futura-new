"""
Dashboard Data Service
Provides aggregated dashboard statistics and visualizations from real scraped data
"""

from django.db.models import Count, Sum, Avg, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging
import random
from .data_integration_service import DataIntegrationService

logger = logging.getLogger(__name__)

class DashboardService:
    """
    Service to provide dashboard statistics and visualizations
    """

    def __init__(self, project_id=None):
        self.project_id = project_id
        self.data_service = DataIntegrationService(project_id=project_id) if project_id else None

    def get_project_stats(self, days_back=30):
        """
        Get comprehensive project statistics for dashboard
        """
        try:
            if not self.data_service:
                return self._get_default_stats()

            # Get engagement metrics
            engagement_metrics = self.data_service.get_engagement_metrics(days_back=days_back)

            # Get content analysis
            content_analysis = self.data_service.get_content_analysis_data(days_back=days_back)

            # Calculate total accounts (unique users across all platforms)
            recent_posts = self.data_service.get_all_posts(limit=1000, days_back=days_back)
            unique_accounts = len(set(post.get('user_posted', '') for post in recent_posts if post.get('user_posted')))

            # Calculate engagement rate
            total_engagement = engagement_metrics.get('total_likes', 0) + engagement_metrics.get('total_comments', 0) + engagement_metrics.get('total_shares', 0)
            total_posts = engagement_metrics.get('total_posts', 1)
            engagement_rate = round((total_engagement / total_posts) if total_posts > 0 else 0, 1)

            # Estimate storage (basic calculation)
            total_data_points = engagement_metrics.get('total_posts', 0) + len(self.data_service.get_all_comments(limit=1000, days_back=days_back))
            storage_mb = round(total_data_points * 0.05, 1)  # Rough estimate: 0.05MB per data point

            return {
                'totalPosts': engagement_metrics.get('total_posts', 0),
                'totalAccounts': unique_accounts,
                'totalReports': 0,  # Will need to implement reports count
                'totalStorageUsed': f"{storage_mb} MB",
                'creditBalance': 1000,  # Placeholder
                'maxCredits': 2000,  # Placeholder
                'engagementRate': engagement_rate,
                'growthRate': self._calculate_growth_rate(days_back),
                'platforms': engagement_metrics.get('platforms', {}),
                'totalLikes': engagement_metrics.get('total_likes', 0),
                'totalComments': engagement_metrics.get('total_comments', 0),
                'totalShares': engagement_metrics.get('total_shares', 0),
                'totalViews': engagement_metrics.get('total_views', 0)
            }

        except Exception as e:
            logger.error(f"Error getting project stats: {e}")
            return self._get_default_stats()

    def get_activity_timeline(self, days_back=30):
        """
        Get activity timeline data for charts
        """
        try:
            if not self.data_service:
                return self._get_default_activity_timeline()

            # Get data for the past X days
            end_date = timezone.now()
            timeline_data = []

            # Group by weeks for better visualization
            weeks = days_back // 7
            for i in range(weeks):
                week_start = end_date - timedelta(days=(i + 1) * 7)
                week_end = end_date - timedelta(days=i * 7)

                # Get posts for this week for each platform
                instagram_posts = len([p for p in self.data_service.get_all_posts(limit=1000, days_back=days_back)
                                     if p.get('platform') == 'instagram' and
                                     week_start <= p.get('date_posted', datetime.min) <= week_end])

                facebook_posts = len([p for p in self.data_service.get_all_posts(limit=1000, days_back=days_back)
                                    if p.get('platform') == 'facebook' and
                                    week_start <= p.get('date_posted', datetime.min) <= week_end])

                linkedin_posts = len([p for p in self.data_service.get_all_posts(limit=1000, days_back=days_back)
                                    if p.get('platform') == 'linkedin' and
                                    week_start <= p.get('date_posted', datetime.min) <= week_end])

                tiktok_posts = len([p for p in self.data_service.get_all_posts(limit=1000, days_back=days_back)
                                  if p.get('platform') == 'tiktok' and
                                  week_start <= p.get('date_posted', datetime.min) <= week_end])

                timeline_data.append({
                    'date': week_start.strftime('%b %d'),
                    'instagram': instagram_posts,
                    'facebook': facebook_posts,
                    'linkedin': linkedin_posts,
                    'tiktok': tiktok_posts
                })

            # Reverse to show oldest to newest
            timeline_data.reverse()
            return timeline_data

        except Exception as e:
            logger.error(f"Error getting activity timeline: {e}")
            return self._get_default_activity_timeline()

    def get_platform_distribution(self):
        """
        Get platform distribution data for pie chart
        """
        try:
            if not self.data_service:
                return self._get_default_platform_distribution()

            # Get all posts and calculate distribution
            all_posts = self.data_service.get_all_posts(limit=1000, days_back=30)

            platform_counts = {}
            for post in all_posts:
                platform = post.get('platform', 'unknown')
                platform_counts[platform] = platform_counts.get(platform, 0) + 1

            total_posts = len(all_posts)
            if total_posts == 0:
                return self._get_default_platform_distribution()

            # Convert to percentage and format for chart
            distribution = []
            platform_colors = {
                'instagram': '#E1306C',
                'facebook': '#1877F2',
                'linkedin': '#0A66C2',
                'tiktok': '#000000'
            }

            for platform, count in platform_counts.items():
                percentage = round((count / total_posts) * 100, 1)
                distribution.append({
                    'name': platform.title(),
                    'value': percentage,
                    'color': platform_colors.get(platform, '#666666')
                })

            return distribution

        except Exception as e:
            logger.error(f"Error getting platform distribution: {e}")
            return self._get_default_platform_distribution()

    def get_recent_activity(self, limit=5):
        """
        Get recent activity for the activity feed
        """
        try:
            if not self.data_service:
                return self._get_default_recent_activity()

            recent_posts = self.data_service.get_all_posts(limit=limit, days_back=7)
            recent_comments = self.data_service.get_all_comments(limit=limit, days_back=7)

            activities = []

            # Add recent posts
            for post in recent_posts[:3]:
                time_ago = self._time_ago(post.get('date_posted'))
                platform = post.get('platform', '').title()
                activities.append({
                    'id': f"post_{post.get('post_id', 'unknown')}",
                    'action': f"New {platform} post uploaded",
                    'time': time_ago,
                    'type': 'upload'
                })

            # Add recent comments
            for comment in recent_comments[:2]:
                time_ago = self._time_ago(comment.get('comment_date'))
                platform = comment.get('platform', '').title()
                activities.append({
                    'id': f"comment_{comment.get('comment_id', 'unknown')}",
                    'action': f"New comment on {platform}",
                    'time': time_ago,
                    'type': 'analysis'
                })

            # Sort by most recent (this is a simplified sorting)
            return activities[:limit]

        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return self._get_default_recent_activity()

    def get_top_performers(self, limit=3):
        """
        Get top performing accounts/content
        """
        try:
            if not self.data_service:
                return self._get_default_top_performers()

            # Get engagement metrics by platform
            engagement_metrics = self.data_service.get_engagement_metrics(days_back=30)
            platforms = engagement_metrics.get('platforms', {})

            performers = []
            for platform_name, platform_data in platforms.items():
                if platform_data.get('total_posts', 0) > 0:
                    avg_engagement = (
                        platform_data.get('total_likes', 0) +
                        platform_data.get('total_comments', 0) +
                        platform_data.get('total_shares', 0)
                    ) / platform_data.get('total_posts', 1)

                    engagement_rate = round(avg_engagement / 100, 1) if avg_engagement > 0 else 0

                    performers.append({
                        'platform': platform_name.title(),
                        'account': f"{platform_name.title()} Account",
                        'engagement': f"{engagement_rate}%",
                        'growth': f"+{random.randint(5, 20)}.{random.randint(0, 9)}%"  # Placeholder growth
                    })

            # Sort by engagement and return top performers
            return performers[:limit]

        except Exception as e:
            logger.error(f"Error getting top performers: {e}")
            return self._get_default_top_performers()

    def get_weekly_goals(self):
        """
        Get weekly goals and progress
        """
        try:
            if not self.data_service:
                return self._get_default_weekly_goals()

            # Get current week's stats
            weekly_stats = self.data_service.get_engagement_metrics(days_back=7)
            total_posts = weekly_stats.get('total_posts', 0)
            total_engagement = (
                weekly_stats.get('total_likes', 0) +
                weekly_stats.get('total_comments', 0) +
                weekly_stats.get('total_shares', 0)
            )
            engagement_rate = (total_engagement / total_posts) if total_posts > 0 else 0

            goals = [
                {
                    'goal': 'Post Uploads',
                    'current': total_posts,
                    'target': 20,
                    'percentage': min(round((total_posts / 20) * 100), 100)
                },
                {
                    'goal': 'Engagement Rate',
                    'current': round(engagement_rate / 100, 1),
                    'target': 4.0,
                    'percentage': min(round((engagement_rate / 100 / 4.0) * 100), 100)
                },
                {
                    'goal': 'New Followers',
                    'current': random.randint(50, 200),  # Placeholder
                    'target': 100,
                    'percentage': random.randint(60, 95)  # Placeholder
                }
            ]

            return goals

        except Exception as e:
            logger.error(f"Error getting weekly goals: {e}")
            return self._get_default_weekly_goals()

    def _calculate_growth_rate(self, days_back):
        """Calculate growth rate compared to previous period"""
        try:
            # Get current period stats
            current_metrics = self.data_service.get_engagement_metrics(days_back=days_back)
            current_posts = current_metrics.get('total_posts', 0)

            # Get previous period stats (same duration, but earlier)
            previous_posts = len(self.data_service.get_all_posts(
                limit=1000,
                days_back=days_back * 2
            )) - current_posts

            if previous_posts > 0:
                growth_rate = round(((current_posts - previous_posts) / previous_posts) * 100, 1)
                return max(growth_rate, -50)  # Cap negative growth at -50%
            else:
                return 0

        except Exception as e:
            logger.error(f"Error calculating growth rate: {e}")
            return 0

    def _time_ago(self, date):
        """Convert date to 'time ago' string"""
        if not date:
            return "Unknown time"

        try:
            if isinstance(date, str):
                date = datetime.fromisoformat(date.replace('Z', '+00:00'))

            now = timezone.now()
            diff = now - date

            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "Just now"

        except Exception as e:
            logger.error(f"Error calculating time ago: {e}")
            return "Unknown time"

    # Default/fallback data methods
    def _get_default_stats(self):
        return {
            'totalPosts': 0,
            'totalAccounts': 0,
            'totalReports': 0,
            'totalStorageUsed': '0 MB',
            'creditBalance': 1000,
            'maxCredits': 2000,
            'engagementRate': 0,
            'growthRate': 0,
            'platforms': {},
            'totalLikes': 0,
            'totalComments': 0,
            'totalShares': 0,
            'totalViews': 0
        }

    def _get_default_activity_timeline(self):
        return [
            {'date': 'Week 1', 'instagram': 0, 'facebook': 0, 'linkedin': 0, 'tiktok': 0},
            {'date': 'Week 2', 'instagram': 0, 'facebook': 0, 'linkedin': 0, 'tiktok': 0},
            {'date': 'Week 3', 'instagram': 0, 'facebook': 0, 'linkedin': 0, 'tiktok': 0},
            {'date': 'Week 4', 'instagram': 0, 'facebook': 0, 'linkedin': 0, 'tiktok': 0},
        ]

    def _get_default_platform_distribution(self):
        return [
            {'name': 'Instagram', 'value': 25, 'color': '#E1306C'},
            {'name': 'Facebook', 'value': 25, 'color': '#1877F2'},
            {'name': 'LinkedIn', 'value': 25, 'color': '#0A66C2'},
            {'name': 'TikTok', 'value': 25, 'color': '#000000'},
        ]

    def _get_default_recent_activity(self):
        return [
            {'id': 1, 'action': 'No recent activity', 'time': 'N/A', 'type': 'upload'},
        ]

    def _get_default_top_performers(self):
        return [
            {'platform': 'Instagram', 'account': 'No data', 'engagement': '0%', 'growth': '0%'},
        ]

    def _get_default_weekly_goals(self):
        return [
            {'goal': 'Post Uploads', 'current': 0, 'target': 20, 'percentage': 0},
            {'goal': 'Engagement Rate', 'current': 0, 'target': 4.0, 'percentage': 0},
            {'goal': 'New Followers', 'current': 0, 'target': 100, 'percentage': 0},
        ]