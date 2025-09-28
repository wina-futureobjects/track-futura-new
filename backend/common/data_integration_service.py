"""
Data Integration Service for AI Analysis
Provides unified access to scraped social media data across all platforms
"""

from django.db.models import Q, Count, Avg, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from users.models import Project
import json
import logging

logger = logging.getLogger(__name__)

class DataIntegrationService:
    """
    Service to integrate scraped data from all social media platforms
    for AI analysis in both chatbot and reports
    """

    def __init__(self, project_id=None):
        self.project_id = project_id
        self.project = None
        if project_id:
            try:
                from users.models import Project
                self.project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                logger.warning(f"Project {project_id} not found")

    def get_all_posts(self, limit=100, platform=None, days_back=30):
        """
        Get posts from all platforms for analysis
        """
        posts_data = []
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days_back)

        # Get Instagram posts
        if not platform or platform == 'instagram':
            posts_data.extend(self._get_instagram_posts(limit, start_date, end_date))

        # Get Facebook posts
        if not platform or platform == 'facebook':
            posts_data.extend(self._get_facebook_posts(limit, start_date, end_date))

        # Get LinkedIn posts
        if not platform or platform == 'linkedin':
            posts_data.extend(self._get_linkedin_posts(limit, start_date, end_date))

        # Get TikTok posts
        if not platform or platform == 'tiktok':
            posts_data.extend(self._get_tiktok_posts(limit, start_date, end_date))

        # Sort by date and limit
        posts_data.sort(key=lambda x: x.get('date_posted', datetime.min), reverse=True)
        return posts_data[:limit]

    def get_all_comments(self, limit=200, platform=None, days_back=30):
        """
        Get comments from all platforms for sentiment analysis
        """
        comments_data = []
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days_back)

        # Get Instagram comments
        if not platform or platform == 'instagram':
            comments_data.extend(self._get_instagram_comments(limit, start_date, end_date))

        # Get Facebook comments
        if not platform or platform == 'facebook':
            comments_data.extend(self._get_facebook_comments(limit, start_date, end_date))

        # Get LinkedIn comments
        if not platform or platform == 'linkedin':
            comments_data.extend(self._get_linkedin_comments(limit, start_date, end_date))

        # Get TikTok comments
        if not platform or platform == 'tiktok':
            comments_data.extend(self._get_tiktok_comments(limit, start_date, end_date))

        # Sort by date and limit
        comments_data.sort(key=lambda x: x.get('comment_date', datetime.min), reverse=True)
        return comments_data[:limit]

    def get_engagement_metrics(self, days_back=30, platform=None):
        """
        Get engagement metrics across all platforms
        """
        metrics = {
            'total_posts': 0,
            'total_likes': 0,
            'total_comments': 0,
            'total_shares': 0,
            'total_views': 0,
            'platforms': {},
            'top_performing_posts': [],
            'engagement_trends': []
        }

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days_back)

        # Instagram metrics
        if not platform or platform == 'instagram':
            instagram_metrics = self._get_instagram_metrics(start_date, end_date)
            metrics['platforms']['instagram'] = instagram_metrics
            metrics['total_posts'] += instagram_metrics.get('total_posts', 0)
            metrics['total_likes'] += instagram_metrics.get('total_likes', 0)
            metrics['total_comments'] += instagram_metrics.get('total_comments', 0)
            metrics['total_views'] += instagram_metrics.get('total_views', 0)
            metrics['top_performing_posts'].extend(instagram_metrics.get('top_posts', []))

        # Facebook metrics
        if not platform or platform == 'facebook':
            facebook_metrics = self._get_facebook_metrics(start_date, end_date)
            metrics['platforms']['facebook'] = facebook_metrics
            metrics['total_posts'] += facebook_metrics.get('total_posts', 0)
            metrics['total_likes'] += facebook_metrics.get('total_likes', 0)
            metrics['total_comments'] += facebook_metrics.get('total_comments', 0)
            metrics['total_shares'] += facebook_metrics.get('total_shares', 0)
            metrics['top_performing_posts'].extend(facebook_metrics.get('top_posts', []))

        # LinkedIn metrics
        if not platform or platform == 'linkedin':
            linkedin_metrics = self._get_linkedin_metrics(start_date, end_date)
            metrics['platforms']['linkedin'] = linkedin_metrics
            metrics['total_posts'] += linkedin_metrics.get('total_posts', 0)
            metrics['total_likes'] += linkedin_metrics.get('total_likes', 0)
            metrics['total_comments'] += linkedin_metrics.get('total_comments', 0)
            metrics['total_shares'] += linkedin_metrics.get('total_shares', 0)
            metrics['top_performing_posts'].extend(linkedin_metrics.get('top_posts', []))

        # TikTok metrics
        if not platform or platform == 'tiktok':
            tiktok_metrics = self._get_tiktok_metrics(start_date, end_date)
            metrics['platforms']['tiktok'] = tiktok_metrics
            metrics['total_posts'] += tiktok_metrics.get('total_posts', 0)
            metrics['total_likes'] += tiktok_metrics.get('total_likes', 0)
            metrics['total_comments'] += tiktok_metrics.get('total_comments', 0)
            metrics['total_views'] += tiktok_metrics.get('total_views', 0)
            metrics['top_performing_posts'].extend(tiktok_metrics.get('top_posts', []))

        # Sort top performing posts
        metrics['top_performing_posts'].sort(
            key=lambda x: x.get('engagement_score', 0), reverse=True
        )
        metrics['top_performing_posts'] = metrics['top_performing_posts'][:10]

        return metrics

    def get_content_analysis_data(self, days_back=30, platform=None):
        """
        Get content analysis data including hashtags, content types, etc.
        """
        content_data = {
            'content_types': {},
            'hashtags': {},
            'posting_times': {},
            'user_mentions': {},
            'platforms': {}
        }

        posts = self.get_all_posts(limit=500, platform=platform, days_back=days_back)

        for post in posts:
            platform_name = post.get('platform', 'unknown')

            # Content type analysis
            content_type = post.get('content_type', 'post')
            if content_type not in content_data['content_types']:
                content_data['content_types'][content_type] = {
                    'count': 0,
                    'total_engagement': 0,
                    'avg_engagement': 0
                }

            engagement = (post.get('likes', 0) + post.get('num_comments', 0) +
                         post.get('num_shares', 0) + post.get('views', 0))

            content_data['content_types'][content_type]['count'] += 1
            content_data['content_types'][content_type]['total_engagement'] += engagement

            # Hashtag analysis
            hashtags = post.get('hashtags', [])
            if isinstance(hashtags, str):
                try:
                    hashtags = json.loads(hashtags) if hashtags.startswith('[') else hashtags.split()
                except:
                    hashtags = hashtags.split() if hashtags else []

            for hashtag in hashtags:
                if hashtag not in content_data['hashtags']:
                    content_data['hashtags'][hashtag] = {
                        'count': 0,
                        'total_engagement': 0,
                        'platforms': set()
                    }
                content_data['hashtags'][hashtag]['count'] += 1
                content_data['hashtags'][hashtag]['total_engagement'] += engagement
                content_data['hashtags'][hashtag]['platforms'].add(platform_name)

            # Posting time analysis
            if post.get('date_posted'):
                hour = post['date_posted'].hour
                if hour not in content_data['posting_times']:
                    content_data['posting_times'][hour] = {
                        'count': 0,
                        'total_engagement': 0
                    }
                content_data['posting_times'][hour]['count'] += 1
                content_data['posting_times'][hour]['total_engagement'] += engagement

        # Calculate averages
        for content_type in content_data['content_types']:
            count = content_data['content_types'][content_type]['count']
            if count > 0:
                content_data['content_types'][content_type]['avg_engagement'] = (
                    content_data['content_types'][content_type]['total_engagement'] / count
                )

        # Convert sets to lists for JSON serialization
        for hashtag in content_data['hashtags']:
            content_data['hashtags'][hashtag]['platforms'] = list(content_data['hashtags'][hashtag]['platforms'])

        return content_data

    def _get_instagram_posts(self, limit, start_date, end_date):
        """Get Instagram posts for the project"""
        try:
            from instagram_data.models import InstagramPost

            queryset = InstagramPost.objects.all()
            if self.project:
                queryset = queryset.filter(folder__project=self.project)

            posts = queryset.filter(
                date_posted__gte=start_date,
                date_posted__lte=end_date
            ).order_by('-date_posted')[:limit]

            return [{
                'platform': 'instagram',
                'post_id': post.post_id,
                'content': post.description or '',
                'user_posted': post.user_posted,
                'date_posted': post.date_posted,
                'likes': post.likes,
                'num_comments': post.num_comments,
                'views': post.views or 0,
                'hashtags': post.hashtags or [],
                'content_type': post.content_type or 'post',
                'url': post.url,
                'engagement_score': post.likes + post.num_comments + (post.views or 0)
            } for post in posts]
        except Exception as e:
            logger.error(f"Error fetching Instagram posts: {e}")
            return []

    def _get_facebook_posts(self, limit, start_date, end_date):
        """Get Facebook posts for the project"""
        try:
            from facebook_data.models import FacebookPost

            queryset = FacebookPost.objects.all()
            if self.project:
                queryset = queryset.filter(folder__project=self.project)

            posts = queryset.filter(
                date_posted__gte=start_date,
                date_posted__lte=end_date
            ).order_by('-date_posted')[:limit]

            return [{
                'platform': 'facebook',
                'post_id': post.post_id,
                'content': post.content or post.description or '',
                'user_posted': post.user_posted,
                'date_posted': post.date_posted,
                'likes': post.likes,
                'num_comments': post.num_comments,
                'num_shares': post.num_shares or 0,
                'views': post.video_view_count or 0,
                'hashtags': post.hashtags or '',
                'content_type': 'post',
                'url': post.url,
                'engagement_score': post.likes + post.num_comments + (post.num_shares or 0)
            } for post in posts]
        except Exception as e:
            logger.error(f"Error fetching Facebook posts: {e}")
            return []

    def _get_linkedin_posts(self, limit, start_date, end_date):
        """Get LinkedIn posts for the project"""
        try:
            from linkedin_data.models import LinkedInPost

            queryset = LinkedInPost.objects.all()
            if self.project:
                queryset = queryset.filter(folder__project=self.project)

            posts = queryset.filter(
                date_posted__gte=start_date,
                date_posted__lte=end_date
            ).order_by('-date_posted')[:limit]

            return [{
                'platform': 'linkedin',
                'post_id': post.post_id or str(post.id),
                'content': post.content or '',
                'user_posted': post.user_posted,
                'date_posted': post.date_posted,
                'likes': getattr(post, 'likes', 0),
                'num_comments': getattr(post, 'num_comments', 0),
                'num_shares': getattr(post, 'num_shares', 0),
                'hashtags': getattr(post, 'hashtags', '') or '',
                'content_type': 'post',
                'url': getattr(post, 'url', ''),
                'engagement_score': getattr(post, 'likes', 0) + getattr(post, 'num_comments', 0)
            } for post in posts]
        except Exception as e:
            logger.error(f"Error fetching LinkedIn posts: {e}")
            return []

    def _get_tiktok_posts(self, limit, start_date, end_date):
        """Get TikTok posts for the project"""
        try:
            from tiktok_data.models import TikTokPost

            queryset = TikTokPost.objects.all()
            if self.project:
                queryset = queryset.filter(folder__project=self.project)

            posts = queryset.filter(
                date_posted__gte=start_date,
                date_posted__lte=end_date
            ).order_by('-date_posted')[:limit]

            return [{
                'platform': 'tiktok',
                'post_id': post.post_id or str(post.id),
                'content': getattr(post, 'content', '') or getattr(post, 'description', ''),
                'user_posted': getattr(post, 'user_posted', ''),
                'date_posted': post.date_posted,
                'likes': getattr(post, 'likes', 0),
                'num_comments': getattr(post, 'num_comments', 0),
                'num_shares': getattr(post, 'num_shares', 0),
                'views': getattr(post, 'views', 0),
                'hashtags': getattr(post, 'hashtags', '') or '',
                'content_type': 'video',
                'url': getattr(post, 'url', ''),
                'engagement_score': getattr(post, 'likes', 0) + getattr(post, 'num_comments', 0) + getattr(post, 'views', 0)
            } for post in posts]
        except Exception as e:
            logger.error(f"Error fetching TikTok posts: {e}")
            return []

    def _get_instagram_comments(self, limit, start_date, end_date):
        """Get Instagram comments for sentiment analysis"""
        try:
            from instagram_data.models import InstagramComment

            queryset = InstagramComment.objects.all()
            if self.project:
                queryset = queryset.filter(folder__project=self.project)

            comments = queryset.filter(
                comment_date__gte=start_date,
                comment_date__lte=end_date
            ).order_by('-comment_date')[:limit]

            return [{
                'platform': 'instagram',
                'comment_id': comment.comment_id,
                'comment': comment.comment,
                'comment_user': comment.comment_user,
                'comment_date': comment.comment_date,
                'likes_number': comment.likes_number,
                'post_id': comment.post_id,
                'post_url': comment.post_url
            } for comment in comments]
        except Exception as e:
            logger.error(f"Error fetching Instagram comments: {e}")
            return []

    def _get_facebook_comments(self, limit, start_date, end_date):
        """Get Facebook comments for sentiment analysis"""
        try:
            from facebook_data.models import FacebookComment

            queryset = FacebookComment.objects.all()
            if self.project:
                queryset = queryset.filter(folder__project=self.project)

            comments = queryset.filter(
                comment_date__gte=start_date,
                comment_date__lte=end_date
            ).order_by('-comment_date')[:limit]

            return [{
                'platform': 'facebook',
                'comment_id': getattr(comment, 'comment_id', str(comment.id)),
                'comment': getattr(comment, 'comment', ''),
                'comment_user': getattr(comment, 'comment_user', ''),
                'comment_date': getattr(comment, 'comment_date', comment.created_at),
                'likes_number': getattr(comment, 'likes_number', 0),
                'post_id': getattr(comment, 'post_id', ''),
                'post_url': getattr(comment, 'post_url', '')
            } for comment in comments]
        except Exception as e:
            logger.error(f"Error fetching Facebook comments: {e}")
            return []

    def _get_linkedin_comments(self, limit, start_date, end_date):
        """Get LinkedIn comments for sentiment analysis"""
        try:
            from linkedin_data.models import LinkedInComment

            queryset = LinkedInComment.objects.all()
            if self.project:
                queryset = queryset.filter(folder__project=self.project)

            comments = queryset.filter(
                comment_date__gte=start_date,
                comment_date__lte=end_date
            ).order_by('-comment_date')[:limit]

            return [{
                'platform': 'linkedin',
                'comment_id': getattr(comment, 'comment_id', str(comment.id)),
                'comment': getattr(comment, 'comment', ''),
                'comment_user': getattr(comment, 'comment_user', ''),
                'comment_date': getattr(comment, 'comment_date', comment.created_at),
                'likes_number': getattr(comment, 'likes_number', 0),
                'post_id': getattr(comment, 'post_id', ''),
                'post_url': getattr(comment, 'post_url', '')
            } for comment in comments]
        except Exception as e:
            logger.error(f"Error fetching LinkedIn comments: {e}")
            return []

    def _get_tiktok_comments(self, limit, start_date, end_date):
        """Get TikTok comments for sentiment analysis"""
        try:
            from tiktok_data.models import TikTokComment

            queryset = TikTokComment.objects.all()
            if self.project:
                queryset = queryset.filter(folder__project=self.project)

            comments = queryset.filter(
                comment_date__gte=start_date,
                comment_date__lte=end_date
            ).order_by('-comment_date')[:limit]

            return [{
                'platform': 'tiktok',
                'comment_id': getattr(comment, 'comment_id', str(comment.id)),
                'comment': getattr(comment, 'comment', ''),
                'comment_user': getattr(comment, 'comment_user', ''),
                'comment_date': getattr(comment, 'comment_date', comment.created_at),
                'likes_number': getattr(comment, 'likes_number', 0),
                'post_id': getattr(comment, 'post_id', ''),
                'post_url': getattr(comment, 'post_url', '')
            } for comment in comments]
        except Exception as e:
            logger.error(f"Error fetching TikTok comments: {e}")
            return []

    def _get_instagram_metrics(self, start_date, end_date):
        """Get Instagram engagement metrics"""
        try:
            from instagram_data.models import InstagramPost

            queryset = InstagramPost.objects.all()
            if self.project:
                queryset = queryset.filter(folder__project=self.project)

            posts = queryset.filter(
                date_posted__gte=start_date,
                date_posted__lte=end_date
            )

            metrics = {
                'total_posts': posts.count(),
                'total_likes': sum(post.likes for post in posts),
                'total_comments': sum(post.num_comments for post in posts),
                'total_views': sum(post.views or 0 for post in posts),
                'avg_engagement': 0,
                'top_posts': []
            }

            if metrics['total_posts'] > 0:
                metrics['avg_engagement'] = (
                    metrics['total_likes'] + metrics['total_comments']
                ) / metrics['total_posts']

            # Get top performing posts
            top_posts = posts.order_by('-likes')[:5]
            metrics['top_posts'] = [{
                'title': f"Post by {post.user_posted}",
                'likes': post.likes,
                'comments': post.num_comments,
                'views': post.views or 0,
                'engagement_score': post.likes + post.num_comments,
                'platform': 'instagram'
            } for post in top_posts]

            return metrics
        except Exception as e:
            logger.error(f"Error fetching Instagram metrics: {e}")
            return {'total_posts': 0, 'total_likes': 0, 'total_comments': 0, 'total_views': 0, 'top_posts': []}

    def _get_facebook_metrics(self, start_date, end_date):
        """Get Facebook engagement metrics"""
        try:
            from facebook_data.models import FacebookPost

            queryset = FacebookPost.objects.all()
            if self.project:
                queryset = queryset.filter(folder__project=self.project)

            posts = queryset.filter(
                date_posted__gte=start_date,
                date_posted__lte=end_date
            )

            metrics = {
                'total_posts': posts.count(),
                'total_likes': sum(post.likes for post in posts),
                'total_comments': sum(post.num_comments for post in posts),
                'total_shares': sum(post.num_shares or 0 for post in posts),
                'avg_engagement': 0,
                'top_posts': []
            }

            if metrics['total_posts'] > 0:
                metrics['avg_engagement'] = (
                    metrics['total_likes'] + metrics['total_comments'] + metrics['total_shares']
                ) / metrics['total_posts']

            # Get top performing posts
            top_posts = posts.order_by('-likes')[:5]
            metrics['top_posts'] = [{
                'title': f"Post by {post.user_posted}",
                'likes': post.likes,
                'comments': post.num_comments,
                'shares': post.num_shares or 0,
                'engagement_score': post.likes + post.num_comments + (post.num_shares or 0),
                'platform': 'facebook'
            } for post in top_posts]

            return metrics
        except Exception as e:
            logger.error(f"Error fetching Facebook metrics: {e}")
            return {'total_posts': 0, 'total_likes': 0, 'total_comments': 0, 'total_shares': 0, 'top_posts': []}

    def _get_linkedin_metrics(self, start_date, end_date):
        """Get LinkedIn engagement metrics"""
        try:
            from linkedin_data.models import LinkedInPost

            queryset = LinkedInPost.objects.all()
            if self.project:
                queryset = queryset.filter(folder__project=self.project)

            posts = queryset.filter(
                date_posted__gte=start_date,
                date_posted__lte=end_date
            )

            metrics = {
                'total_posts': posts.count(),
                'total_likes': sum(getattr(post, 'likes', 0) for post in posts),
                'total_comments': sum(getattr(post, 'num_comments', 0) for post in posts),
                'total_shares': sum(getattr(post, 'num_shares', 0) for post in posts),
                'avg_engagement': 0,
                'top_posts': []
            }

            if metrics['total_posts'] > 0:
                metrics['avg_engagement'] = (
                    metrics['total_likes'] + metrics['total_comments'] + metrics['total_shares']
                ) / metrics['total_posts']

            # Get top performing posts
            top_posts = posts[:5]  # Simple ordering
            metrics['top_posts'] = [{
                'title': f"Post by {getattr(post, 'user_posted', 'User')}",
                'likes': getattr(post, 'likes', 0),
                'comments': getattr(post, 'num_comments', 0),
                'shares': getattr(post, 'num_shares', 0),
                'engagement_score': getattr(post, 'likes', 0) + getattr(post, 'num_comments', 0),
                'platform': 'linkedin'
            } for post in top_posts]

            return metrics
        except Exception as e:
            logger.error(f"Error fetching LinkedIn metrics: {e}")
            return {'total_posts': 0, 'total_likes': 0, 'total_comments': 0, 'total_shares': 0, 'top_posts': []}

    def _get_tiktok_metrics(self, start_date, end_date):
        """Get TikTok engagement metrics"""
        try:
            from tiktok_data.models import TikTokPost

            queryset = TikTokPost.objects.all()
            if self.project:
                queryset = queryset.filter(folder__project=self.project)

            posts = queryset.filter(
                date_posted__gte=start_date,
                date_posted__lte=end_date
            )

            metrics = {
                'total_posts': posts.count(),
                'total_likes': sum(getattr(post, 'likes', 0) for post in posts),
                'total_comments': sum(getattr(post, 'num_comments', 0) for post in posts),
                'total_views': sum(getattr(post, 'views', 0) for post in posts),
                'avg_engagement': 0,
                'top_posts': []
            }

            if metrics['total_posts'] > 0:
                metrics['avg_engagement'] = (
                    metrics['total_likes'] + metrics['total_comments']
                ) / metrics['total_posts']

            # Get top performing posts
            top_posts = posts[:5]  # Simple ordering
            metrics['top_posts'] = [{
                'title': f"Video by {getattr(post, 'user_posted', 'User')}",
                'likes': getattr(post, 'likes', 0),
                'comments': getattr(post, 'num_comments', 0),
                'views': getattr(post, 'views', 0),
                'engagement_score': getattr(post, 'likes', 0) + getattr(post, 'num_comments', 0) + getattr(post, 'views', 0),
                'platform': 'tiktok'
            } for post in top_posts]

            return metrics
        except Exception as e:
            logger.error(f"Error fetching TikTok metrics: {e}")
            return {'total_posts': 0, 'total_likes': 0, 'total_comments': 0, 'total_views': 0, 'top_posts': []}