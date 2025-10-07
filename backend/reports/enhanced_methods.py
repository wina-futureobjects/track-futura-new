"""
Enhanced report processing methods for all templates
Add these methods to GeneratedReportViewSet class in views.py
"""

import time
import logging
from django.utils import timezone
from datetime import datetime, timedelta
from collections import Counter

logger = logging.getLogger(__name__)


def _process_engagement_metrics_ENHANCED(self, report, project_id=None):
    """Enhanced engagement metrics with deep analytics and visualizations"""
    start_time = time.time()

    from instagram_data.models import InstagramPost, Folder as InstagramFolder
    from facebook_data.models import FacebookPost, Folder as FacebookFolder
    from tiktok_data.models import TikTokPost, Folder as TikTokFolder
    from linkedin_data.models import LinkedInPost, Folder as LinkedInFolder

    config = report.configuration or {}
    batch_job_ids = config.get('batch_job_ids', [])
    folder_ids = config.get('folder_ids', [])

    # Get posts directly from database
    posts = []

    # Get from folders if specified
    if folder_ids:
        for folder_id in folder_ids:
            for Folder in [InstagramFolder, FacebookFolder, TikTokFolder, LinkedInFolder]:
                try:
                    folder = Folder.objects.get(id=folder_id)
                    platform = 'instagram' if Folder == InstagramFolder else \
                              'facebook' if Folder == FacebookFolder else \
                              'tiktok' if Folder == TikTokFolder else 'linkedin'

                    for post in folder.posts.all()[:50]:
                        posts.append({
                            'id': post.id,
                            'platform': platform,
                            'content': post.description or '',
                            'user': post.user_posted or 'unknown',
                            'likes': post.likes or 0,
                            'comments': post.num_comments or 0,
                            'views': post.views or 0,
                            'date_posted': str(post.date_posted) if hasattr(post, 'date_posted') else '',
                            'content_type': post.content_type if hasattr(post, 'content_type') else 'post',
                            'post_id': post.post_id if hasattr(post, 'post_id') else str(post.id)
                        })
                except:
                    continue

    # If no folders, get recent posts
    if not posts:
        for Post in [InstagramPost, FacebookPost, TikTokPost, LinkedInPost]:
            platform = 'instagram' if Post == InstagramPost else \
                      'facebook' if Post == FacebookPost else \
                      'tiktok' if Post == TikTokPost else 'linkedin'

            for post in Post.objects.all()[:50]:
                posts.append({
                    'id': post.id,
                    'platform': platform,
                    'content': post.description or '',
                    'user': post.user_posted or 'unknown',
                    'likes': post.likes or 0,
                    'comments': post.num_comments or 0,
                    'views': post.views or 0,
                    'date_posted': str(post.date_posted) if hasattr(post, 'date_posted') else '',
                    'content_type': post.content_type if hasattr(post, 'content_type') else 'post',
                    'post_id': post.post_id if hasattr(post, 'post_id') else str(post.id)
                })

    if not posts:
        return {
            'error': 'No data available',
            'data_source_count': 0
        }

    # Calculate comprehensive engagement metrics
    total_posts = len(posts)
    total_likes = sum(p.get('likes', 0) for p in posts)
    total_comments = sum(p.get('comments', 0) for p in posts)
    total_views = sum(p.get('views', 0) for p in posts)

    avg_likes = round(total_likes / total_posts) if total_posts > 0 else 0
    avg_comments = round(total_comments / total_posts) if total_posts > 0 else 0
    avg_views = round(total_views / total_posts) if total_posts > 0 else 0

    engagement_rate = round((total_likes + total_comments) / max(total_views, 1) * 100, 2)

    # Find top performing posts
    top_posts = sorted(posts, key=lambda x: x.get('likes', 0) + x.get('comments', 0) * 2, reverse=True)[:10]

    # Platform breakdown
    platform_metrics = {}
    for post in posts:
        platform = post.get('platform', 'unknown')
        if platform not in platform_metrics:
            platform_metrics[platform] = {
                'posts': 0,
                'likes': 0,
                'comments': 0,
                'views': 0
            }
        platform_metrics[platform]['posts'] += 1
        platform_metrics[platform]['likes'] += post.get('likes', 0)
        platform_metrics[platform]['comments'] += post.get('comments', 0)
        platform_metrics[platform]['views'] += post.get('views', 0)

    # Visualization: Line chart for engagement over time
    engagement_trend = []
    for i, post in enumerate(sorted(posts, key=lambda x: x.get('date_posted', ''))[:30]):
        engagement_trend.append({
            'index': i + 1,
            'likes': post.get('likes', 0),
            'comments': post.get('comments', 0),
            'total_engagement': post.get('likes', 0) + post.get('comments', 0)
        })

    # Visualization: Bar chart for platform comparison
    platform_chart = {
        'labels': list(platform_metrics.keys()),
        'datasets': [
            {
                'label': 'Total Likes',
                'data': [platform_metrics[p]['likes'] for p in platform_metrics],
                'backgroundColor': '#2196F3'
            },
            {
                'label': 'Total Comments',
                'data': [platform_metrics[p]['comments'] for p in platform_metrics],
                'backgroundColor': '#4CAF50'
            }
        ]
    }

    # Generate insights
    insights = []
    insights.append(f"📊 Analyzed {total_posts:,} posts with {total_likes:,} total likes and {total_comments:,} comments")
    insights.append(f"💡 Average engagement rate: {engagement_rate}% across all platforms")

    if engagement_rate > 5:
        insights.append(f"🎉 Excellent engagement! Rate is above industry average")
    elif engagement_rate < 2:
        insights.append(f"📈 Engagement rate could be improved. Consider more interactive content")

    best_platform = max(platform_metrics.items(), key=lambda x: x[1]['likes'] + x[1]['comments'])
    insights.append(f"🏆 Best performing platform: {best_platform[0].title()} with {best_platform[1]['likes']:,} likes")

    processing_time = time.time() - start_time

    return {
        'report_type': 'engagement_metrics',
        'title': 'Engagement Metrics Report',
        'summary': f"Comprehensive analysis of {total_posts} posts across {len(platform_metrics)} platforms",
        'total_posts': total_posts,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'total_views': total_views,
        'avg_likes_per_post': avg_likes,
        'avg_comments_per_post': avg_comments,
        'avg_views_per_post': avg_views,
        'engagement_rate': engagement_rate,
        'platform_breakdown': platform_metrics,
        'top_performing_posts': top_posts[:10],
        'insights': insights,
        'visualizations': {
            'engagement_trend': {
                'type': 'line',
                'title': 'Engagement Trend',
                'data': {
                    'labels': [e['index'] for e in engagement_trend],
                    'datasets': [
                        {
                            'label': 'Total Engagement',
                            'data': [e['total_engagement'] for e in engagement_trend],
                            'borderColor': '#2196F3',
                            'fill': False
                        }
                    ]
                }
            },
            'platform_comparison': {
                'type': 'bar',
                'title': 'Platform Performance',
                'data': platform_chart
            }
        },
        'data_source_count': total_posts,
        'processing_time': round(processing_time, 2),
        'generated_at': timezone.now().isoformat()
    }


