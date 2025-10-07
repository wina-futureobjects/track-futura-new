#!/usr/bin/env python3
"""
Sync all Apify scraper requests and process completed results
"""
import os
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyScraperRequest
from apify_integration.views import _process_apify_results
from django.utils import timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_all_apify_jobs():
    """Sync all pending Apify jobs and process completed ones"""

    # Get all processing/pending requests
    pending_requests = ApifyScraperRequest.objects.filter(
        status__in=['processing', 'pending']
    ).order_by('id')

    logger.info(f"Found {pending_requests.count()} pending/processing requests")

    for request in pending_requests:
        logger.info(f"\n=== Processing Request {request.id} ===")
        logger.info(f"Request ID: {request.request_id}")
        logger.info(f"Platform: {request.platform}")
        logger.info(f"Current Status: {request.status}")
        logger.info(f"Batch Job: {request.batch_job_id}")

        if not request.request_id:
            logger.warning(f"No request_id for {request.id}, skipping")
            continue

        try:
            config = request.config
            run_info_url = f'https://api.apify.com/v2/acts/{config.actor_id}/runs/{request.request_id}'
            headers = {'Authorization': f'Bearer {config.api_token}'}

            # Check run status
            run_response = requests.get(run_info_url, headers=headers, timeout=10)
            if run_response.status_code != 200:
                logger.error(f"Failed to fetch run info: {run_response.status_code}")
                continue

            run_data = run_response.json()['data']
            apify_status = run_data.get('status')
            started_at = run_data.get('startedAt')
            finished_at = run_data.get('finishedAt')
            dataset_id = run_data.get('defaultDatasetId')

            logger.info(f"Apify Status: {apify_status}")
            logger.info(f"Dataset ID: {dataset_id}")

            # Map Apify status to our status
            status_mapping = {
                'READY': 'processing',
                'RUNNING': 'processing',
                'SUCCEEDED': 'completed',
                'FAILED': 'failed',
                'ABORTED': 'cancelled',
                'TIMED_OUT': 'failed'
            }

            new_status = status_mapping.get(apify_status, 'processing')

            # Update request status
            if request.status != new_status:
                request.status = new_status
                if new_status in ['completed', 'failed', 'cancelled']:
                    request.completed_at = timezone.now()
                request.save()
                logger.info(f"Updated status: {request.status} -> {new_status}")

            # Process results if completed
            if new_status == 'completed':
                try:
                    logger.info("Processing results...")
                    _process_apify_results(request)
                    logger.info("✅ Results processed successfully")
                except Exception as e:
                    logger.error(f"❌ Error processing results: {e}")

        except Exception as e:
            logger.error(f"❌ Error syncing request {request.id}: {e}")
            continue

    # Summary
    completed_count = ApifyScraperRequest.objects.filter(status='completed').count()
    processing_count = ApifyScraperRequest.objects.filter(status='processing').count()
    failed_count = ApifyScraperRequest.objects.filter(status='failed').count()

    logger.info(f"\n=== SYNC SUMMARY ===")
    logger.info(f"Completed: {completed_count}")
    logger.info(f"Processing: {processing_count}")
    logger.info(f"Failed: {failed_count}")

if __name__ == "__main__":
    sync_all_apify_jobs()