#!/usr/bin/env python3
"""
EMERGENCY PRODUCTION FIX: Replace sample data generation with real data prioritization
This script directly fixes the production brightdata_job_results view
"""

production_fix_code = '''
@csrf_exempt
@require_http_methods(["GET"])
def brightdata_job_results(request, job_folder_id):
    """
    Fetch BrightData results for a specific job folder and link them to the job
    FIXED: Now prioritizes real scraped data over sample data
    """
    try:
        # Get the job folder
        from track_accounts.models import ReportFolder
        from .models import BrightDataScrapedPost, BrightDataScraperRequest
        
        try:
            job_folder = ReportFolder.objects.get(id=job_folder_id)
        except ReportFolder.DoesNotExist:
            return JsonResponse({
                'success': False,
                'job_folder_id': job_folder_id,
                'error': f'Job folder {job_folder_id} not found'
            }, status=404)

        # 🚀 PRIORITY 1: Check for REAL scraped data FIRST
        existing_scraped_posts = BrightDataScrapedPost.objects.filter(
            folder_id=job_folder_id
        ).exclude(
            post_id__startswith='sample_post_'  # Exclude old sample data
        ).order_by('-date_posted', '-created_at')

        if existing_scraped_posts.exists():
            logger.info(f"✅ Found {existing_scraped_posts.count()} real scraped posts for folder {job_folder_id}")
            
            # Return real scraped data immediately - NO SAMPLE DATA
            posts_data = []
            for post in existing_scraped_posts:
                posts_data.append({
                    'post_id': post.post_id,
                    'url': post.url,
                    'user_username': post.user_posted,
                    'username': post.user_posted,
                    'caption': post.content,
                    'description': post.description,
                    'likes_count': post.likes,
                    'likesCount': post.likes,
                    'comments_count': post.num_comments,
                    'commentsCount': post.num_comments,
                    'shares_count': post.shares,
                    'timestamp': post.date_posted.isoformat() if post.date_posted else post.created_at.isoformat(),
                    'date_posted': post.date_posted.isoformat() if post.date_posted else post.created_at.isoformat(),
                    'is_verified': post.is_verified,
                    'platform': post.platform,
                    'media_type': post.media_type,
                    'media_url': post.media_url,
                    'location': post.location,
                    'hashtags': post.hashtags,
                    'mentions': post.mentions,
                })
            
            return JsonResponse({
                'success': True,
                'job_folder_id': job_folder_id,
                'job_folder_name': job_folder.name,
                'total_results': len(posts_data),
                'data': posts_data,
                'posts': posts_data,  # Also include as 'posts' for compatibility
                'source': 'real_brightdata_scraped_data',
                'message': f'Showing {len(posts_data)} real scraped posts from BrightData'
            })

        # If no real scraped data, return empty result - NO MORE SAMPLE DATA GENERATION
        return JsonResponse({
            'success': True,
            'job_folder_id': job_folder_id,
            'job_folder_name': job_folder.name,
            'total_results': 0,
            'data': [],
            'posts': [],
            'source': 'no_data_available',
            'message': 'No scraped data available for this job folder. Run a scraping job first.'
        })
            
    except Exception as e:
        logger.error(f"Error fetching job results for folder {job_folder_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'job_folder_id': job_folder_id,
            'error': str(e)
        }, status=500)
'''

print("🚨 EMERGENCY PRODUCTION FIX CODE READY")
print("This will replace the entire brightdata_job_results function")
print("=" * 60)
print(production_fix_code)