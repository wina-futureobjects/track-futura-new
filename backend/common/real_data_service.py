"""
Real Data Service - Uses ONLY Apify scraped data
No fallback data, no mock data, only real scraped content
"""
import requests
import logging
from django.utils import timezone
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RealDataService:
    def __init__(self, project_id=None, batch_job_ids=None, folder_ids=None):
        self.project_id = project_id
        self.batch_job_ids = batch_job_ids or []
        self.folder_ids = folder_ids or []
        self.base_url = "http://localhost:8000"
        self.headers = {"Authorization": "Token ffc8a1106cfb2b3bb16d91158a1ebc00ae60a278"}

    def _get_batch_job_ids_from_folders(self):
        """Resolve folder IDs to batch job IDs"""
        batch_job_ids = []

        for folder_id in self.folder_ids:
            try:
                response = requests.get(
                    f"{self.base_url}/api/apify/batch-jobs/resolve_folder/?folder_id={folder_id}",
                    headers=self.headers,
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    batch_job_ids.append(data['batch_job_id'])
            except Exception as e:
                logger.warning(f"Failed to resolve folder {folder_id}: {e}")

        return batch_job_ids

    def _get_all_batch_job_ids(self):
        """Get all batch job IDs to fetch data from"""
        all_ids = list(self.batch_job_ids)

        # Add resolved folder IDs
        if self.folder_ids:
            all_ids.extend(self._get_batch_job_ids_from_folders())

        # If no IDs specified, get latest completed batch jobs
        if not all_ids:
            try:
                response = requests.get(
                    f"{self.base_url}/api/apify/batch-jobs/",
                    headers=self.headers,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    # Get latest 5 completed jobs
                    for job in data.get('results', [])[:5]:
                        if job.get('status') == 'completed':
                            all_ids.append(job['id'])
                            if len(all_ids) >= 5:
                                break
            except Exception as e:
                logger.error(f"Failed to get batch jobs: {e}")

        return all_ids

    def get_scraped_posts(self, limit=100):
        """Get ONLY real scraped posts from Apify - NO FALLBACK DATA"""
        try:
            batch_job_ids = self._get_all_batch_job_ids()

            if not batch_job_ids:
                logger.warning("No batch job IDs available for fetching data")
                return []

            real_posts = []

            # Fetch data from all specified batch jobs
            for batch_job_id in batch_job_ids:
                try:
                    response = requests.get(
                        f"{self.base_url}/api/apify/batch-jobs/{batch_job_id}/results/",
                        headers=self.headers,
                        timeout=10
                    )

                    if response.status_code != 200:
                        logger.warning(f"Failed to get data from batch job {batch_job_id}: {response.status_code}")
                        continue

                    data = response.json()

                    for result in data.get('results', []):
                        # Use ONLY the actual scraped data - no modifications
                        real_posts.append({
                            'id': result['id'],
                            'batch_job_id': batch_job_id,
                            'platform': result['platform'],
                            'content': result['description'],
                            'url': result['url'],
                            'user': result['user_posted'],
                            'likes': result['likes'],
                            'comments': result['num_comments'],
                            'views': result['views'],
                            'hashtags': result['hashtags'],
                            'date_posted': result['date_posted'],
                            'post_id': result['post_id'],
                            'content_type': result['content_type'],
                            'thumbnail': result['thumbnail'],
                            'followers': result['followers'],
                            'is_verified': result['is_verified'],
                            'shortcode': result['shortcode']
                        })

                        if len(real_posts) >= limit:
                            break

                    if len(real_posts) >= limit:
                        break

                except Exception as e:
                    logger.error(f"Error fetching from batch job {batch_job_id}: {e}")
                    continue

            return real_posts[:limit]

        except Exception as e:
            logger.error(f"Error fetching real scraped data: {e}")
            return []  # Return empty list - NO FALLBACK

    def get_real_engagement_metrics(self):
        """Calculate engagement metrics from ONLY real scraped data"""
        posts = self.get_scraped_posts()

        if not posts:
            return {}

        total_posts = len(posts)
        total_likes = sum(post['likes'] for post in posts)
        total_comments = sum(post['comments'] for post in posts)
        total_views = sum(post['views'] for post in posts)

        # Calculate averages using ONLY real data
        avg_likes = total_likes / total_posts if total_posts > 0 else 0
        avg_comments = total_comments / total_posts if total_posts > 0 else 0
        avg_views = total_views / total_posts if total_posts > 0 else 0

        # Calculate engagement rate from real data
        engagement_rate = ((total_likes + total_comments) / total_views * 100) if total_views > 0 else 0

        # Sort by actual engagement
        top_posts = sorted(posts, key=lambda x: x['likes'] + x['comments'], reverse=True)

        return {
            'total_posts': total_posts,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_views': total_views,
            'avg_likes_per_post': round(avg_likes, 1),
            'avg_comments_per_post': round(avg_comments, 1),
            'avg_views_per_post': round(avg_views, 1),
            'engagement_rate': round(engagement_rate, 2),
            'top_performing_posts': top_posts,
            'platform_breakdown': {
                'instagram': {
                    'posts': total_posts,
                    'likes': total_likes,
                    'comments': total_comments,
                    'views': total_views
                }
            },
            'data_source_count': total_posts
        }

    def get_real_content_analysis(self):
        """Analyze content using ONLY real scraped data"""
        posts = self.get_scraped_posts()

        if not posts:
            return {}

        # Content type breakdown from real data
        content_types = {}
        hashtag_performance = {}
        user_performance = {}

        for post in posts:
            # Real content type analysis
            content_type = post['content_type']
            if content_type not in content_types:
                content_types[content_type] = {'count': 0, 'total_likes': 0, 'total_comments': 0}

            content_types[content_type]['count'] += 1
            content_types[content_type]['total_likes'] += post['likes']
            content_types[content_type]['total_comments'] += post['comments']

            # Real hashtag analysis
            for hashtag in post['hashtags']:
                if hashtag not in hashtag_performance:
                    hashtag_performance[hashtag] = {'posts': 0, 'total_likes': 0, 'avg_likes': 0}

                hashtag_performance[hashtag]['posts'] += 1
                hashtag_performance[hashtag]['total_likes'] += post['likes']

            # Real user performance
            user = post['user']
            if user not in user_performance:
                user_performance[user] = {'posts': 0, 'total_likes': 0, 'total_followers': 0}

            user_performance[user]['posts'] += 1
            user_performance[user]['total_likes'] += post['likes']
            user_performance[user]['total_followers'] = max(
                user_performance[user]['total_followers'],
                post['followers']
            )

        # Calculate hashtag averages
        for hashtag in hashtag_performance:
            hashtag_performance[hashtag]['avg_likes'] = round(
                hashtag_performance[hashtag]['total_likes'] / hashtag_performance[hashtag]['posts'], 2
            )

        # Sort by real performance
        top_hashtags = sorted(
            hashtag_performance.items(),
            key=lambda x: x[1]['avg_likes'],
            reverse=True
        )

        top_users = sorted(
            user_performance.items(),
            key=lambda x: x[1]['total_likes'],
            reverse=True
        )

        return {
            'content_type_breakdown': content_types,
            'top_hashtags': [{'hashtag': k, **v} for k, v in top_hashtags],
            'top_performing_users': [{'user': k, **v} for k, v in top_users],
            'total_unique_hashtags': len(hashtag_performance),
            'total_content_creators': len(user_performance),
            'data_source_count': len(posts)
        }

    def get_real_visualization_data(self):
        """Generate visualization data from ONLY real scraped data"""
        posts = self.get_scraped_posts()

        if not posts:
            return {}

        # Real engagement trend data
        engagement_trend = []
        for i, post in enumerate(posts[:10]):
            engagement_trend.append({
                'day': i + 1,
                'engagement': post['likes'] + post['comments'],
                'likes': post['likes'],
                'comments': post['comments'],
                'views': post['views'],
                'content': post['content'][:50] + '...' if len(post['content']) > 50 else post['content']
            })

        # Real content performance breakdown
        content_performance = {}
        for post in posts:
            content_type = post['content_type']
            if content_type not in content_performance:
                content_performance[content_type] = {
                    'type': content_type,
                    'count': 0,
                    'total_likes': 0,
                    'total_comments': 0,
                    'avg_engagement': 0
                }

            content_performance[content_type]['count'] += 1
            content_performance[content_type]['total_likes'] += post['likes']
            content_performance[content_type]['total_comments'] += post['comments']

        # Calculate real averages
        for content_type in content_performance.values():
            if content_type['count'] > 0:
                content_type['avg_engagement'] = (content_type['total_likes'] + content_type['total_comments']) / content_type['count']

        return {
            'engagement_trend': engagement_trend,
            'content_performance_breakdown': list(content_performance.values()),
            'total_real_posts': len(posts)
        }

# Global service instance
real_data_service = RealDataService()