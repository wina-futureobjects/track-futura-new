"""
Management command to update stuck Apify scraper jobs

Usage:
    python manage.py update_stuck_jobs
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apify_integration.models import ApifyScraperRequest, ApifyBatchJob
import requests
import os
from datetime import timedelta


class Command(BaseCommand):
    help = 'Update stuck Apify scraper jobs by checking their status on Apify'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Check jobs from the last N days (default: 1)'
        )

    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now() - timedelta(days=days)

        # Find stuck requests (processing status but created more than 30 minutes ago)
        stuck_requests = ApifyScraperRequest.objects.filter(
            status='processing',
            created_at__lt=timezone.now() - timedelta(minutes=30)
        )

        self.stdout.write(f"Found {stuck_requests.count()} potentially stuck requests")

        api_token = os.getenv('APIFY_API_TOKEN', '')
        if not api_token:
            self.stdout.write(self.style.WARNING('No APIFY_API_TOKEN found in environment'))
            return

        updated_count = 0
        for request in stuck_requests:
            if not request.request_id:
                continue

            try:
                # Check status on Apify
                url = f"https://api.apify.com/v2/actor-runs/{request.request_id}?token={api_token}"
                response = requests.get(url)

                if response.status_code == 200:
                    data = response.json().get('data', {})
                    apify_status = data.get('status')
                    finished_at = data.get('finishedAt')

                    self.stdout.write(f"Request {request.id} ({request.request_id}): Apify status = {apify_status}")

                    # Update based on Apify status
                    if apify_status == 'SUCCEEDED':
                        request.status = 'completed'
                        request.completed_at = timezone.now()
                        request.save()
                        self.stdout.write(self.style.SUCCESS(f'[OK] Updated request {request.id} to completed'))

                        # Process results
                        try:
                            from apify_integration.views import _process_apify_results
                            _process_apify_results(request)
                            self.stdout.write(f'[OK] Processed results for request {request.id}')
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'[WARN] Error processing results: {str(e)}'))

                        updated_count += 1

                        # Update batch job
                        self._update_batch_job_status(request.batch_job)

                    elif apify_status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                        request.status = 'failed'
                        request.completed_at = timezone.now()
                        request.error_message = f"Apify run {apify_status}"
                        request.save()
                        self.stdout.write(self.style.ERROR(f'[FAIL] Updated request {request.id} to failed'))
                        updated_count += 1

                        # Update batch job
                        self._update_batch_job_status(request.batch_job)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error checking request {request.id}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'\nUpdated {updated_count} requests'))

    def _update_batch_job_status(self, batch_job):
        """Update batch job status based on its requests"""
        if not batch_job:
            return

        total = batch_job.scraper_requests.count()
        completed = batch_job.scraper_requests.filter(status='completed').count()
        failed = batch_job.scraper_requests.filter(status='failed').count()

        if completed + failed >= total:
            if failed == 0:
                batch_job.status = 'completed'
            else:
                batch_job.status = 'failed'
            batch_job.completed_at = timezone.now()
            batch_job.save()
            self.stdout.write(self.style.SUCCESS(f'[OK] Updated batch job {batch_job.id} to {batch_job.status}'))