def _process_content_analysis_ENHANCED(self, report, project_id=None):
    """Enhanced content analysis with AI-powered insights"""
    start_time = time.time()

    from instagram_data.models import InstagramPost, Folder as InstagramFolder
    from facebook_data.models import FacebookPost, Folder as FacebookFolder
    from tiktok_data.models import TikTokPost, Folder as TikTokFolder
    from linkedin_data.models import LinkedInPost, Folder as LinkedInFolder

    config = report.configuration or {}
    folder_ids = config.get('folder_ids', [])

    # Get posts directly from database
    posts = []

    if folder_ids:
        for folder_id in folder_ids:
            for Folder in [InstagramFolder, FacebookFolder, TikTokFolder, LinkedInFolder]:
                try:
                    folder = Folder.objects.get(id=folder_id)
                    for post in folder.posts.all()[:50]:
                        hashtags = []
                        if hasattr(post, 'hashtags') and post.hashtags:
                            if isinstance(post.hashtags, list):
                                hashtags = post.hashtags
                            elif isinstance(post.hashtags, str):
                                hashtags = [h.strip() for h in post.hashtags.split(',') if h.strip()]

                        posts.append({
                            'id': post.id,
                            'content': post.description or '',
                            'content_type': post.content_type if hasattr(post, 'content_type') else 'post',
                            'hashtags': hashtags
                        })
                except:
                    continue

    if not posts:
        for Post in [InstagramPost, FacebookPost, TikTokPost, LinkedInPost]:
            for post in Post.objects.all()[:50]:
                hashtags = []
                if hasattr(post, 'hashtags') and post.hashtags:
                    if isinstance(post.hashtags, list):
                        hashtags = post.hashtags
                    elif isinstance(post.hashtags, str):
                        hashtags = [h.strip() for h in post.hashtags.split(',') if h.strip()]

                posts.append({
                    'id': post.id,
                    'content': post.description or '',
                    'content_type': post.content_type if hasattr(post, 'content_type') else 'post',
                    'hashtags': hashtags
                })

    if not posts:
        return {'error': 'No data available', 'data_source_count': 0}

    # Content type analysis
    content_types = Counter(p.get('content_type', 'unknown') for p in posts)

    # Hashtag analysis
    all_hashtags = []
    for post in posts:
        hashtags = post.get('hashtags', [])
        if isinstance(hashtags, list):
            all_hashtags.extend(hashtags)
        elif isinstance(hashtags, str):
            all_hashtags.extend(hashtags.split(','))

    top_hashtags = Counter(all_hashtags).most_common(20)

    # Content length analysis
    content_lengths = [len(p.get('content', '')) for p in posts if p.get('content')]
    avg_content_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0

    # Visualization: Pie chart for content types
    content_type_chart = {
        'labels': list(content_types.keys()),
        'values': list(content_types.values()),
        'colors': ['#2196F3', '#4CAF50', '#FF9800', '#F44336']
    }

    # Visualization: Bar chart for top hashtags
    hashtag_chart = {
        'labels': [h[0] for h in top_hashtags[:10]],
        'datasets': [
            {
                'label': 'Usage Count',
                'data': [h[1] for h in top_hashtags[:10]],
                'backgroundColor': '#9C27B0'
            }
        ]
    }

    insights = []
    insights.append(f"📝 Analyzed {len(posts)} posts with {len(set(all_hashtags))} unique hashtags")
    insights.append(f"📏 Average content length: {round(avg_content_length)} characters")

    most_common_type = content_types.most_common(1)[0] if content_types else ('Unknown', 0)
    insights.append(f"🎬 Most common content type: {most_common_type[0]} ({most_common_type[1]} posts)")

    if top_hashtags:
        insights.append(f"#️⃣ Top hashtag: #{top_hashtags[0][0]} used {top_hashtags[0][1]} times")

    processing_time = time.time() - start_time

    return {
        'report_type': 'content_analysis',
        'title': 'Content Analysis Report',
        'summary': f"In-depth analysis of content strategies across {len(posts)} posts",
        'total_posts': len(posts),
        'content_type_breakdown': dict(content_types),
        'top_hashtags': top_hashtags,
        'avg_content_length': round(avg_content_length),
        'unique_hashtags': len(set(all_hashtags)),
        'insights': insights,
        'visualizations': {
            'content_types': {
                'type': 'pie',
                'title': 'Content Type Distribution',
                'data': content_type_chart
            },
            'top_hashtags': {
                'type': 'bar',
                'title': 'Most Used Hashtags',
                'data': hashtag_chart
            }
        },
        'data_source_count': len(posts),
        'processing_time': round(processing_time, 2),
        'generated_at': timezone.now().isoformat()
    }


