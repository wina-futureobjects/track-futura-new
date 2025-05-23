"""
Automated Batch Scraper Services

This module provides services for automated batch scraping of social media data
from tracked accounts using BrightData's API.
"""

import logging
import requests
import json
import datetime
from typing import List, Dict, Optional, Tuple
from django.utils import timezone
from django.db import transaction
from urllib.parse import urlparse
from django.conf import settings

from .models import BatchScraperJob, ScraperRequest, BrightdataConfig
from track_accounts.models import TrackAccount
from facebook_data.models import Folder as FacebookFolder
from instagram_data.models import Folder as InstagramFolder
from linkedin_data.models import Folder as LinkedInFolder
from tiktok_data.models import Folder as TikTokFolder

logger = logging.getLogger(__name__)

class AutomatedBatchScraper:
    """
    Main service class for automated batch scraping of social media accounts
    """
    
    # Platform to folder model mapping
    PLATFORM_FOLDER_MODELS = {
        'facebook': FacebookFolder,
        'instagram': InstagramFolder,
        'linkedin': LinkedInFolder,
        'tiktok': TikTokFolder,
    }
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def create_batch_job(self, name: str, project_id: int, source_folder_ids: List[int], 
                        platforms_to_scrape: List[str] = None, num_of_posts: int = 10,
                        start_date: str = None, end_date: str = None, 
                        auto_create_folders: bool = True, output_folder_pattern: str = None) -> BatchScraperJob:
        """
        Create a new batch scraper job
        """
        if platforms_to_scrape is None:
            platforms_to_scrape = ['facebook', 'instagram', 'linkedin', 'tiktok']
        
        if output_folder_pattern is None:
            output_folder_pattern = "{platform}_{date}_{job_name}"
        
        job = BatchScraperJob.objects.create(
            name=name,
            project_id=project_id,
            source_folder_ids=source_folder_ids,
            platforms_to_scrape=platforms_to_scrape,
            num_of_posts=num_of_posts,
            start_date=datetime.datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None,
            end_date=datetime.datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None,
            auto_create_folders=auto_create_folders,
            output_folder_pattern=output_folder_pattern,
            status='pending'
        )
        
        self.logger.info(f"Created batch scraper job: {job.name} (ID: {job.id})")
        return job
    
    def execute_batch_job(self, job_id: int) -> bool:
        """
        Execute a batch scraper job
        """
        try:
            job = BatchScraperJob.objects.get(id=job_id)
            
            with transaction.atomic():
                job.status = 'processing'
                job.started_at = timezone.now()
                job.save()
            
            self.logger.info(f"Starting execution of batch job: {job.name}")
            
            # Get all tracked accounts from source folders
            accounts = self._get_accounts_from_folders(job.source_folder_ids)
            job.total_accounts = len(accounts)
            job.save()
            
            if not accounts:
                self.logger.warning(f"No accounts found in source folders for job {job.name}")
                job.status = 'completed'
                job.completed_at = timezone.now()
                job.save()
                return True
            
            # Initialize job metadata
            job_metadata = {
                'accounts_processed': [],
                'platforms_attempted': {},
                'folders_created': {},
                'start_time': timezone.now().isoformat(),
            }
            
            successful_requests = 0
            failed_requests = 0
            
            # Process each account
            for account in accounts:
                try:
                    account_result = self._process_account(job, account)
                    job_metadata['accounts_processed'].append({
                        'account_name': account.name,
                        'iac_no': account.iac_no,
                        'platforms_scraped': account_result['platforms_scraped'],
                        'requests_created': account_result['requests_created'],
                        'errors': account_result['errors']
                    })
                    
                    successful_requests += account_result['successful_requests']
                    failed_requests += account_result['failed_requests']
                    
                    # Update progress
                    job.processed_accounts += 1
                    job.successful_requests = successful_requests
                    job.failed_requests = failed_requests
                    job.save()
                    
                except Exception as e:
                    self.logger.error(f"Error processing account {account.name}: {str(e)}")
                    failed_requests += 1
                    job.failed_requests = failed_requests
                    job.save()
            
            # Complete the job
            job_metadata['end_time'] = timezone.now().isoformat()
            job_metadata['summary'] = {
                'total_accounts': job.total_accounts,
                'processed_accounts': job.processed_accounts,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests
            }
            
            job.job_metadata = job_metadata
            job.status = 'completed' if failed_requests == 0 else 'completed'  # Consider partial success as completed
            job.completed_at = timezone.now()
            job.save()
            
            self.logger.info(f"Completed batch job: {job.name}. Success: {successful_requests}, Failed: {failed_requests}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing batch job {job_id}: {str(e)}")
            try:
                job = BatchScraperJob.objects.get(id=job_id)
                job.status = 'failed'
                job.error_log = str(e)
                job.completed_at = timezone.now()
                job.save()
            except:
                pass
            return False
    
    def _get_accounts_from_folders(self, folder_ids: List[int]) -> List[TrackAccount]:
        """
        Get all tracked accounts from the project (folders have been removed)
        """
        # Since folders have been removed, we'll get all accounts from the project
        # The folder_ids parameter is kept for backward compatibility but ignored
        accounts = TrackAccount.objects.all()
        self.logger.info(f"Found {accounts.count()} accounts (folders have been removed)")
        return list(accounts)
    
    def _process_account(self, job: BatchScraperJob, account: TrackAccount) -> Dict:
        """
        Process a single account for all specified platforms
        """
        result = {
            'platforms_scraped': [],
            'requests_created': [],
            'successful_requests': 0,
            'failed_requests': 0,
            'errors': []
        }
        
        for platform in job.platforms_to_scrape:
            try:
                url = self._get_platform_url(account, platform)
                if not url:
                    self.logger.debug(f"No {platform} URL found for account {account.name}")
                    continue
                
                # Get platform-specific configuration
                config = self._get_platform_config(platform)
                if not config:
                    error_msg = f"No active {platform} configuration found"
                    self.logger.error(error_msg)
                    result['errors'].append(error_msg)
                    result['failed_requests'] += 1
                    continue
                
                # Create or get output folder
                folder_id = self._get_or_create_output_folder(job, platform, account)
                
                # Create scraper request
                scraper_request = self._create_scraper_request(
                    job, account, platform, url, config, folder_id
                )
                
                if scraper_request:
                    result['platforms_scraped'].append(platform)
                    result['requests_created'].append(scraper_request.id)
                    result['successful_requests'] += 1
                    
                    # Trigger the actual scrape
                    self._trigger_scrape(scraper_request)
                else:
                    result['failed_requests'] += 1
                    
            except Exception as e:
                error_msg = f"Error processing {platform} for {account.name}: {str(e)}"
                self.logger.error(error_msg)
                result['errors'].append(error_msg)
                result['failed_requests'] += 1
        
        return result
    
    def _get_platform_url(self, account: TrackAccount, platform: str) -> Optional[str]:
        """
        Extract the appropriate platform URL from the account
        """
        url_mapping = {
            'facebook': account.facebook_link,
            'instagram': account.instagram_link,
            'linkedin': account.linkedin_link,
            'tiktok': account.tiktok_link,
        }
        
        url = url_mapping.get(platform)
        if url and url.strip():
            return url.strip()
        return None
    
    def _get_platform_config(self, platform: str) -> Optional[BrightdataConfig]:
        """
        Get the active configuration for a specific platform
        """
        return BrightdataConfig.objects.filter(platform=platform, is_active=True).first()
    
    def _get_or_create_output_folder(self, job: BatchScraperJob, platform: str, account: TrackAccount) -> Optional[int]:
        """
        Get or create an output folder for the scraped data
        """
        if not job.auto_create_folders:
            return None
        
        try:
            # Generate folder name using the pattern
            folder_name = job.output_folder_pattern.format(
                platform=platform.title(),
                date=timezone.now().strftime('%Y-%m-%d'),
                job_name=job.name,
                account_name=account.name,
                iac_no=account.iac_no
            )
            
            # Get the appropriate folder model for this platform
            FolderModel = self.PLATFORM_FOLDER_MODELS.get(platform)
            if not FolderModel:
                self.logger.error(f"No folder model found for platform: {platform}")
                return None
            
            # Create or get the folder
            folder, created = FolderModel.objects.get_or_create(
                name=folder_name,
                defaults={'project_id': job.project_id}
            )
            
            if created:
                self.logger.info(f"Created new {platform} folder: {folder_name}")
            
            return folder.id
            
        except Exception as e:
            self.logger.error(f"Error creating output folder for {platform}: {str(e)}")
            return None
    
    def _create_scraper_request(self, job: BatchScraperJob, account: TrackAccount, 
                              platform: str, url: str, config: BrightdataConfig, 
                              folder_id: Optional[int]) -> Optional[ScraperRequest]:
        """
        Create a scraper request for the account and platform
        """
        try:
            scraper_request = ScraperRequest.objects.create(
                config=config,
                batch_job=job,
                platform=platform,
                content_type='post',  # Default to posts
                target_url=url,
                account_name=account.name,
                iac_no=account.iac_no,
                num_of_posts=job.num_of_posts,
                start_date=job.start_date,
                end_date=job.end_date,
                folder_id=folder_id,
                status='pending'
            )
            
            self.logger.info(f"Created scraper request for {account.name} on {platform}")
            return scraper_request
            
        except Exception as e:
            self.logger.error(f"Error creating scraper request: {str(e)}")
            return None
    
    def _trigger_scrape(self, scraper_request: ScraperRequest) -> bool:
        """
        Trigger the actual scrape using BrightData API
        """
        try:
            # Prepare the API request based on platform
            platform_trigger_methods = {
                'facebook': self._trigger_facebook_scrape,
                'instagram': self._trigger_instagram_scrape,
                'linkedin': self._trigger_linkedin_scrape,
                'tiktok': self._trigger_tiktok_scrape,
            }
            
            trigger_method = platform_trigger_methods.get(scraper_request.platform)
            if not trigger_method:
                self.logger.error(f"No trigger method found for platform: {scraper_request.platform}")
                return False
            
            return trigger_method(scraper_request)
            
        except Exception as e:
            self.logger.error(f"Error triggering scrape for request {scraper_request.id}: {str(e)}")
            scraper_request.status = 'failed'
            scraper_request.error_message = str(e)
            scraper_request.save()
            return False
    
    def _make_brightdata_request(self, scraper_request: ScraperRequest, payload: List[Dict]) -> bool:
        """
        Make the actual API request to BrightData
        """
        try:
            config = scraper_request.config
            
            # Import Django settings to get base URL and webhook token
            base_url = getattr(settings, 'BRIGHTDATA_BASE_URL', 'http://localhost:8000')
            webhook_token = getattr(settings, 'BRIGHTDATA_WEBHOOK_TOKEN', 'your-webhook-secret-token')
            
            url = "https://api.brightdata.com/datasets/v3/trigger"
            headers = {
                "Authorization": f"Bearer {config.api_token}",
                "Content-Type": "application/json",
            }
            params = {
                "dataset_id": config.dataset_id,
                "endpoint": f"{base_url}/api/brightdata/webhook/",
                "auth_header": f"Bearer {webhook_token}",
                "notify": f"{base_url}/api/brightdata/notify/",
                "format": "json",
                "uncompressed_webhook": "true",
                "include_errors": "true",
            }
            
            # Store the request payload
            scraper_request.request_payload = payload
            scraper_request.status = 'processing'
            scraper_request.save()
            
            # Make the API request
            response = requests.post(url, headers=headers, params=params, json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                scraper_request.request_id = response_data.get('snapshot_id') or response_data.get('request_id')
                scraper_request.response_metadata = response_data
                scraper_request.save()
                
                self.logger.info(f"Successfully triggered scrape for request {scraper_request.id}")
                return True
            else:
                error_msg = f"BrightData API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                scraper_request.status = 'failed'
                scraper_request.error_message = error_msg
                scraper_request.save()
                return False
                
        except Exception as e:
            error_msg = f"Error making BrightData request: {str(e)}"
            self.logger.error(error_msg)
            scraper_request.status = 'failed'
            scraper_request.error_message = error_msg
            scraper_request.save()
            return False
    
    def _trigger_facebook_scrape(self, scraper_request: ScraperRequest) -> bool:
        """Trigger Facebook scrape"""
        payload = [{
            "url": scraper_request.target_url,
            "num_of_posts": scraper_request.num_of_posts,
            "posts_to_not_include": [],
            "start_date": scraper_request.start_date.strftime('%m-%d-%Y') if scraper_request.start_date else "",
            "end_date": scraper_request.end_date.strftime('%m-%d-%Y') if scraper_request.end_date else "",
        }]
        return self._make_brightdata_request(scraper_request, payload)
    
    def _trigger_instagram_scrape(self, scraper_request: ScraperRequest) -> bool:
        """Trigger Instagram scrape"""
        payload = [{
            "url": scraper_request.target_url,
            "num_of_posts": scraper_request.num_of_posts,
            "start_date": scraper_request.start_date.strftime('%m-%d-%Y') if scraper_request.start_date else "",
            "end_date": scraper_request.end_date.strftime('%m-%d-%Y') if scraper_request.end_date else "",
        }]
        return self._make_brightdata_request(scraper_request, payload)
    
    def _trigger_linkedin_scrape(self, scraper_request: ScraperRequest) -> bool:
        """Trigger LinkedIn scrape"""
        payload = [{
            "url": scraper_request.target_url,
            "num_of_posts": scraper_request.num_of_posts,
            "start_date": scraper_request.start_date.strftime('%m-%d-%Y') if scraper_request.start_date else "",
            "end_date": scraper_request.end_date.strftime('%m-%d-%Y') if scraper_request.end_date else "",
        }]
        return self._make_brightdata_request(scraper_request, payload)
    
    def _trigger_tiktok_scrape(self, scraper_request: ScraperRequest) -> bool:
        """Trigger TikTok scrape"""
        payload = [{
            "url": scraper_request.target_url,
            "num_of_posts": scraper_request.num_of_posts,
            "start_date": scraper_request.start_date.strftime('%m-%d-%Y') if scraper_request.start_date else "",
            "end_date": scraper_request.end_date.strftime('%m-%d-%Y') if scraper_request.end_date else "",
        }]
        return self._make_brightdata_request(scraper_request, payload)

# Convenience function for external use
def create_and_execute_batch_job(name: str, project_id: int, source_folder_ids: List[int], 
                                 platforms_to_scrape: List[str] = None, **kwargs) -> Tuple[BatchScraperJob, bool]:
    """
    Create and immediately execute a batch scraper job
    """
    scraper = AutomatedBatchScraper()
    job = scraper.create_batch_job(name, project_id, source_folder_ids, platforms_to_scrape, **kwargs)
    success = scraper.execute_batch_job(job.id)
    return job, success 