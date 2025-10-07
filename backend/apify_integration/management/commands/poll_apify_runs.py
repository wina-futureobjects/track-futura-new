"""
Management command to poll Apify for run status updates
This is an alternative to webhooks when a public URL is not available
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
import requests
import logging
import time

from apify_integration.models import ApifyScraperRequest, ApifyBatchJob

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Poll Apify API for run status updates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run continuously, polling every 30 seconds',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Polling interval in seconds (default: 30)',
        )

    def handle(self, *args, **options):
        continuous = options['continuous']
        interval = options['interval']

        self.stdout.write(self.style.SUCCESS('Starting Apify run polling...'))

        if continuous:
            self.stdout.write(f'Polling every {interval} seconds. Press Ctrl+C to stop.')
            try:
                while True:
                    self.poll_runs()
                    time.sleep(interval)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('\nStopping polling...'))
        else:
            self.poll_runs()

    def poll_runs(self):
        """Poll all pending/processing scraper requests"""
        # Get all scraper requests that are not completed/failed/cancelled
        active_requests = ApifyScraperRequest.objects.filter(
            status__in=['pending', 'processing']
        ).exclude(request_id__isnull=True).exclude(request_id='')

        if not active_requests.exists():
            self.stdout.write('No active runs to poll.')
            return

        self.stdout.write(f'Polling {active_requests.count()} active run(s)...')

        for scraper_request in active_requests:
            try:
                self.check_run_status(scraper_request)
            except Exception as e:
                logger.error(f"Error polling run {scraper_request.request_id}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f'Error polling run {scraper_request.id}: {str(e)}')
                )

    def check_run_status(self, scraper_request: ApifyScraperRequest):
        """Check the status of a single run"""
        config = scraper_request.config
        run_id = scraper_request.request_id

        # Get run status from Apify
        url = f"https://api.apify.com/v2/acts/{config.actor_id}/runs/{run_id}"
        headers = {
            'Authorization': f'Bearer {config.api_token}',
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            run_data = response.json()['data']
            apify_status = run_data['status']

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
            old_status = scraper_request.status

            # Update if status changed
            if new_status != old_status:
                scraper_request.status = new_status

                if new_status in ['completed', 'failed', 'cancelled']:
                    scraper_request.completed_at = timezone.now()

                scraper_request.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Run {scraper_request.id} status: {old_status} -> {new_status}'
                    )
                )

                # Process results if completed
                if new_status == 'completed':
                    self.process_results(scraper_request)

                # Update batch job status
                self.update_batch_job_status(scraper_request.batch_job)

        else:
            logger.error(
                f"Failed to get run status for {run_id}: {response.status_code} - {response.text}"
            )

    def process_results(self, scraper_request: ApifyScraperRequest):
        """Download and process results from Apify"""
        try:
            from apify_integration.views import _process_apify_results

            self.stdout.write(f'Processing results for run {scraper_request.id}...')
            _process_apify_results(scraper_request)
            self.stdout.write(self.style.SUCCESS(f'SUCCESS: Results processed for run {scraper_request.id}'))

        except Exception as e:
            logger.error(f"Error processing results for run {scraper_request.id}: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Error processing results: {str(e)}')
            )

    def update_batch_job_status(self, batch_job: ApifyBatchJob):
        """Update batch job status based on scraper request statuses"""
        try:
            # Count completed/failed requests
            total_requests = batch_job.scraper_requests.count()
            completed_requests = batch_job.scraper_requests.filter(status='completed').count()
            failed_requests = batch_job.scraper_requests.filter(status='failed').count()

            # Update counts
            batch_job.successful_requests = completed_requests
            batch_job.failed_requests = failed_requests

            # Update overall status
            if completed_requests + failed_requests >= total_requests:
                if failed_requests == 0:
                    batch_job.status = 'completed'
                    self.stdout.write(
                        self.style.SUCCESS(f'SUCCESS: Batch job {batch_job.id} completed successfully')
                    )
                else:
                    batch_job.status = 'failed'
                    self.stdout.write(
                        self.style.WARNING(
                            f'WARNING: Batch job {batch_job.id} completed with {failed_requests} failures'
                        )
                    )

                batch_job.completed_at = timezone.now()

            batch_job.save()

        except Exception as e:
            logger.error(f"Error updating batch job {batch_job.id}: {str(e)}")