def _process_trend_analysis_ENHANCED(self, report, project_id=None):
    """Enhanced trend analysis with predictive insights"""
    start_time = time.time()

    from instagram_data.models import InstagramPost, Folder as InstagramFolder
    from facebook_data.models import FacebookPost, Folder as FacebookFolder
    from tiktok_data.models import TikTokPost, Folder as TikTokFolder
    from linkedin_data.models import LinkedInPost, Folder as LinkedInFolder

    config = report.configuration or {}
    folder_ids = config.get('folder_ids', [])

    # Get posts directly from database
    posts = []

    if folder_ids:
        for folder_id in folder_ids:
            for Folder in [InstagramFolder, FacebookFolder, TikTokFolder, LinkedInFolder]:
                try:
                    folder = Folder.objects.get(id=folder_id)
                    for post in folder.posts.all()[:50]:
                        posts.append({
                            'id': post.id,
                            'likes': post.likes or 0,
                            'comments': post.num_comments or 0,
                            'date_posted': str(post.date_posted) if hasattr(post, 'date_posted') else ''
                        })
                except:
                    continue

    if not posts:
        for Post in [InstagramPost, FacebookPost, TikTokPost, LinkedInPost]:
            for post in Post.objects.all()[:50]:
                posts.append({
                    'id': post.id,
                    'likes': post.likes or 0,
                    'comments': post.num_comments or 0,
                    'date_posted': str(post.date_posted) if hasattr(post, 'date_posted') else ''
                })

    if not posts:
        return {'error': 'No data available', 'data_source_count': 0}

    # Sort posts by date
    sorted_posts = sorted(posts, key=lambda x: x.get('date_posted', ''))

    # Calculate engagement trends
    trend_data = []
    window_size = max(1, len(sorted_posts) // 10)

    for i in range(0, len(sorted_posts), window_size):
        window = sorted_posts[i:i + window_size]
        avg_likes = sum(p.get('likes', 0) for p in window) / len(window) if window else 0
        avg_comments = sum(p.get('comments', 0) for p in window) / len(window) if window else 0

        trend_data.append({
            'period': f"Period {i//window_size + 1}",
            'avg_likes': round(avg_likes),
            'avg_comments': round(avg_comments),
            'post_count': len(window)
        })

    # Calculate growth rate
    if len(trend_data) >= 2:
        first_period = trend_data[0]['avg_likes'] + trend_data[0]['avg_comments']
        last_period = trend_data[-1]['avg_likes'] + trend_data[-1]['avg_comments']
        growth_rate = ((last_period - first_period) / max(first_period, 1)) * 100
    else:
        growth_rate = 0

    # Visualization: Line chart for trends
    trend_chart = {
        'labels': [t['period'] for t in trend_data],
        'datasets': [
            {
                'label': 'Avg Likes',
                'data': [t['avg_likes'] for t in trend_data],
                'borderColor': '#2196F3',
                'fill': False
            },
            {
                'label': 'Avg Comments',
                'data': [t['avg_comments'] for t in trend_data],
                'borderColor': '#4CAF50',
                'fill': False
            }
        ]
    }

    insights = []
    insights.append(f"📈 Analyzed trends across {len(posts)} posts over {len(trend_data)} periods")
    insights.append(f"{'📊 Growth:' if growth_rate >= 0 else '📉 Decline:'} {abs(growth_rate):.1f}% in engagement")

    if growth_rate > 20:
        insights.append(f"🚀 Strong upward trend! Keep up the momentum")
    elif growth_rate < -20:
        insights.append(f"⚠️ Declining engagement. Consider refreshing content strategy")
    else:
        insights.append(f"➡️ Stable engagement trends")

    processing_time = time.time() - start_time

    return {
        'report_type': 'trend_analysis',
        'title': 'Trend Analysis Report',
        'summary': f"Trend analysis across {len(trend_data)} time periods",
        'total_posts': len(posts),
        'growth_rate': round(growth_rate, 2),
        'trend_data': trend_data,
        'insights': insights,
        'visualizations': {
            'engagement_trends': {
                'type': 'line',
                'title': 'Engagement Trends Over Time',
                'data': trend_chart
            }
        },
        'data_source_count': len(posts),
        'processing_time': round(processing_time, 2),
        'generated_at': timezone.now().isoformat()
    }


def _process_user_behavior_ENHANCED(self, report, project_id=None):
    """Enhanced user behavior analysis with pattern detection"""
    start_time = time.time()

    from instagram_data.models import InstagramPost, Folder as InstagramFolder
    from facebook_data.models import FacebookPost, Folder as FacebookFolder
    from tiktok_data.models import TikTokPost, Folder as TikTokFolder
    from linkedin_data.models import LinkedInPost, Folder as LinkedInFolder

    config = report.configuration or {}
    folder_ids = config.get('folder_ids', [])

    # Get posts directly from database
    posts = []

    if folder_ids:
        for folder_id in folder_ids:
            for Folder in [InstagramFolder, FacebookFolder, TikTokFolder, LinkedInFolder]:
                try:
                    folder = Folder.objects.get(id=folder_id)
                    for post in folder.posts.all()[:50]:
                        posts.append({
                            'id': post.id,
                            'user': post.user_posted or 'unknown',
                            'likes': post.likes or 0,
                            'comments': post.num_comments or 0
                        })
                except:
                    continue

    if not posts:
        for Post in [InstagramPost, FacebookPost, TikTokPost, LinkedInPost]:
            for post in Post.objects.all()[:50]:
                posts.append({
                    'id': post.id,
                    'user': post.user_posted or 'unknown',
                    'likes': post.likes or 0,
                    'comments': post.num_comments or 0
                })

    if not posts:
        return {'error': 'No data available', 'data_source_count': 0}

    # Analyze user engagement patterns
    user_engagement = {}
    for post in posts:
        user = post.get('user', 'Unknown')
        if user not in user_engagement:
            user_engagement[user] = {
                'posts': 0,
                'total_likes': 0,
                'total_comments': 0,
                'avg_engagement': 0
            }

        user_engagement[user]['posts'] += 1
        user_engagement[user]['total_likes'] += post.get('likes', 0)
        user_engagement[user]['total_comments'] += post.get('comments', 0)

    # Calculate averages
    for user, data in user_engagement.items():
        data['avg_engagement'] = round((data['total_likes'] + data['total_comments']) / data['posts']) if data['posts'] > 0 else 0

    # Sort by engagement
    top_users = sorted(user_engagement.items(), key=lambda x: x[1]['avg_engagement'], reverse=True)[:10]

    # Visualization: Bar chart for top users
    user_chart = {
        'labels': [u[0] for u in top_users],
        'datasets': [
            {
                'label': 'Avg Engagement',
                'data': [u[1]['avg_engagement'] for u in top_users],
                'backgroundColor': '#673AB7'
            }
        ]
    }

    insights = []
    insights.append(f"👥 Analyzed behavior of {len(user_engagement)} unique users")
    insights.append(f"🏆 Top user: {top_users[0][0]} with {top_users[0][1]['avg_engagement']:,} avg engagement")

    total_posts = sum(u[1]['posts'] for u in top_users)
    insights.append(f"📊 Top 10 users account for {total_posts} posts")

    processing_time = time.time() - start_time

    return {
        'report_type': 'user_behavior',
        'title': 'User Behavior Analysis Report',
        'summary': f"Behavior patterns of {len(user_engagement)} users",
        'total_users': len(user_engagement),
        'total_posts': len(posts),
        'top_users': [{'user': u[0], **u[1]} for u in top_users],
        'insights': insights,
        'visualizations': {
            'top_users': {
                'type': 'bar',
                'title': 'Top Users by Engagement',
                'data': user_chart
            }
        },
        'data_source_count': len(posts),
        'processing_time': round(processing_time, 2),
        'generated_at': timezone.now().isoformat()
    }
