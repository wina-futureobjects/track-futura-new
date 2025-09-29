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
import json
import logging
import time

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
