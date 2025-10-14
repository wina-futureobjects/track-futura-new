"""
Clean webhook handler implementation based on reference project
Handles BrightData webhook events for data delivery
"""

import json
import time
import logging
import traceback
import requests
from datetime import datetime
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import BrightDataWebhookEvent, BrightDataScraperRequest
from workflow.models import ScrapingJob

logger = logging.getLogger(__name__)


@csrf_exempt
def brightdata_webhook(request):
    """
    Safe webhook handler that always captures raw payload first, then validates
    """
    # 1. CONFIRM DJANGO RECEIVES THE REQUEST
    logger.info("=" * 80)
    logger.info(f"🎯 WEBHOOK RECEIVED AT {datetime.now()}")
    logger.info("=" * 80)
    logger.info(f"📡 Method: {request.method}")
    logger.info(f"🌐 Client IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
    logger.info(f"🔗 URL: {request.build_absolute_uri()}")
    logger.info(f"📋 Content-Type: {request.content_type}")
    logger.info(f"📏 Content-Length: {request.META.get('CONTENT_LENGTH', 'unknown')}")
    logger.info(f"📨 Headers: {dict(request.headers)}")
    logger.info(f"🔍 Query Params: {dict(request.GET)}")

    # 2. CHECK HTTP METHOD
    if request.method != 'POST':
        logger.error(f"❌ Invalid method: {request.method}. Expected POST")
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    start_time = time.time()
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')
    webhook_event = None

    try:
        # 3. ALWAYS SAVE RAW PAYLOAD FIRST (for debugging)
        logger.info("📦 CAPTURING RAW PAYLOAD:")
        try:
            raw_body = request.body.decode("utf-8")
            logger.info(f"Raw body: {raw_body[:1000]}...")  # First 1000 chars
        except UnicodeDecodeError as e:
            logger.error(f"❌ Unicode decode error: {e}")
            raw_body = str(request.body)
            logger.info(f"Raw body (bytes): {raw_body[:1000]}...")

        # 4. PARSE JSON (but don't fail yet)
        logger.info("🔍 PARSING JSON PAYLOAD:")
        data = None
        json_error = None

        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                logger.info(f"✅ JSON parsed successfully")
                logger.info(f"📊 Data type: {type(data)}")

                # Add robust type checks
                if not isinstance(data, (list, dict)):
                    logger.warning(f"⚠️  JSON is not list/dict, wrapping as list: {type(data)}")
                    data = [data]  # Wrap single items in list

                if isinstance(data, dict):
                    logger.info(f"📋 Data keys: {list(data.keys())}")
                elif isinstance(data, list):
                    logger.info(f"📋 List length: {len(data)}")
                logger.info(f"📄 Parsed JSON: {str(data)[:500]}...")  # First 500 chars
            except json.JSONDecodeError as e:
                json_error = str(e)
                logger.error(f"❌ JSON decode error: {e}")
                logger.error(f"❌ Raw body that failed: {raw_body}")
                # Don't return error yet - save the raw payload first
        else:
            logger.error(f"❌ Unsupported content type: {request.content_type}")
            logger.error(f"❌ Expected: application/json")
            # Still save the raw payload for debugging

        # 5. EXTRACT METADATA
        logger.info("🏷️ EXTRACTING METADATA:")
        snapshot_id = _extract_snapshot_id_from_request_and_data(request, data)

        # Improved platform detection
        platform = (request.headers.get('X-Platform') or
                   request.headers.get('x-platform') or
                   request.GET.get('platform'))

        # If no platform specified, try to detect from data content
        if not platform and data:
            platform = _detect_platform_from_data(data)

        logger.info(f"📱 Platform detected: {platform}")
        logger.info(f"📸 Snapshot ID: {snapshot_id}")

        # 6. ALWAYS SAVE TO DATABASE FIRST (even if validation fails)
        logger.info("💾 SAVING RAW PAYLOAD TO DATABASE:")
        try:
            # Better test webhook detection
            is_test_webhook = (request.headers.get('X-Brightdata-Test') or
                             request.headers.get('x-brightdata-test') or
                             not snapshot_id)

            # Determine status based on what we have
            if json_error:
                status = 'json_error'
            elif is_test_webhook:
                status = 'test_webhook'
            else:
                status = 'pending'

            webhook_event = BrightDataWebhookEvent.objects.create(
                event_id=f"{snapshot_id}_{int(time.time())}" if snapshot_id else f"webhook_{int(time.time())}",
                platform=platform,
                snapshot_id=snapshot_id,
                raw_data=data if data else {'raw_body': raw_body, 'json_error': json_error},
                status=status,
                error_message=json_error if json_error else None
            )
            logger.info(f"✅ WebhookEvent created: ID {webhook_event.id}")
            logger.info(f"✅ Platform: {webhook_event.platform}")
            logger.info(f"✅ Snapshot ID: {webhook_event.snapshot_id}")
            logger.info(f"✅ Status: {webhook_event.status}")
            logger.info(f"✅ Created at: {webhook_event.created_at}")
            if json_error:
                logger.info(f"✅ Error message: {webhook_event.error_message}")
        except Exception as e:
            logger.error(f"❌ Failed to save webhook event to database: {str(e)}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            # Even if we can't save to DB, we should still try to process

        # 7. NOW VALIDATE AND PROCESS
        if json_error:
            logger.error(f"❌ JSON validation failed: {json_error}")
            processing_time = round(time.time() - start_time, 3)
            logger.info("=" * 80)
            return JsonResponse({
                'status': 'json_error',
                'message': 'Invalid JSON payload',
                'details': json_error,
                'webhook_event_id': webhook_event.id if webhook_event else None,
                'processing_time': processing_time
            }, status=400)

        # Check if this is a test payload
        if is_test_webhook:
            logger.warning(f"🧪 TEST WEBHOOK DETECTED")
            logger.warning(f"📋 Test payload data: {data}")
            logger.warning(f"📨 Headers: {dict(request.headers)}")
            logger.warning(f"🔍 Query params: {dict(request.GET)}")

            # Update status to indicate it was processed
            if webhook_event:
                webhook_event.status = 'test_processed'
                webhook_event.save()

            processing_time = round(time.time() - start_time, 3)
            logger.info(f"✅ Test webhook received successfully in {processing_time}s")
            logger.info("=" * 80)

            return JsonResponse({
                'status': 'test_received',
                'message': 'Test webhook received successfully',
                'webhook_event_id': webhook_event.id if webhook_event else None,
                'processing_time': processing_time,
                'note': 'This was a test webhook from BrightData. Real scraping webhooks will contain snapshot_id.'
            })

        logger.info(f"✅ Metadata extracted successfully")

        # 8. PROCESS REAL WEBHOOK DATA
        # Handle BrightData file_url payload format
        if isinstance(data, dict) and 'file_url' in data:
            logger.info(f"BrightData sent file_url: {data['file_url']}")
            try:
                response = requests.get(data['file_url'], timeout=30)
                response.raise_for_status()
                posts_data = response.json()
                logger.info(f"Successfully fetched {len(posts_data) if isinstance(posts_data, list) else 1} posts from file_url")
                # Update the data with the fetched content
                data['fetched_data'] = posts_data
            except Exception as e:
                logger.error(f"Failed to fetch data from file_url: {str(e)}")
                if webhook_event:
                    webhook_event.status = 'file_url_error'
                    webhook_event.error_message = f'Failed to fetch data from file_url: {str(e)}'
                    webhook_event.save()
                return JsonResponse({
                    'status': 'error',
                    'message': f'Failed to fetch data from file_url: {str(e)}',
                    'webhook_event_id': webhook_event.id if webhook_event else None,
                    'snapshot_id': snapshot_id
                }, status=500)
        else:
            # Direct data format
            posts_data = data if isinstance(data, list) else data.get('data', [])
            logger.info(f"Processing direct data format with {len(posts_data) if isinstance(posts_data, list) else 1} items")

        # 9. PROCESS THE ACTUAL DATA
        logger.info("🔄 PROCESSING WEBHOOK DATA:")

        # Find ScrapingJob directly by snapshot_id
        scrape_job = None
        try:
            scrape_job = ScrapingJob.objects.filter(request_id=snapshot_id).first()
            if scrape_job:
                logger.info(f"✅ Found ScrapingJob directly by request_id: {scrape_job.id}")
                # Update job status to processing
                scrape_job.status = 'processing'
                scrape_job.started_at = timezone.now()
                scrape_job.save()
            else:
                logger.warning(f"⚠️  No ScrapingJob found with request_id: {snapshot_id}")
        except Exception as e:
            logger.warning(f"⚠️  Error finding ScrapingJob: {str(e)}")

        # Find associated scraper requests for this snapshot_id (for backward compatibility)
        scraper_requests = []
        try:
            from brightdata_integration.models import BrightDataScraperRequest
            scraper_requests = list(BrightDataScraperRequest.objects.filter(
                snapshot_id=snapshot_id
            ).order_by('created_at'))
            logger.info(f"📋 Found {len(scraper_requests)} scraper requests for snapshot_id: {snapshot_id}")
        except Exception as e:
            logger.warning(f"⚠️  Error finding scraper requests: {str(e)}")

        # Process the data
        try:
            logger.info(f"🔄 Calling _process_webhook_data with platform: {platform}")
            success = _process_webhook_data(posts_data, platform, scraper_requests, scrape_job)

            if success:
                logger.info(f"✅ Data processing completed successfully")
                # Update job status to completed
                if scrape_job:
                    scrape_job.status = 'completed'
                    scrape_job.completed_at = timezone.now()
                    scrape_job.save()
                    logger.info(f"✅ Updated ScrapingJob {scrape_job.id} to completed")
            else:
                logger.warning(f"⚠️  Data processing completed with warnings")
                if scrape_job:
                    scrape_job.status = 'failed'
                    scrape_job.error_message = 'Data processing failed'
                    scrape_job.save()

        except Exception as e:
            logger.error(f"❌ Error processing data: {str(e)}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            if webhook_event:
                webhook_event.status = 'processing_error'
                webhook_event.error_message = f'Data processing error: {str(e)}'
                webhook_event.save()
            if scrape_job:
                scrape_job.status = 'failed'
                scrape_job.error_message = str(e)
                scrape_job.save()
            return JsonResponse({
                'status': 'processing_error',
                'message': f'Error processing data: {str(e)}',
                'webhook_event_id': webhook_event.id if webhook_event else None,
                'snapshot_id': snapshot_id,
                'processing_time': round(time.time() - start_time, 3)
            }, status=500)

        # 10. UPDATE STATUS TO PROCESSED
        if webhook_event:
            webhook_event.status = 'processed'
            webhook_event.processed_at = timezone.now()
            webhook_event.save()
            logger.info(f"✅ WebhookEvent status updated to 'processed'")

        processing_time = round(time.time() - start_time, 3)
        logger.info(f"✅ Webhook processed successfully: {snapshot_id} in {processing_time}s")
        logger.info("=" * 80)

        return JsonResponse({
            'status': 'processed',
            'message': 'Webhook data processed successfully',
            'webhook_event_id': webhook_event.id if webhook_event else None,
            'snapshot_id': snapshot_id,
            'processing_time': processing_time
        })

    except Exception as e:
        logger.error(f"❌ Error processing webhook: {str(e)}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        logger.error(f"❌ Traceback: {traceback.format_exc()}")

        # Wrap webhook_event references safely
        if webhook_event:
            webhook_event.status = 'error'
            webhook_event.error_message = str(e)
            webhook_event.save()
            logger.info(f"✅ WebhookEvent status updated to 'error'")

        logger.error("=" * 80)
        return JsonResponse({
            'error': 'Internal server error',
            'details': str(e),
            'webhook_event_id': webhook_event.id if webhook_event else None,
            'processing_time': round(time.time() - start_time, 3)
        }, status=500)


def _extract_snapshot_id_from_request_and_data(req, payload):
    """
    Robust snapshot ID extraction from multiple sources
    """
    try:
        headers = req.headers or {}
        # Candidate sources ordered by precedence
        candidates = [
            # New BrightData delivery headers
            headers.get('Snapshot-Id'),
            headers.get('snapshot-id'),
            headers.get('Dca-Collection-Id'),
            headers.get('dca-collection-id'),
            headers.get('X-Snapshot-Id'),
            headers.get('X-Brightdata-Snapshot-Id'),
            headers.get('X-BrightData-Snapshot-Id'),
            headers.get('X-Request-Id'),
            headers.get('X-Brightdata-Request-Id'),
            headers.get('X-BrightData-Request-Id'),
            headers.get('x-snapshot-id'),
            headers.get('x-request-id'),
            # Query params fallbacks
            req.GET.get('snapshot_id'),
            req.GET.get('id'),
            req.GET.get('request_id'),
            req.GET.get('snapshotId'),
            req.GET.get('requestId'),
        ]

        # From JSON body (top-level)
        if isinstance(payload, dict):
            candidates.extend([
                payload.get('snapshot_id'),
                payload.get('request_id'),
                payload.get('id'),
                payload.get('snapshotId'),
                payload.get('requestId'),
                payload.get('Snapshot-Id'),
                payload.get('Request-Id'),
                payload.get('Dca-Collection-Id'),
                payload.get('job_id'),
                payload.get('jobId'),
            ])

            meta = payload.get('metadata') or payload.get('meta') or {}
            if isinstance(meta, dict):
                candidates.extend([
                    meta.get('snapshot_id'),
                    meta.get('request_id'),
                    meta.get('id'),
                    meta.get('snapshotId'),
                    meta.get('requestId'),
                ])
        elif isinstance(payload, list) and payload:
            first = payload[0]
            if isinstance(first, dict):
                candidates.extend([
                    first.get('snapshot_id'),
                    first.get('request_id'),
                    first.get('id'),
                    first.get('snapshotId'),
                    first.get('requestId'),
                    first.get('Snapshot-Id'),
                    first.get('Request-Id'),
                    first.get('Dca-Collection-Id'),
                    first.get('job_id'),
                    first.get('jobId'),
                ])
                meta = first.get('metadata') or first.get('meta') or {}
                if isinstance(meta, dict):
                    candidates.extend([
                        meta.get('snapshot_id'),
                        meta.get('request_id'),
                        meta.get('id'),
                        meta.get('snapshotId'),
                        meta.get('requestId'),
                    ])

        for candidate in candidates:
            if candidate is not None and str(candidate).strip():
                return str(candidate)
    except Exception as e:
        logger.warning(f"⚠️  Snapshot ID extraction failed: {e}")
    return None


def _detect_platform_from_data(data):
    """
    Improved platform detection from data content
    """
    if not data:
        return 'instagram'  # Default fallback

    # If data is a list, check the first item
    if isinstance(data, list) and len(data) > 0:
        first_item = data[0]
    elif isinstance(data, dict):
        # If data is a dict, check if it has 'data' key
        if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
            first_item = data['data'][0]
        else:
            first_item = data
    else:
        return 'instagram'  # Default fallback

    if not isinstance(first_item, dict):
        return 'instagram'  # Default fallback

    # LinkedIn-specific field detection (more specific)
    linkedin_fields = [
        'user_id', 'user_url', 'user_title', 'post_text', 'post_text_html',
        'num_likes', 'num_shares', 'user_followers', 'user_posts', 'user_articles',
        'num_connections', 'post_type', 'account_type', 'external_link_data',
        'embedded_links', 'document_cover_image', 'document_page_count',
        'tagged_companies', 'tagged_people', 'repost_data', 'author_profile_pic'
    ]

    # Facebook-specific field detection
    facebook_fields = [
        'facebook_id', 'facebook_url', 'facebook_user', 'page_name', 'profile_id',
        'page_intro', 'page_category', 'page_logo', 'page_external_website',
        'page_likes', 'page_followers', 'page_is_verified', 'page_phone',
        'page_email', 'page_creation_time', 'page_reviews_score',
        'page_reviewers_amount', 'page_price_range', 'attachments_data',
        'post_external_image', 'page_url', 'header_image', 'avatar_image_url',
        'profile_handle', 'is_sponsored', 'shortcode', 'is_page', 'about',
        'active_ads_urls', 'delegate_page_id'
    ]

    # Instagram-specific field detection
    instagram_fields = [
        'pk', 'shortcode', 'user_pk', 'username', 'full_name', 'thumbnail_url',
        'video_url', 'is_video', 'media_type', 'product_type', 'carousel_media',
        'taken_at_timestamp', 'like_count', 'comment_count', 'view_count',
        'caption', 'location', 'tagged_users', 'accessibility_caption'
    ]

    # TikTok-specific field detection
    tiktok_fields = [
        'video_id', 'video_url', 'author_username', 'author_nickname',
        'video_description', 'music_title', 'music_author', 'video_duration',
        'cover_url', 'dynamic_cover', 'play_count', 'download_count',
        'share_count', 'hashtags', 'video_definition'
    ]

    # Count matches for each platform
    linkedin_matches = sum(1 for field in linkedin_fields if field in first_item)
    facebook_matches = sum(1 for field in facebook_fields if field in first_item)
    instagram_matches = sum(1 for field in instagram_fields if field in first_item)
    tiktok_matches = sum(1 for field in tiktok_fields if field in first_item)

    # Determine platform based on highest match count
    matches = {
        'linkedin': linkedin_matches,
        'facebook': facebook_matches,
        'instagram': instagram_matches,
        'tiktok': tiktok_matches
    }

    detected_platform = max(matches, key=matches.get)
    max_matches = matches[detected_platform]

    logger.info(f"Platform detection matches: {matches}")

    # Only return detected platform if we have at least 2 matches
    if max_matches >= 2:
        return detected_platform

    # Check URL patterns as fallback
    url = first_item.get('url', '') or first_item.get('post_url', '') or first_item.get('user_url', '')
    if 'linkedin.com' in url:
        return 'linkedin'
    elif 'facebook.com' in url:
        return 'facebook'
    elif 'instagram.com' in url:
        return 'instagram'
    elif 'tiktok.com' in url:
        return 'tiktok'

    return 'instagram'  # Default fallback


def _process_webhook_data(data, platform: str, scraper_requests, scrape_job=None):
    """
    Process incoming webhook data - delegates to existing processing functions
    """
    try:
        # Import existing processing function
        from .views import _process_brightdata_results

        # Get the first scraper request for folder context
        scraper_request = scraper_requests[0] if scraper_requests else None
        target_folder_id = scraper_request.folder_id if scraper_request else None

        # Call existing processing function
        success = _process_brightdata_results(data, platform, scraper_request, target_folder_id)

        return success

    except Exception as e:
        logger.error(f"Error in _process_webhook_data: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
