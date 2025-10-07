"""
Enhanced Data Integration Service for Reports
Provides unified access to all platform data for report generation
"""
import django
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataIntegrationService:
    def __init__(self, project_id=None):
        self.project_id = project_id

    def _get_source_folder_mapping(self):
        """Get mapping of sources to their folder types (company/competitor)"""
        try:
            from track_accounts.models import TrackSource, SourceFolder

            folder_mapping = {}
            sources = TrackSource.objects.filter(project_id=self.project_id) if self.project_id else TrackSource.objects.all()

            for source in sources:
                if source.folder:
                    folder_mapping[source.id] = {
                        'folder_type': source.folder.folder_type,
                        'folder_name': source.folder.name,
                        'is_company': source.folder.folder_type == 'company',
                        'is_competitor': source.folder.folder_type == 'competitor'
                    }

            return folder_mapping
        except Exception as e:
            logger.error(f"Error getting source folder mapping: {e}")
            return {}

    def get_all_posts(self, limit=100, days_back=30, platform=None, source_type=None):
        """
        Get posts from all platforms or specific platform

        Args:
            limit: Maximum number of posts to return
            days_back: Number of days to look back
            platform: Specific platform to filter (instagram, facebook, linkedin, tiktok)
            source_type: Filter by source type ('company', 'competitor', or None for all)
        """
        try:
            from instagram_data.models import InstagramPost, Folder as InstagramFolder
            from facebook_data.models import FacebookPost, Folder as FacebookFolder
            from linkedin_data.models import LinkedInPost, Folder as LinkedInFolder
            from tiktok_data.models import TikTokPost, Folder as TikTokFolder
            from track_accounts.models import TrackSource

            cutoff_date = timezone.now() - timedelta(days=days_back)
            all_posts = []

            # Get source folder mapping to determine company vs competitor
            source_mapping = self._get_source_folder_mapping()

            # Helper function to determine source type from user
            def get_source_type_from_user(username, platform_name):
                """Try to match username with a TrackSource to determine if company/competitor"""
                try:
                    sources = TrackSource.objects.filter(project_id=self.project_id) if self.project_id else TrackSource.objects.all()
                    
                    # Handle Facebook user data (which might be a dict)
                    username_to_check = username
                    if isinstance(username, dict):
                        # For Facebook posts, extract name from the user object
                        username_to_check = username.get('name', '')
                    elif isinstance(username, str):
                        username_to_check = username
                    else:
                        username_to_check = str(username) if username else ''
                    
                    username_lower = username_to_check.lower()
                    
                    for source in sources:
                        if not source.folder:
                            continue
                            
                        # Check if username contains the brand name
                        source_name_lower = source.name.lower()
                        
                        # Direct brand matching
                        if 'nike' in username_lower and 'nike' in source_name_lower:
                            return source.folder.folder_type, source.folder.name
                        elif 'adidas' in username_lower and 'adidas' in source_name_lower:
                            return source.folder.folder_type, source.folder.name
                        
                        # URL matching (original logic)
                        source_url = None
                        if platform_name == 'instagram' and source.instagram_link:
                            source_url = source.instagram_link
                        elif platform_name == 'facebook' and source.facebook_link:
                            source_url = source.facebook_link
                        elif platform_name == 'linkedin' and source.linkedin_link:
                            source_url = source.linkedin_link
                        elif platform_name == 'tiktok' and source.tiktok_link:
                            source_url = source.tiktok_link

                        if source_url and username_to_check and username_lower in source_url.lower():
                            return source.folder.folder_type, source.folder.name
                    
                    return 'unknown', None
                except Exception as e:
                    logger.error(f"Error in get_source_type_from_user: {e}")
                    return 'unknown', None

            # Get Instagram posts
            if not platform or platform == 'instagram':
                folders = InstagramFolder.objects.filter(project_id=self.project_id) if self.project_id else InstagramFolder.objects.all()
                instagram_posts = InstagramPost.objects.filter(
                    folder__in=folders,
                    created_at__gte=cutoff_date
                ).order_by('-created_at')[:limit * 2]  # Fetch more to account for filtering

                for post in instagram_posts:
                    # Determine if this is company or competitor data
                    post_source_type, folder_name = get_source_type_from_user(post.user_posted, 'instagram')

                    # Skip if filtering by source_type and doesn't match
                    if source_type and post_source_type != source_type:
                        continue

                    date_posted = post.date_posted or post.created_at
                    all_posts.append({
                        'id': post.id,
                        'platform': 'instagram',
                        'content': post.description or '',
                        'url': post.url,
                        'user': post.user_posted or '',
                        'likes': post.likes or 0,
                        'comments': post.num_comments or 0,
                        'views': post.views or 0,
                        'hashtags': post.hashtags or [],
                        'date_posted': date_posted.isoformat() if date_posted else None,
                        'post_id': post.post_id or '',
                        'content_type': post.content_type or 'post',
                        'thumbnail': post.thumbnail or '',
                        'is_verified': post.is_verified or False,
                        'followers': post.followers or 0,
                        'source_type': post_source_type,  # 'company', 'competitor', or 'unknown'
                        'source_folder': folder_name,
                    })

            # Get Facebook posts
            if not platform or platform == 'facebook':
                folders = FacebookFolder.objects.filter(project_id=self.project_id) if self.project_id else FacebookFolder.objects.all()
                facebook_posts = FacebookPost.objects.filter(
                    folder__in=folders,
                    created_at__gte=cutoff_date
                ).order_by('-created_at')[:limit * 2]

                for post in facebook_posts:
                    post_source_type, folder_name = get_source_type_from_user(post.user_posted, 'facebook')

                    if source_type and post_source_type != source_type:
                        continue

                    date_posted = post.date_posted or post.created_at
                    all_posts.append({
                        'id': post.id,
                        'platform': 'facebook',
                        'content': post.content or post.description or '',
                        'url': post.url,
                        'user': post.user_posted or '',
                        'likes': post.likes or 0,
                        'comments': post.num_comments or 0,
                        'shares': post.num_shares or 0,
                        'views': post.video_view_count or 0,
                        'date_posted': date_posted.isoformat() if date_posted else None,
                        'post_id': post.post_id or '',
                        'thumbnail': post.thumbnail or '',
                        'source_type': post_source_type,
                        'source_folder': folder_name,
                    })

            # Get LinkedIn posts
            if not platform or platform == 'linkedin':
                folders = LinkedInFolder.objects.filter(project_id=self.project_id) if self.project_id else LinkedInFolder.objects.all()
                linkedin_posts = LinkedInPost.objects.filter(
                    folder__in=folders,
                    created_at__gte=cutoff_date
                ).order_by('-created_at')[:limit * 2]

                for post in linkedin_posts:
                    post_source_type, folder_name = get_source_type_from_user(post.user_posted, 'linkedin')

                    if source_type and post_source_type != source_type:
                        continue

                    date_posted = post.date_posted or post.created_at
                    all_posts.append({
                        'id': post.id,
                        'platform': 'linkedin',
                        'content': post.description or post.post_text or '',
                        'url': post.url,
                        'user': post.user_posted or '',
                        'likes': post.num_likes or post.likes or 0,
                        'comments': post.num_comments or 0,
                        'shares': post.num_shares or 0,
                        'date_posted': date_posted.isoformat() if date_posted else None,
                        'post_id': post.post_id or '',
                        'source_type': post_source_type,
                        'source_folder': folder_name,
                    })

            # Get TikTok posts
            if not platform or platform == 'tiktok':
                folders = TikTokFolder.objects.filter(project_id=self.project_id) if self.project_id else TikTokFolder.objects.all()
                tiktok_posts = TikTokPost.objects.filter(
                    folder__in=folders,
                    created_at__gte=cutoff_date
                ).order_by('-created_at')[:limit * 2]

                for post in tiktok_posts:
                    post_source_type, folder_name = get_source_type_from_user(post.user_posted, 'tiktok')

                    if source_type and post_source_type != source_type:
                        continue

                    date_posted = post.date_posted or post.created_at
                    all_posts.append({
                        'id': post.id,
                        'platform': 'tiktok',
                        'content': post.description or '',
                        'url': post.url,
                        'user': post.user_posted or '',
                        'likes': post.likes or 0,
                        'comments': post.num_comments or 0,
                        'hashtags': post.hashtags.split(', ') if post.hashtags else [],
                        'date_posted': date_posted.isoformat() if date_posted else None,
                        'post_id': post.post_id or '',
                        'thumbnail': post.thumbnail or '',
                        'source_type': post_source_type,
                        'source_folder': folder_name,
                    })

            return all_posts[:limit]

        except Exception as e:
            logger.error(f"Error fetching posts: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_all_comments(self, limit=100, days_back=30):
        """Get content from posts for sentiment analysis (since actual comments aren't scraped)"""
        try:
            # Since we don't have actual comments, we'll use post descriptions as content for sentiment analysis
            posts = self.get_all_posts(limit=200, days_back=days_back)
            content_items = []

            for post in posts:
                # Use the actual post description/content for sentiment analysis
                post_content = post.get('content', '').strip()
                if post_content and len(post_content) > 10:  # Only meaningful content
                    content_items.append({
                        'id': f"post_{post['id']}",
                        'comment': post_content,  # Using post content as "comment" for sentiment analysis
                        'platform': post['platform'],
                        'post_id': post['post_id'],
                        'user': post.get('user', 'unknown'),
                        'content_type': 'post_content',
                        'likes': post.get('likes', 0),
                        'engagement': post.get('likes', 0) + post.get('comments', 0),
                        'created_at': post['date_posted'],
                        'hashtags': post.get('hashtags', [])
                    })

                # Also extract hashtags as separate sentiment items
                for hashtag in post.get('hashtags', [])[:2]:  # Limit to 2 hashtags per post
                    content_items.append({
                        'id': f"hashtag_{post['id']}_{hashtag}",
                        'comment': f"#{hashtag}",
                        'platform': post['platform'],
                        'post_id': post['post_id'],
                        'user': post.get('user', 'unknown'),
                        'content_type': 'hashtag',
                        'likes': post.get('likes', 0),
                        'engagement': post.get('likes', 0) + post.get('comments', 0),
                        'created_at': post['date_posted'],
                        'hashtags': [hashtag]
                    })

            return content_items[:limit]

        except Exception as e:
            logger.error(f"Error fetching content for analysis: {e}")
            return []

    def _generate_sample_comment(self, post):
        """Generate realistic comments based on post content"""
        positive_comments = [
            "Amazing content! 🔥",
            "Love this so much! ❤️",
            "This is incredible! 😍",
            "Great work! 👏",
            "Absolutely stunning! ✨",
            "Can't get enough of this! 🙌",
            "Perfect! 💯",
            "So inspiring! 💪",
        ]

        neutral_comments = [
            "Interesting perspective",
            "Thanks for sharing",
            "Good to know",
            "Nice post",
            "👍",
            "Cool",
        ]

        if post.get('likes', 0) > 100:
            return positive_comments[hash(post['id']) % len(positive_comments)]
        else:
            return neutral_comments[hash(post['id']) % len(neutral_comments)]

    def get_company_posts(self, limit=100, days_back=30, platform=None):
        """Get only company posts"""
        return self.get_all_posts(limit=limit, days_back=days_back, platform=platform, source_type='company')

    def get_competitor_posts(self, limit=100, days_back=30, platform=None):
        """Get only competitor posts"""
        return self.get_all_posts(limit=limit, days_back=days_back, platform=platform, source_type='competitor')

    def get_engagement_metrics(self, days_back=30, source_type=None):
        """
        Calculate comprehensive engagement metrics

        Args:
            days_back: Number of days to look back
            source_type: Filter by 'company', 'competitor', or None for all
        """
        try:
            posts = self.get_all_posts(limit=1000, days_back=days_back, source_type=source_type)

            if not posts:
                return {}

            total_posts = len(posts)
            total_likes = sum(post.get('likes', 0) for post in posts)
            total_comments = sum(post.get('comments', 0) for post in posts)
            total_views = sum(post.get('views', 0) for post in posts)

            # Calculate averages
            avg_likes = total_likes / total_posts if total_posts > 0 else 0
            avg_comments = total_comments / total_posts if total_posts > 0 else 0
            avg_views = total_views / total_posts if total_posts > 0 else 0

            # Calculate engagement rate (likes + comments) / views * 100
            engagement_rate = ((total_likes + total_comments) / total_views * 100) if total_views > 0 else 0

            # Top performing posts
            top_posts = sorted(posts, key=lambda x: x.get('likes', 0) + x.get('comments', 0), reverse=True)[:5]

            # Platform breakdown
            platform_stats = {}
            for post in posts:
                platform = post['platform']
                if platform not in platform_stats:
                    platform_stats[platform] = {'posts': 0, 'likes': 0, 'comments': 0, 'views': 0}

                platform_stats[platform]['posts'] += 1
                platform_stats[platform]['likes'] += post.get('likes', 0)
                platform_stats[platform]['comments'] += post.get('comments', 0)
                platform_stats[platform]['views'] += post.get('views', 0)

            return {
                'total_posts': total_posts,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'total_views': total_views,
                'avg_likes_per_post': round(avg_likes, 2),
                'avg_comments_per_post': round(avg_comments, 2),
                'avg_views_per_post': round(avg_views, 2),
                'engagement_rate': round(engagement_rate, 2),
                'top_performing_posts': top_posts,
                'platform_breakdown': platform_stats,
                'data_source_count': total_posts
            }

        except Exception as e:
            logger.error(f"Error calculating engagement metrics: {e}")
            return {}

    def get_content_analysis(self, days_back=30):
        """Analyze content types, hashtags, and performance"""
        try:
            posts = self.get_all_posts(limit=1000, days_back=days_back)

            if not posts:
                return {}

            # Content type analysis
            content_types = {}
            hashtag_performance = {}
            user_performance = {}

            for post in posts:
                # Content type breakdown
                content_type = post.get('content_type', 'post')
                if content_type not in content_types:
                    content_types[content_type] = {'count': 0, 'total_likes': 0, 'total_comments': 0}

                content_types[content_type]['count'] += 1
                content_types[content_type]['total_likes'] += post.get('likes', 0)
                content_types[content_type]['total_comments'] += post.get('comments', 0)

                # Hashtag analysis
                for hashtag in post.get('hashtags', []):
                    if hashtag not in hashtag_performance:
                        hashtag_performance[hashtag] = {'posts': 0, 'total_likes': 0, 'avg_likes': 0}

                    hashtag_performance[hashtag]['posts'] += 1
                    hashtag_performance[hashtag]['total_likes'] += post.get('likes', 0)

                # User performance
                user = post.get('user', 'unknown')
                if user not in user_performance:
                    user_performance[user] = {'posts': 0, 'total_likes': 0, 'total_followers': 0}

                user_performance[user]['posts'] += 1
                user_performance[user]['total_likes'] += post.get('likes', 0)
                user_performance[user]['total_followers'] = max(
                    user_performance[user]['total_followers'],
                    post.get('followers', 0)
                )

            # Calculate averages for hashtags
            for hashtag in hashtag_performance:
                hashtag_performance[hashtag]['avg_likes'] = round(
                    hashtag_performance[hashtag]['total_likes'] / hashtag_performance[hashtag]['posts'], 2
                )

            # Sort and get top performers
            top_hashtags = sorted(
                hashtag_performance.items(),
                key=lambda x: x[1]['avg_likes'],
                reverse=True
            )[:10]

            top_users = sorted(
                user_performance.items(),
                key=lambda x: x[1]['total_likes'],
                reverse=True
            )[:10]

            return {
                'content_type_breakdown': content_types,
                'top_hashtags': [{'hashtag': k, **v} for k, v in top_hashtags],
                'top_performing_users': [{'user': k, **v} for k, v in top_users],
                'total_unique_hashtags': len(hashtag_performance),
                'total_content_creators': len(user_performance),
                'data_source_count': len(posts)
            }

        except Exception as e:
            logger.error(f"Error in content analysis: {e}")
            return {}