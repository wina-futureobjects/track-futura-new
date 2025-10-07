"""
BrightData Integration Views

This module provides API views for BrightData integration,
including configuration management and webhook handling.
"""

import json
import logging
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import BrightDataConfig, BrightDataBatchJob, BrightDataScraperRequest, BrightDataWebhookEvent
from .serializers import BrightDataConfigSerializer, BrightDataBatchJobSerializer, BrightDataScraperRequestSerializer
from .services import BrightDataAutomatedBatchScraper

logger = logging.getLogger(__name__)


class BrightDataConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for BrightData configuration management"""
    queryset = BrightDataConfig.objects.all()
    serializer_class = BrightDataConfigSerializer

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test connection to BrightData API"""
        config = self.get_object()
        scraper = BrightDataAutomatedBatchScraper()
        result = scraper.test_brightdata_connection(config)
        
        return Response(result, status=status.HTTP_200_OK if result['success'] else status.HTTP_400_BAD_REQUEST)


class BrightDataBatchJobViewSet(viewsets.ModelViewSet):
    """ViewSet for BrightData batch job management"""
    queryset = BrightDataBatchJob.objects.all()
    serializer_class = BrightDataBatchJobSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a batch job"""
        batch_job = self.get_object()
        
        if batch_job.status != 'pending':
            return Response(
                {'error': f'Cannot execute job with status: {batch_job.status}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        scraper = BrightDataAutomatedBatchScraper()
        success = scraper.execute_batch_job(batch_job.id)
        
        if success:
            return Response({'message': 'Batch job execution started'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to start batch job'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def create_and_execute(self, request):
        """Create and immediately execute a batch job"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            batch_job = serializer.save()
            
            # Execute the job
            scraper = BrightDataAutomatedBatchScraper()
            success = scraper.execute_batch_job(batch_job.id)
            
            if success:
                return Response(
                    {'id': batch_job.id, 'message': 'Batch job created and started'}, 
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'id': batch_job.id, 'error': 'Job created but failed to start'}, 
                    status=status.HTTP_201_CREATED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BrightDataScraperRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for BrightData scraper request management"""
    queryset = BrightDataScraperRequest.objects.all()
    serializer_class = BrightDataScraperRequestSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        batch_job_id = self.request.query_params.get('batch_job_id')
        if batch_job_id:
            queryset = queryset.filter(batch_job_id=batch_job_id)
        return queryset


@csrf_exempt
@require_http_methods(["POST"])
def brightdata_webhook(request):
    """Handle BrightData webhook events for data delivery"""
    start_time = time.time()
    
    try:
        # Parse webhook data
        data = json.loads(request.body)
        
        # Check for platform setup request
        if isinstance(data, dict) and data.get('setup_type') == 'platforms_and_services':
            return _handle_platform_setup(data)
        
        # Check for database setup trigger
        if isinstance(data, dict) and data.get('snapshot_id') == 'database_setup_trigger':
            return _handle_platform_setup(data)
        
        # Handle both single items and arrays
        if not isinstance(data, list):
            data = [data]
        
        # Extract metadata from the first item if available
        snapshot_id = None
        platform = 'unknown'
        
        if data and len(data) > 0:
            first_item = data[0]
            snapshot_id = first_item.get('snapshot_id') or first_item.get('_id')
            
            # Determine platform from URL or other indicators
            if 'instagram.com' in str(first_item.get('url', '')):
                platform = 'instagram'
            elif 'facebook.com' in str(first_item.get('url', '')):
                platform = 'facebook'
            elif 'tiktok.com' in str(first_item.get('url', '')):
                platform = 'tiktok'
            elif 'linkedin.com' in str(first_item.get('url', '')):
                platform = 'linkedin'
        
        if not snapshot_id:
            snapshot_id = f"webhook_{int(time.time())}"
        
        # Create webhook event
        webhook_event = BrightDataWebhookEvent.objects.create(
            event_id=f"{snapshot_id}_{int(time.time())}",
            snapshot_id=snapshot_id,
            status='processing',
            platform=platform,
            raw_data=data
        )
        
        # Find associated scraper request
        scraper_request = None
        if snapshot_id:
            try:
                scraper_request = BrightDataScraperRequest.objects.filter(
                    snapshot_id=snapshot_id
                ).first()
                
                if scraper_request:
                    webhook_event.platform = scraper_request.platform
                    webhook_event.save()
                    logger.info(f"Found associated scraper request: {scraper_request.id}")
            except Exception as e:
                logger.error(f"Error finding scraper request: {str(e)}")
        
        # Process the webhook data
        try:
            success = _process_brightdata_results(data, platform, scraper_request)
            
            if success:
                webhook_event.status = 'completed'
                webhook_event.processed_at = timezone.now()
                
                if scraper_request:
                    scraper_request.status = 'completed'
                    scraper_request.completed_at = timezone.now()
                    scraper_request.save()
                    
                    # Update batch job status
                    _update_batch_job_status(scraper_request.batch_job)
                    
            else:
                webhook_event.status = 'failed'
                
                if scraper_request:
                    scraper_request.status = 'failed'
                    scraper_request.error_message = 'Failed to process webhook data'
                    scraper_request.save()
                    
            webhook_event.save()
            
        except Exception as e:
            logger.error(f"Error processing webhook data: {str(e)}")
            webhook_event.status = 'failed'
            webhook_event.save()
            
            if scraper_request:
                scraper_request.status = 'failed'
                scraper_request.error_message = str(e)
                scraper_request.save()
        
        processing_time = time.time() - start_time
        logger.info(f"Webhook processed in {processing_time:.2f}s - {len(data)} items")
        
        return JsonResponse({
            'status': 'success',
            'items_processed': len(data),
            'processing_time': processing_time
        })
        
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@csrf_exempt
@require_http_methods(["POST"])
def brightdata_notify(request):
    """Handle BrightData notification events for job status updates"""
    try:
        # Parse notification data
        data = json.loads(request.body)
        
        # Check for platform setup request
        if data.get('type') == 'setup_platforms' or data.get('setup_type') == 'platforms_and_services':
            return _handle_platform_setup(data)
        
        snapshot_id = data.get('snapshot_id')
        status_value = data.get('status', 'unknown')
        
        logger.info(f"Received BrightData notification: {snapshot_id} - {status_value}")
        
        # Find associated scraper request
        if snapshot_id:
            scraper_request = BrightDataScraperRequest.objects.filter(
                snapshot_id=snapshot_id
            ).first()
            
            if scraper_request:
                # Map BrightData status to our status
                status_mapping = {
                    'running': 'processing',
                    'completed': 'completed',
                    'failed': 'failed',
                    'cancelled': 'cancelled'
                }
                
                new_status = status_mapping.get(status_value.lower(), 'processing')
                scraper_request.status = new_status
                
                if new_status in ['completed', 'failed', 'cancelled']:
                    scraper_request.completed_at = timezone.now()
                
                scraper_request.save()
                
                # Update batch job status
                _update_batch_job_status(scraper_request.batch_job)
                
                logger.info(f"Updated scraper request {scraper_request.id} status to {new_status}")
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Notification processing error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def _process_brightdata_results(data: list, platform: str, scraper_request=None):
    """Process BrightData results and store them in appropriate models"""
    try:
        logger.info(f"Processing {len(data)} items for platform {platform}")
        
        # Process results based on platform
        if platform == 'instagram':
            return _process_instagram_results(scraper_request, data)
        elif platform == 'facebook':
            return _process_facebook_results(scraper_request, data)
        elif platform == 'tiktok':
            return _process_tiktok_results(scraper_request, data)
        elif platform == 'linkedin':
            return _process_linkedin_results(scraper_request, data)
        else:
            logger.warning(f"Unknown platform for result processing: {platform}")
            return True  # Don't fail for unknown platforms
            
    except Exception as e:
        logger.error(f"Error processing BrightData results: {str(e)}")
        return False


def _process_instagram_results(scraper_request, results):
    """Process Instagram scraping results"""
    try:
        from instagram_data.models import InstagramPost, InstagramAccount, Folder
        
        processed_count = 0
        
        for item in results:
            try:
                # Get or create Instagram account
                username = item.get('user_username') or item.get('username')
                if not username:
                    continue
                
                account, created = InstagramAccount.objects.get_or_create(
                    username=username,
                    defaults={
                        'display_name': item.get('user_full_name', username),
                        'bio': item.get('user_bio', ''),
                        'followers_count': item.get('user_followers', 0),
                        'following_count': item.get('user_following', 0),
                        'posts_count': item.get('user_posts_count', 0),
                    }
                )
                
                # Create Instagram post
                post_id = item.get('post_id') or item.get('id')
                if not post_id:
                    continue
                
                post, created = InstagramPost.objects.get_or_create(
                    post_id=post_id,
                    defaults={
                        'account': account,
                        'content': item.get('caption', ''),
                        'likes_count': item.get('likes_count', 0),
                        'comments_count': item.get('comments_count', 0),
                        'media_type': item.get('media_type', 'unknown'),
                        'media_url': item.get('media_url', ''),
                        'timestamp': item.get('timestamp'),
                        'location': item.get('location', ''),
                        'hashtags': item.get('hashtags', []),
                        'mentions': item.get('mentions', []),
                    }
                )
                
                if created:
                    processed_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing Instagram item: {str(e)}")
                continue
        
        logger.info(f"Processed {processed_count} Instagram posts")
        return True
        
    except Exception as e:
        logger.error(f"Error processing Instagram results: {str(e)}")
        return False


def _process_facebook_results(scraper_request, results):
    """Process Facebook scraping results"""
    try:
        from facebook_data.models import FacebookPost, FacebookAccount, Folder
        
        processed_count = 0
        
        for item in results:
            try:
                # Get or create Facebook account
                username = item.get('user_username') or item.get('page_name')
                if not username:
                    continue
                
                account, created = FacebookAccount.objects.get_or_create(
                    username=username,
                    defaults={
                        'name': item.get('user_name', username),
                        'page_id': item.get('page_id', ''),
                        'followers_count': item.get('followers_count', 0),
                        'likes_count': item.get('page_likes', 0),
                    }
                )
                
                # Create Facebook post
                post_id = item.get('post_id') or item.get('id')
                if not post_id:
                    continue
                
                post, created = FacebookPost.objects.get_or_create(
                    post_id=post_id,
                    defaults={
                        'user_posted': account,
                        'post_text': item.get('post_text', ''),
                        'num_likes': item.get('num_likes', 0),
                        'num_comments': item.get('num_comments', 0),
                        'num_shares': item.get('num_shares', 0),
                        'date_posted': item.get('date_posted'),
                        'url': item.get('url', ''),
                        'media_type': item.get('media_type', 'text'),
                        'media_url': item.get('media_url', ''),
                    }
                )
                
                if created:
                    processed_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing Facebook item: {str(e)}")
                continue
        
        logger.info(f"Processed {processed_count} Facebook posts")
        return True
        
    except Exception as e:
        logger.error(f"Error processing Facebook results: {str(e)}")
        return False


def _process_tiktok_results(scraper_request, results):
    """Process TikTok scraping results"""
    try:
        from tiktok_data.models import TikTokVideo, TikTokProfile
        
        processed_count = 0
        
        for item in results:
            try:
                # Get or create TikTok profile
                username = item.get('username') or item.get('author_username')
                if not username:
                    continue
                
                profile, created = TikTokProfile.objects.get_or_create(
                    username=username,
                    defaults={
                        'display_name': item.get('author_name', username),
                        'bio': item.get('author_bio', ''),
                        'followers_count': item.get('author_followers', 0),
                        'following_count': item.get('author_following', 0),
                        'likes_count': item.get('author_likes', 0),
                    }
                )
                
                # Create TikTok video
                video_id = item.get('video_id') or item.get('id')
                if not video_id:
                    continue
                
                video, created = TikTokVideo.objects.get_or_create(
                    video_id=video_id,
                    defaults={
                        'profile': profile,
                        'description': item.get('description', ''),
                        'likes_count': item.get('likes_count', 0),
                        'comments_count': item.get('comments_count', 0),
                        'shares_count': item.get('shares_count', 0),
                        'views_count': item.get('views_count', 0),
                        'video_url': item.get('video_url', ''),
                        'duration': item.get('duration', 0),
                        'created_time': item.get('created_time'),
                        'hashtags': item.get('hashtags', []),
                    }
                )
                
                if created:
                    processed_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing TikTok item: {str(e)}")
                continue
        
        logger.info(f"Processed {processed_count} TikTok videos")
        return True
        
    except Exception as e:
        logger.error(f"Error processing TikTok results: {str(e)}")
        return False


def _process_linkedin_results(scraper_request, results):
    """Process LinkedIn scraping results"""
    try:
        from linkedin_data.models import LinkedInPost, LinkedInProfile
        
        processed_count = 0
        
        for item in results:
            try:
                # Get or create LinkedIn profile
                username = item.get('author_username') or item.get('user_name')
                if not username:
                    continue
                
                profile, created = LinkedInProfile.objects.get_or_create(
                    username=username,
                    defaults={
                        'name': item.get('author_name', username),
                        'headline': item.get('author_headline', ''),
                        'location': item.get('author_location', ''),
                        'connections_count': item.get('connections_count', 0),
                    }
                )
                
                # Create LinkedIn post
                post_id = item.get('post_id') or item.get('id')
                if not post_id:
                    continue
                
                post, created = LinkedInPost.objects.get_or_create(
                    post_id=post_id,
                    defaults={
                        'profile': profile,
                        'content': item.get('content', ''),
                        'likes_count': item.get('likes_count', 0),
                        'comments_count': item.get('comments_count', 0),
                        'shares_count': item.get('shares_count', 0),
                        'published_at': item.get('published_at'),
                        'url': item.get('url', ''),
                        'media_type': item.get('media_type', 'text'),
                    }
                )
                
                if created:
                    processed_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing LinkedIn item: {str(e)}")
                continue
        
        logger.info(f"Processed {processed_count} LinkedIn posts")
        return True
        
    except Exception as e:
        logger.error(f"Error processing LinkedIn results: {str(e)}")
        return False


def _update_batch_job_status(batch_job: BrightDataBatchJob):
    """Update batch job status based on scraper request statuses"""
    try:
        scraper_requests = batch_job.scraper_requests.all()
        total_requests = scraper_requests.count()
        
        if total_requests == 0:
            return
        
        completed_requests = scraper_requests.filter(status='completed').count()
        failed_requests = scraper_requests.filter(status='failed').count()
        processing_requests = scraper_requests.filter(status='processing').count()
        
        # Calculate progress
        progress = int((completed_requests + failed_requests) / total_requests * 100)
        batch_job.progress = progress
        
        # Update status
        if completed_requests == total_requests:
            batch_job.status = 'completed'
            batch_job.completed_at = timezone.now()
        elif failed_requests == total_requests:
            batch_job.status = 'failed'
            batch_job.completed_at = timezone.now()
        elif processing_requests > 0:
            batch_job.status = 'processing'
        
        batch_job.save()
        
        logger.info(f"Updated batch job {batch_job.id} status to {batch_job.status} ({progress}%)")
        
    except Exception as e:
        logger.error(f"Error updating batch job status: {str(e)}")


def _handle_platform_setup(data):
    """Handle platform and service setup requests"""
    try:
        logger.info("Handling platform setup request...")
        
        from users.models import Platform, Service, PlatformService
        
        platforms_created = 0
        services_created = 0
        platform_services_created = 0
        
        # Create Instagram platform
        instagram_platform, created = Platform.objects.get_or_create(
            name='instagram',
            defaults={
                'display_name': 'Instagram',
                'description': 'Instagram social media platform',
                'is_enabled': True
            }
        )
        if created:
            platforms_created += 1
            logger.info(f"Created Instagram platform with ID {instagram_platform.id}")
        
        # Create Facebook platform  
        facebook_platform, created = Platform.objects.get_or_create(
            name='facebook',
            defaults={
                'display_name': 'Facebook', 
                'description': 'Facebook social media platform',
                'is_enabled': True
            }
        )
        if created:
            platforms_created += 1
            logger.info(f"Created Facebook platform with ID {facebook_platform.id}")
        
        # Create Posts service
        posts_service, created = Service.objects.get_or_create(
            name='posts',
            defaults={
                'display_name': 'Posts Scraping',
                'description': 'Scrape posts from social media platforms',
                'is_enabled': True
            }
        )
        if created:
            services_created += 1
            logger.info(f"Created Posts service with ID {posts_service.id}")
        
        # Create platform-service combinations
        instagram_posts, created = PlatformService.objects.get_or_create(
            platform=instagram_platform,
            service=posts_service,
            defaults={
                'description': 'Instagram posts scraping service',
                'is_enabled': True
            }
        )
        if created:
            platform_services_created += 1
            logger.info(f"Created Instagram-Posts service with ID {instagram_posts.id}")
        
        facebook_posts, created = PlatformService.objects.get_or_create(
            platform=facebook_platform,
            service=posts_service,
            defaults={
                'description': 'Facebook posts scraping service', 
                'is_enabled': True
            }
        )
        if created:
            platform_services_created += 1
            logger.info(f"Created Facebook-Posts service with ID {facebook_posts.id}")
        
        logger.info(f"Platform setup complete! Created {platforms_created} platforms, {services_created} services, {platform_services_created} platform services")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Platform setup completed',
            'platforms_created': platforms_created,
            'services_created': services_created,
            'platform_services_created': platform_services_created,
            'instagram_platform_id': instagram_platform.id,
            'facebook_platform_id': facebook_platform.id,
            'posts_service_id': posts_service.id,
            'instagram_posts_id': instagram_posts.id,
            'facebook_posts_id': facebook_posts.id
        })
        
    except Exception as e:
        logger.error(f"Error in platform setup: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Platform setup failed: {str(e)}'
        }, status=500)