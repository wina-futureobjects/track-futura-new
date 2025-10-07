"""
Apify Integration Views

API endpoints for managing Apify configurations, batch jobs, and webhooks.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
import json
import logging
import time
import requests

from .models import ApifyConfig, ApifyBatchJob, ApifyScraperRequest, ApifyNotification, ApifyWebhookEvent
from .serializers import ApifyConfigSerializer, ApifyBatchJobSerializer, ApifyScraperRequestSerializer
from .services import ApifyAutomatedBatchScraper

logger = logging.getLogger(__name__)

class ApifyConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Apify configurations"""
    queryset = ApifyConfig.objects.all()
    serializer_class = ApifyConfigSerializer
    
    @action(detail=False, methods=['post'])
    def setup_defaults(self, request):
        """Set up default Apify configurations"""
        try:
            api_token = request.data.get('api_token')
            if not api_token:
                return Response({'error': 'API token required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create default configurations
            platforms = [
                ('facebook_posts', 'apify/facebook-scraper'),
                ('facebook_reels', 'apify/facebook-scraper'),
                ('facebook_comments', 'apify/facebook-scraper'),
                ('instagram_posts', 'apify/instagram-scraper'),
                ('instagram_reels', 'apify/instagram-scraper'),
                ('instagram_comments', 'apify/instagram-scraper'),
                ('linkedin_posts', 'apify/linkedin-scraper'),
                ('tiktok_posts', 'apify/tiktok-scraper'),
            ]
            
            created_count = 0
            for platform, actor_id in platforms:
                config, created = ApifyConfig.objects.get_or_create(
                    platform=platform,
                    defaults={
                        'name': f"{platform.replace('_', ' ').title()}",
                        'api_token': api_token,
                        'actor_id': actor_id,
                        'is_active': True
                    }
                )
                if created:
                    created_count += 1
            
            return Response({
                'message': f'Created {created_count} configurations',
                'total': len(platforms)
            })
            
        except Exception as e:
            logger.error(f"Error setting up defaults: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ApifyBatchJobViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Apify batch jobs"""
    queryset = ApifyBatchJob.objects.all()
    serializer_class = ApifyBatchJobSerializer

    @action(detail=False, methods=['get'])
    def resolve_folder(self, request):
        """Resolve a folder ID to its associated batch job ID"""
        folder_id = request.query_params.get('folder_id')
        if not folder_id:
            return Response({'error': 'folder_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from track_accounts.models import UnifiedRunFolder
            from workflow.models import ScrapingJob

            # Try to get the unified folder
            try:
                unified_folder = UnifiedRunFolder.objects.get(id=folder_id)

                # If this is a job folder, find its associated batch job through scraping run
                if unified_folder.scraping_run:
                    scraping_jobs = unified_folder.scraping_run.scraping_jobs.all()
                    if scraping_jobs.exists():
                        batch_job = scraping_jobs.first().batch_job
                        return Response({
                            'folder_id': folder_id,
                            'batch_job_id': batch_job.id,
                            'batch_job_name': batch_job.name,
                            'batch_job_status': batch_job.status,
                            'scraping_run_id': unified_folder.scraping_run.id
                        })
            except UnifiedRunFolder.DoesNotExist:
                pass

            # If folder_id might be a batch job ID directly, try that
            try:
                batch_job = ApifyBatchJob.objects.get(id=folder_id)
                return Response({
                    'folder_id': folder_id,
                    'batch_job_id': batch_job.id,
                    'batch_job_name': batch_job.name,
                    'batch_job_status': batch_job.status,
                    'is_direct_batch_job': True
                })
            except ApifyBatchJob.DoesNotExist:
                pass

            return Response({'error': 'No batch job found for this folder'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error resolving folder to batch job: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a batch job"""
        try:
            batch_job = self.get_object()
            scraper = ApifyAutomatedBatchScraper()
            success = scraper.execute_batch_job(batch_job.id)
            
            if success:
                return Response({'message': 'Batch job started successfully'})
            else:
                return Response({'error': 'Failed to start batch job'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error executing batch job: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get results for a batch job"""
        try:
            batch_job = self.get_object()
            results = []
            
            # Get results from all completed scraper requests
            for scraper_request in batch_job.scraper_requests.filter(status='completed'):
                platform_results = _get_platform_results(scraper_request)
                if platform_results:
                    results.extend(platform_results)
            
            return Response({
                'batch_job_id': batch_job.id,
                'batch_job_name': batch_job.name,
                'status': batch_job.status,
                'total_results': len(results),
                'results': results
            })
            
        except Exception as e:
            logger.error(f"Error getting batch job results: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def requests(self, request, pk=None):
        """Get scraper requests for a batch job"""
        try:
            batch_job = self.get_object()
            scraper_requests = batch_job.scraper_requests.all()

            # Serialize the scraper requests
            serializer = ApifyScraperRequestSerializer(scraper_requests, many=True)

            return Response({
                'results': serializer.data,
                'count': scraper_requests.count()
            })

        except Exception as e:
            logger.error(f"Error getting batch job requests: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Export batch job results as CSV or JSON"""
        try:
            batch_job = self.get_object()
            export_format = request.query_params.get('format', 'csv')

            # Get all results
            all_results = []
            for scraper_request in batch_job.scraper_requests.filter(status='completed'):
                platform_results = _get_platform_results(scraper_request)
                if platform_results:
                    all_results.extend(platform_results)

            if export_format.lower() == 'json':
                response = JsonResponse({
                    'batch_job': batch_job.name,
                    'export_date': timezone.now().isoformat(),
                    'total_results': len(all_results),
                    'results': all_results
                })
                response['Content-Disposition'] = f'attachment; filename="{batch_job.name}_results.json"'
                return response
            else:
                # Return CSV format
                import csv
                from django.http import HttpResponse

                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{batch_job.name}_results.csv"'

                if all_results:
                    writer = csv.DictWriter(response, fieldnames=all_results[0].keys())
                    writer.writeheader()
                    writer.writerows(all_results)

                return response

        except Exception as e:
            logger.error(f"Error exporting batch job results: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ApifyScraperRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Apify scraper requests"""
    queryset = ApifyScraperRequest.objects.all()
    serializer_class = ApifyScraperRequestSerializer

@csrf_exempt
@require_http_methods(["POST"])
def apify_webhook(request):
    """Handle Apify webhook events"""
    start_time = time.time()
    
    try:
        # Parse webhook data
        data = json.loads(request.body)
        run_id = data.get('runId')
        status = data.get('status')
        actor_id = data.get('actorId')
        
        if not run_id:
            return JsonResponse({'error': 'runId required'}, status=400)
        
        # Create webhook event
        webhook_event = ApifyWebhookEvent.objects.create(
            event_id=f"{run_id}_{int(time.time())}",
            run_id=run_id,
            status='processing',
            platform=actor_id.split('/')[-1] if actor_id else '',
            raw_data=data
        )
        
        # Find associated scraper request
        scraper_request = None
        if run_id:
            try:
                scraper_request = ApifyScraperRequest.objects.filter(request_id=run_id).first()
                if scraper_request:
                    webhook_event.platform = scraper_request.platform.split('_')[0]
                    webhook_event.save()
                    logger.info(f"✅ Found associated scraper request: {scraper_request.id}")
            except Exception as e:
                logger.error(f"Error finding scraper request: {str(e)}")
                scraper_request = None
        
        # Update scraper request status
        if scraper_request:
            try:
                # Map Apify status to our status
                status_mapping = {
                    'READY': 'processing',
                    'RUNNING': 'processing',
                    'SUCCEEDED': 'completed',
                    'FAILED': 'failed',
                    'ABORTED': 'cancelled',
                    'TIMED_OUT': 'failed'
                }
                
                new_status = status_mapping.get(status, 'processing')
                scraper_request.status = new_status
                
                if new_status in ['completed', 'failed', 'cancelled']:
                    scraper_request.completed_at = timezone.now()
                
                # Process results if completed successfully
                if new_status == 'completed':
                    try:
                        _process_apify_results(scraper_request)
                        logger.info(f"✅ Processed results for scraper request {scraper_request.id}")
                    except Exception as e:
                        logger.error(f"❌ Error processing results for {scraper_request.id}: {str(e)}")
                
                scraper_request.save()
                logger.info(f"✅ Updated scraper request {scraper_request.id} status to {new_status}")
                
                # Update batch job status
                batch_job = scraper_request.batch_job
                if batch_job:
                    # Count completed/failed requests
                    completed_requests = batch_job.scraper_requests.filter(status='completed').count()
                    failed_requests = batch_job.scraper_requests.filter(status='failed').count()
                    total_requests = batch_job.scraper_requests.count()
                    
                    if completed_requests + failed_requests >= total_requests:
                        if failed_requests == 0:
                            batch_job.status = 'completed'
                        else:
                            batch_job.status = 'failed'
                        batch_job.completed_at = timezone.now()
                        batch_job.save()
                        logger.info(f"✅ Updated batch job {batch_job.id} status to {batch_job.status}")

            except Exception as e:
                logger.error(f"❌ Error updating scraper request: {str(e)}")

        # Mark webhook as completed
        webhook_event.status = 'completed'
        webhook_event.processed_at = timezone.now()
        webhook_event.save()
        
        processing_time = time.time() - start_time
        logger.info(f"Webhook processed in {processing_time:.2f}s")
        
        return JsonResponse({'status': 'success'})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def apify_notify(request):
    """Handle Apify notifications"""
    try:
        data = json.loads(request.body)
        run_id = data.get('runId')
        status = data.get('status')
        message = data.get('message', '')
        error_message = data.get('errorMessage', '')
        
        # Create notification
        notification = ApifyNotification.objects.create(
            run_id=run_id,
            status=status,
            message=message or f"Run {status}",
            raw_data=data,
            request_ip=request.META.get('REMOTE_ADDR'),
            request_headers=dict(request.META)
        )
        
        # Find associated scraper request and update
        if run_id:
            try:
                scraper_request = ApifyScraperRequest.objects.filter(request_id=run_id).first()
                if scraper_request:
                    notification.scraper_request = scraper_request
                    notification.save()
                
                # Update scraper request status
                status_mapping = {
                    'READY': 'processing',
                    'RUNNING': 'processing',
                    'SUCCEEDED': 'completed',
                    'FAILED': 'failed',
                    'ABORTED': 'cancelled',
                    'TIMED_OUT': 'failed'
                }
                
                new_status = status_mapping.get(status, 'processing')
                if scraper_request:
                    scraper_request.status = new_status
                    if new_status in ['completed', 'failed', 'cancelled']:
                        scraper_request.completed_at = timezone.now()
                    if error_message:
                        scraper_request.error_message = error_message
                    scraper_request.save()
                    
            except Exception as e:
                logger.error(f"Error updating scraper request: {str(e)}")
        
        return JsonResponse({'status': 'success'})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Notification error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def _process_apify_results(scraper_request: ApifyScraperRequest):
    """
    Download and process results from Apify when a scraper request completes
    """
    try:
        # Get the dataset results from Apify
        config = scraper_request.config
        run_id = scraper_request.request_id
        
        if not run_id:
            logger.error(f"No run_id found for scraper request {scraper_request.id}")
            return
        
        # Download results from Apify
        dataset_url = f"https://api.apify.com/v2/acts/{config.actor_id}/runs/{run_id}/dataset/items"
        headers = {
            'Authorization': f'Bearer {config.api_token}',
            'Content-Type': 'application/json'
        }
        
        # Try the correct dataset API endpoint
        response = requests.get(dataset_url, headers=headers, timeout=30)
        
        # If that fails, try the alternative dataset endpoint
        if response.status_code == 404:
            dataset_url = f"https://api.apify.com/v2/datasets/{run_id}/items"
            response = requests.get(dataset_url, headers=headers, timeout=30)
            
        # If still failing, try to get the dataset ID from the run info
        if response.status_code == 404:
            run_info_url = f"https://api.apify.com/v2/acts/{config.actor_id}/runs/{run_id}"
            run_response = requests.get(run_info_url, headers=headers, timeout=30)
            
            if run_response.status_code == 200:
                run_data = run_response.json()['data']
                dataset_id = run_data.get('defaultDatasetId')
                
                if dataset_id:
                    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
                    response = requests.get(dataset_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            results = response.json()
            logger.info(f"Downloaded {len(results)} items for {scraper_request.platform}")
            
            # Process results based on platform
            if scraper_request.platform.startswith('instagram'):
                _process_instagram_results(scraper_request, results)
            elif scraper_request.platform.startswith('facebook'):
                _process_facebook_results(scraper_request, results)
            elif scraper_request.platform.startswith('tiktok'):
                _process_tiktok_results(scraper_request, results)
            elif scraper_request.platform.startswith('linkedin'):
                _process_linkedin_results(scraper_request, results)
            else:
                logger.warning(f"Unknown platform for result processing: {scraper_request.platform}")
                
        else:
            logger.error(f"Failed to download results: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error processing Apify results: {str(e)}")


def _process_instagram_results(scraper_request: ApifyScraperRequest, results):
    """Process Instagram scraping results"""
    try:
        from instagram_data.models import Folder, InstagramPost
        from track_accounts.models import SourceFolder, UnifiedRunFolder

        # Create or get folder for this scraping run
        batch_job = scraper_request.batch_job

        # Get source folder names
        source_folder_names = []
        if batch_job.source_folder_ids:
            source_folders = SourceFolder.objects.filter(id__in=batch_job.source_folder_ids)
            source_folder_names = [sf.name for sf in source_folders]

        # Create folder name with source folder names + date/time
        if source_folder_names:
            folder_base_name = ", ".join(source_folder_names)
        else:
            folder_base_name = "Instagram Scrape"

        # Format: "Brand Sources - 06/10/2025 14:00:00"
        folder_name = f"{folder_base_name} - {scraper_request.started_at.strftime('%d/%m/%Y %H:%M:%S')}"

        # Find the corresponding unified job folder for this scraper request
        # Look for job folder with Instagram platform created around the same time
        unified_job_folder = None
        target_url = scraper_request.target_url or ''
        username = target_url.split('/')[-1] if target_url else ''

        if username:
            # Try to find unified job folder by username in name
            unified_job_folder = UnifiedRunFolder.objects.filter(
                Q(project=batch_job.project) &
                Q(folder_type='job') &
                Q(name__icontains='Instagram') &
                Q(name__icontains=username)
            ).first()

        if not unified_job_folder:
            # Fallback: find most recent Instagram job folder for this project
            unified_job_folder = UnifiedRunFolder.objects.filter(
                project=batch_job.project,
                folder_type='job',
                name__icontains='Instagram'
            ).order_by('-created_at').first()

        folder, created = Folder.objects.get_or_create(
            name=folder_name,
            project=batch_job.project,
            defaults={
                'description': f'Results from Apify run {scraper_request.request_id}',
                'category': 'posts',
                'folder_type': 'content',
                'unified_job_folder': unified_job_folder
            }
        )

        if created:
            logger.info(f"✓ Created new Instagram folder: {folder.name} (ID: {folder.id})")
        else:
            logger.info(f"✓ Using existing Instagram folder: {folder.name} (ID: {folder.id})")

        # Update unified_job_folder link if folder already exists but wasn't linked
        if not created and not folder.unified_job_folder and unified_job_folder:
            folder.unified_job_folder = unified_job_folder
            folder.save()
            logger.info(f"✓ Linked existing folder {folder.id} to unified job folder {unified_job_folder.id}")
        
        posts_saved = 0
        for item in results:
            try:
                # Map Apify data to InstagramPost model
                post_data = {
                    'folder': folder,
                    'url': item.get('url', ''),
                    'user_posted': item.get('ownerUsername', ''),
                    'description': item.get('caption', ''),
                    'hashtags': item.get('hashtags', []),
                    'num_comments': item.get('commentsCount', 0),
                    'likes': item.get('likesCount', 0),
                    'post_id': item.get('id', ''),
                    'shortcode': item.get('shortCode', ''),
                    'content_type': item.get('type', 'post'),
                    'views': item.get('videoViewCount', 0),
                    'photos': item.get('images', []),
                    'videos': item.get('videos', []),
                    'thumbnail': item.get('displayUrl', ''),
                    'user_posted_id': item.get('ownerId', ''),
                    'followers': item.get('ownerFollowersCount', 0),
                    'following': item.get('ownerFollowingCount', 0),
                    'is_verified': item.get('ownerIsVerified', False),
                    'location': item.get('locationName', ''),
                    'date_posted': timezone.now()  # Apify doesn't always provide this
                }
                
                # Create or update post - use post_id as primary uniqueness key
                post, created = InstagramPost.objects.get_or_create(
                    post_id=post_data['post_id'],
                    defaults=post_data
                )

                if created:
                    posts_saved += 1
                    logger.info(f"✓ Saved Instagram post {post_data['post_id']} by @{post_data['user_posted']}")
                else:
                    # Update existing post with new folder if different
                    if post.folder != folder:
                        post.folder = folder
                        post.save()
                        posts_saved += 1
                        logger.info(f"✓ Updated Instagram post {post_data['post_id']} folder assignment")

            except Exception as e:
                logger.error(f"Error saving Instagram post {post_data.get('post_id', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"Saved {posts_saved} Instagram posts to folder {folder.name}")
        
    except Exception as e:
        logger.error(f"Error processing Instagram results: {str(e)}")


def _process_facebook_results(scraper_request: ApifyScraperRequest, results):
    """Process Facebook scraping results"""
    try:
        from facebook_data.models import Folder, FacebookPost
        from track_accounts.models import SourceFolder, UnifiedRunFolder
        from django.db.models import Q

        # Create or get folder for this scraping run
        batch_job = scraper_request.batch_job

        # Get source folder names
        source_folder_names = []
        if batch_job.source_folder_ids:
            source_folders = SourceFolder.objects.filter(id__in=batch_job.source_folder_ids)
            source_folder_names = [sf.name for sf in source_folders]

        # Create folder name with source folder names + date/time
        if source_folder_names:
            folder_base_name = ", ".join(source_folder_names)
        else:
            folder_base_name = "Facebook Scrape"

        # Format: "Brand Sources - 06/10/2025 14:00:00"
        folder_name = f"{folder_base_name} - {scraper_request.started_at.strftime('%d/%m/%Y %H:%M:%S')}"

        # Find the corresponding unified job folder for this scraper request
        unified_job_folder = None
        target_url = scraper_request.target_url or ''
        username = target_url.split('/')[-1] if target_url else ''

        if username:
            # Try to find unified job folder by username in name
            unified_job_folder = UnifiedRunFolder.objects.filter(
                Q(project=batch_job.project) &
                Q(folder_type='job') &
                Q(name__icontains='Facebook') &
                Q(name__icontains=username)
            ).first()

        if not unified_job_folder:
            # Fallback: find most recent Facebook job folder for this project
            unified_job_folder = UnifiedRunFolder.objects.filter(
                project=batch_job.project,
                folder_type='job',
                name__icontains='Facebook'
            ).order_by('-created_at').first()

        folder, created = Folder.objects.get_or_create(
            name=folder_name,
            project=batch_job.project,
            defaults={
                'description': f'Results from Apify run {scraper_request.request_id}',
                'category': 'posts',
                'unified_job_folder': unified_job_folder,
                'folder_type': 'content'
            }
        )

        # Update unified_job_folder link if folder already exists but wasn't linked
        if not created and not folder.unified_job_folder and unified_job_folder:
            folder.unified_job_folder = unified_job_folder
            folder.save()
            logger.info(f"✓ Linked existing folder {folder.id} to unified job folder {unified_job_folder.id}")

        posts_saved = 0
        for item in results:
            try:
                # Map Apify data to FacebookPost model
                post_data = {
                    'folder': folder,
                    'url': item.get('postUrl', item.get('url', '')),
                    'user_posted': item.get('user', ''),
                    'content': item.get('text', ''),
                    'description': item.get('text', ''),
                    'likes': item.get('likes', 0),
                    'num_comments': item.get('comments', 0),
                    'num_shares': item.get('shares', 0),
                    'post_id': item.get('postId', item.get('id', '')),
                    'video_view_count': item.get('views', 0),
                    'date_posted': timezone.now()
                }

                # Create or update post
                post, created = FacebookPost.objects.get_or_create(
                    post_id=post_data['post_id'],
                    defaults=post_data
                )

                if created:
                    posts_saved += 1
                    logger.info(f"✓ Saved Facebook post {post_data['post_id']} by {post_data['user_posted']}")
                else:
                    # Update existing post with new folder if different
                    if post.folder != folder:
                        post.folder = folder
                        post.save()
                        logger.info(f"✓ Updated Facebook post {post_data['post_id']} folder")

            except Exception as e:
                logger.error(f"Error saving Facebook post {item.get('postId', 'unknown')}: {str(e)}")
                continue

        logger.info(f"Saved {posts_saved} Facebook posts to folder {folder.name}")

    except Exception as e:
        logger.error(f"Error processing Facebook results: {str(e)}")


def _process_tiktok_results(scraper_request: ApifyScraperRequest, results):
    """Process TikTok scraping results"""
    try:
        from tiktok_data.models import Folder, TikTokPost
        from track_accounts.models import SourceFolder

        # Create or get folder for this scraping run
        batch_job = scraper_request.batch_job

        # Get source folder names
        source_folder_names = []
        if batch_job.source_folder_ids:
            source_folders = SourceFolder.objects.filter(id__in=batch_job.source_folder_ids)
            source_folder_names = [sf.name for sf in source_folders]

        # Create folder name with source folder names + date/time
        if source_folder_names:
            folder_base_name = ", ".join(source_folder_names)
        else:
            folder_base_name = "TikTok Scrape"

        # Format: "Brand Sources - 06/10/2025 14:00:00"
        folder_name = f"{folder_base_name} - {scraper_request.started_at.strftime('%d/%m/%Y %H:%M:%S')}"

        folder, created = Folder.objects.get_or_create(
            name=folder_name,
            project=batch_job.project,
            defaults={
                'description': f'Results from Apify run {scraper_request.request_id}',
                'category': 'posts',
                'folder_type': 'content'
            }
        )

        posts_saved = 0
        for item in results:
            try:
                # Map Apify data to TikTokPost model
                hashtags_list = item.get('hashtags', [])
                hashtags_str = ', '.join([tag.get('name', '') if isinstance(tag, dict) else str(tag) for tag in hashtags_list])

                post_data = {
                    'folder': folder,
                    'url': item.get('webVideoUrl', item.get('url', '')),
                    'user_posted': item.get('authorMeta', {}).get('name', item.get('author', '')),
                    'description': item.get('text', ''),
                    'hashtags': hashtags_str,
                    'likes': item.get('diggCount', 0),
                    'num_comments': item.get('commentCount', 0),
                    'post_id': item.get('id', ''),
                    'thumbnail': item.get('covers', {}).get('default', '') if isinstance(item.get('covers'), dict) else '',
                    'videos': item.get('videoUrl', ''),
                    'followers': item.get('authorMeta', {}).get('fans', 0),
                    'is_verified': item.get('authorMeta', {}).get('verified', False),
                    'date_posted': timezone.now()
                }

                # Create or update post
                post, created = TikTokPost.objects.get_or_create(
                    post_id=post_data['post_id'],
                    defaults=post_data
                )

                if created:
                    posts_saved += 1
                    logger.info(f"✓ Saved TikTok post {post_data['post_id']} by @{post_data['user_posted']}")
                else:
                    # Update existing post with new folder if different
                    if post.folder != folder:
                        post.folder = folder
                        post.save()
                        logger.info(f"✓ Updated TikTok post {post_data['post_id']} folder")

            except Exception as e:
                logger.error(f"Error saving TikTok post {item.get('id', 'unknown')}: {str(e)}")
                continue

        logger.info(f"Saved {posts_saved} TikTok posts to folder {folder.name}")

    except Exception as e:
        logger.error(f"Error processing TikTok results: {str(e)}")


def _process_linkedin_results(scraper_request: ApifyScraperRequest, results):
    """Process LinkedIn scraping results"""
    try:
        from linkedin_data.models import Folder, LinkedInPost
        from track_accounts.models import SourceFolder

        # Create or get folder for this scraping run
        batch_job = scraper_request.batch_job

        # Get source folder names
        source_folder_names = []
        if batch_job.source_folder_ids:
            source_folders = SourceFolder.objects.filter(id__in=batch_job.source_folder_ids)
            source_folder_names = [sf.name for sf in source_folders]

        # Create folder name with source folder names + date/time
        if source_folder_names:
            folder_base_name = ", ".join(source_folder_names)
        else:
            folder_base_name = "LinkedIn Scrape"

        # Format: "Brand Sources - 06/10/2025 14:00:00"
        folder_name = f"{folder_base_name} - {scraper_request.started_at.strftime('%d/%m/%Y %H:%M:%S')}"

        folder, created = Folder.objects.get_or_create(
            name=folder_name,
            project=batch_job.project,
            defaults={
                'description': f'Results from Apify run {scraper_request.request_id}',
                'category': 'posts',
                'folder_type': 'content'
            }
        )

        posts_saved = 0
        for item in results:
            try:
                # Map Apify data to LinkedInPost model
                author_data = item.get('author', {})
                post_data = {
                    'folder': folder,
                    'url': item.get('postUrl', item.get('url', '')),
                    'user_posted': author_data.get('name', item.get('authorName', '')),
                    'description': item.get('text', ''),
                    'likes': item.get('likesCount', 0),
                    'num_likes': item.get('likesCount', 0),
                    'num_comments': item.get('commentsCount', 0),
                    'num_shares': item.get('sharesCount', 0),
                    'post_id': item.get('postId', item.get('urn', '')),
                    'post_text': item.get('text', ''),
                    'images': item.get('images', []),
                    'videos': item.get('videos', []),
                    'user_title': author_data.get('title', ''),
                    'user_headline': author_data.get('headline', ''),
                    'user_url': author_data.get('url', ''),
                    'author_profile_pic': author_data.get('profilePicture', ''),
                    'date_posted': timezone.now(),
                    'account_type': 'company' if item.get('type') == 'company' else 'personal'
                }

                # Create or update post
                post, created = LinkedInPost.objects.get_or_create(
                    post_id=post_data['post_id'],
                    defaults=post_data
                )

                if created:
                    posts_saved += 1
                    logger.info(f"✓ Saved LinkedIn post {post_data['post_id']} by {post_data['user_posted']}")
                else:
                    # Update existing post with new folder if different
                    if post.folder != folder:
                        post.folder = folder
                        post.save()
                        logger.info(f"✓ Updated LinkedIn post {post_data['post_id']} folder")

            except Exception as e:
                logger.error(f"Error saving LinkedIn post {item.get('postId', 'unknown')}: {str(e)}")
                continue

        logger.info(f"Saved {posts_saved} LinkedIn posts to folder {folder.name}")

    except Exception as e:
        logger.error(f"Error processing LinkedIn results: {str(e)}")


def _get_platform_results(scraper_request: ApifyScraperRequest):
    """Get processed results for a platform scraper request"""
    try:
        platform = scraper_request.platform
        results = []
        batch_job = scraper_request.batch_job

        # Build the exact folder name that was created for this scraper request
        if not scraper_request.started_at:
            logger.warning(f"Scraper request {scraper_request.id} has no started_at timestamp")
            return []

        if platform.startswith('instagram'):
            from instagram_data.models import Folder, InstagramPost
            from track_accounts.models import SourceFolder

            # Get source folder names
            source_folder_names = []
            if batch_job.source_folder_ids:
                source_folders = SourceFolder.objects.filter(id__in=batch_job.source_folder_ids)
                source_folder_names = [sf.name for sf in source_folders]

            # Create folder name with source folder names + date/time
            if source_folder_names:
                folder_base_name = ", ".join(source_folder_names)
            else:
                folder_base_name = "Instagram Scrape"

            # Format: "Brand Sources - 06/10/2025 14:00:00"
            folder_name = f"{folder_base_name} - {scraper_request.started_at.strftime('%d/%m/%Y %H:%M:%S')}"

            try:
                folder = Folder.objects.get(
                    name=folder_name,
                    project=batch_job.project
                )

                # Get posts ONLY from this specific folder
                for post in folder.posts.all():
                    results.append({
                        'id': post.id,
                        'platform': 'instagram',
                        'url': post.url,
                        'user_posted': post.user_posted,
                        'description': post.description,
                        'hashtags': post.hashtags,
                        'likes': post.likes,
                        'num_comments': post.num_comments,
                        'views': post.views,
                        'date_posted': post.date_posted.isoformat() if post.date_posted else None,
                        'content_type': post.content_type,
                        'post_id': post.post_id,
                        'shortcode': post.shortcode,
                        'thumbnail': post.thumbnail,
                        'followers': post.followers,
                        'is_verified': post.is_verified,
                        'location': post.location,
                        'created_at': post.created_at.isoformat(),
                    })
            except Folder.DoesNotExist:
                logger.warning(f"No folder found for scraper request {scraper_request.id}")

        elif platform.startswith('facebook'):
            from facebook_data.models import Folder, FacebookPost
            from track_accounts.models import SourceFolder

            # Get source folder names
            source_folder_names = []
            if batch_job.source_folder_ids:
                source_folders = SourceFolder.objects.filter(id__in=batch_job.source_folder_ids)
                source_folder_names = [sf.name for sf in source_folders]

            # Create folder name with source folder names + date/time
            if source_folder_names:
                folder_base_name = ", ".join(source_folder_names)
            else:
                folder_base_name = "Facebook Scrape"

            # Format: "Brand Sources - 06/10/2025 14:00:00"
            folder_name = f"{folder_base_name} - {scraper_request.started_at.strftime('%d/%m/%Y %H:%M:%S')}"

            try:
                folder = Folder.objects.get(
                    name=folder_name,
                    project=batch_job.project
                )

                for post in folder.posts.all():
                    results.append({
                        'id': post.id,
                        'platform': 'facebook',
                        'url': post.url,
                        'user_posted': post.user_posted,
                        'description': post.content or post.description,
                        'likes': post.likes,
                        'num_comments': post.num_comments,
                        'num_shares': post.num_shares,
                        'video_view_count': post.video_view_count,
                        'date_posted': post.date_posted.isoformat() if post.date_posted else None,
                        'post_id': post.post_id,
                        'thumbnail': post.thumbnail,
                        'created_at': post.created_at.isoformat(),
                    })
            except Folder.DoesNotExist:
                logger.warning(f"No folder found for scraper request {scraper_request.id}")

        elif platform.startswith('tiktok'):
            from tiktok_data.models import Folder, TikTokPost
            from track_accounts.models import SourceFolder

            # Get source folder names
            source_folder_names = []
            if batch_job.source_folder_ids:
                source_folders = SourceFolder.objects.filter(id__in=batch_job.source_folder_ids)
                source_folder_names = [sf.name for sf in source_folders]

            # Create folder name with source folder names + date/time
            if source_folder_names:
                folder_base_name = ", ".join(source_folder_names)
            else:
                folder_base_name = "TikTok Scrape"

            # Format: "Brand Sources - 06/10/2025 14:00:00"
            folder_name = f"{folder_base_name} - {scraper_request.started_at.strftime('%d/%m/%Y %H:%M:%S')}"

            try:
                folder = Folder.objects.get(
                    name=folder_name,
                    project=batch_job.project
                )

                for post in folder.posts.all():
                    results.append({
                        'id': post.id,
                        'platform': 'tiktok',
                        'url': post.url,
                        'user_posted': post.user_posted,
                        'description': post.description,
                        'hashtags': post.hashtags,
                        'likes': post.likes,
                        'num_comments': post.num_comments,
                        'date_posted': post.date_posted.isoformat() if post.date_posted else None,
                        'post_id': post.post_id,
                        'thumbnail': post.thumbnail,
                        'followers': post.followers,
                        'is_verified': post.is_verified,
                        'created_at': post.created_at.isoformat(),
                    })
            except Folder.DoesNotExist:
                logger.warning(f"No folder found for scraper request {scraper_request.id}")

        elif platform.startswith('linkedin'):
            from linkedin_data.models import Folder, LinkedInPost
            from track_accounts.models import SourceFolder

            # Get source folder names
            source_folder_names = []
            if batch_job.source_folder_ids:
                source_folders = SourceFolder.objects.filter(id__in=batch_job.source_folder_ids)
                source_folder_names = [sf.name for sf in source_folders]

            # Create folder name with source folder names + date/time
            if source_folder_names:
                folder_base_name = ", ".join(source_folder_names)
            else:
                folder_base_name = "LinkedIn Scrape"

            # Format: "Brand Sources - 06/10/2025 14:00:00"
            folder_name = f"{folder_base_name} - {scraper_request.started_at.strftime('%d/%m/%Y %H:%M:%S')}"

            try:
                folder = Folder.objects.get(
                    name=folder_name,
                    project=batch_job.project
                )

                for post in folder.posts.all():
                    results.append({
                        'id': post.id,
                        'platform': 'linkedin',
                        'url': post.url,
                        'user_posted': post.user_posted,
                        'description': post.description or post.post_text,
                        'likes': post.likes,
                        'num_comments': post.num_comments,
                        'num_shares': post.num_shares,
                        'date_posted': post.date_posted.isoformat() if post.date_posted else None,
                        'post_id': post.post_id,
                        'user_title': post.user_title,
                        'user_headline': post.user_headline,
                        'created_at': post.created_at.isoformat(),
                    })
            except Folder.DoesNotExist:
                logger.warning(f"No folder found for scraper request {scraper_request.id}")

        return results

    except Exception as e:
        logger.error(f"Error getting platform results: {str(e)}")
        import traceback
        traceback.print_exc()
        return []
