"""
BrightData Integration Services

This module provides services for interacting with the BrightData API
for social media scraping operations.
"""

import logging
import os
import requests
import json
from typing import Optional, Dict, Any, List
from django.conf import settings
from django.utils import timezone

from .models import BrightDataConfig, BrightDataBatchJob, BrightDataScraperRequest

logger = logging.getLogger(__name__)


class BrightDataAutomatedBatchScraper:
    """Service for managing BrightData batch scraping operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.brightdata.com/datasets/v3"
        
        # Platform-specific dataset configurations
        self.platform_datasets = {
            'instagram': 'gd_l7q7dkf244hwps8lu0',  # Instagram dataset ID
            'facebook': 'gd_l7q7dkf244hwps8lu1',   # Facebook dataset ID
            'tiktok': 'gd_l7q7dkf244hwps8lu2',     # TikTok dataset ID
            'linkedin': 'gd_l7q7dkf244hwps8lu3',   # LinkedIn dataset ID
        }

    def create_batch_job(self, name: str, project_id: int, source_folder_ids: List[int], 
                        platforms_to_scrape: List[str], content_types_to_scrape: Dict[str, List[str]], 
                        num_of_posts: int = 10, **kwargs) -> Optional[BrightDataBatchJob]:
        """
        Create a new batch scraping job
        
        Args:
            name: Job name
            project_id: Project ID
            source_folder_ids: List of source folder IDs for data storage
            platforms_to_scrape: List of platforms to scrape
            content_types_to_scrape: Dict mapping platforms to content types
            num_of_posts: Number of posts to scrape per source
            **kwargs: Additional configuration parameters
            
        Returns:
            BrightDataBatchJob: Created batch job or None if failed
        """
        try:
            from users.models import Project
            
            project = Project.objects.get(id=project_id)
            
            batch_job = BrightDataBatchJob.objects.create(
                name=name,
                project=project,
                source_folder_ids=source_folder_ids,
                platforms_to_scrape=platforms_to_scrape,
                content_types_to_scrape=content_types_to_scrape,
                num_of_posts=num_of_posts,
                start_date=kwargs.get('start_date'),
                end_date=kwargs.get('end_date'),
                platform_params=kwargs.get('platform_params', {}),
                created_by=kwargs.get('created_by')
            )
            
            self.logger.info(f"Created batch job: {batch_job.id} - {name}")
            return batch_job
            
        except Exception as e:
            self.logger.error(f"Error creating batch job: {str(e)}")
            return None

    def execute_batch_job(self, batch_job_id: int) -> bool:
        """
        Execute a batch scraping job
        
        Args:
            batch_job_id: ID of the batch job to execute
            
        Returns:
            bool: True if execution started successfully, False otherwise
        """
        try:
            batch_job = BrightDataBatchJob.objects.get(id=batch_job_id)
            
            # Update job status
            batch_job.status = 'processing'
            batch_job.started_at = timezone.now()
            batch_job.save()
            
            self.logger.info(f"Executing batch job: {batch_job.id}")
            
            # Process each platform
            all_success = True
            for platform in batch_job.platforms_to_scrape:
                success = self._process_platform_scraping(batch_job, platform)
                if not success:
                    all_success = False
                    self.logger.error(f"Failed to process platform: {platform}")
            
            if all_success:
                self.logger.info(f"Successfully started all scraping for batch job: {batch_job.id}")
                return True
            else:
                batch_job.status = 'failed'
                batch_job.error_log = "Some platforms failed to start"
                batch_job.save()
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing batch job {batch_job_id}: {str(e)}")
            return False

    def _process_platform_scraping(self, batch_job: BrightDataBatchJob, platform: str) -> bool:
        """Process scraping for a specific platform"""
        try:
            # Get configuration for this platform
            config = BrightDataConfig.objects.filter(
                platform=platform,
                is_active=True
            ).first()
            
            if not config:
                self.logger.error(f"No active config found for platform: {platform}")
                return False
            
            # Get the actual target URL from platform params or workflow
            target_url = self._get_target_url_for_platform(batch_job, platform)
            if not target_url:
                self.logger.error(f"No target URL found for platform {platform} in batch job {batch_job.id}")
                return False
            
            # Create scraper request
            scraper_request = BrightDataScraperRequest.objects.create(
                config=config,
                batch_job=batch_job,
                platform=platform,
                content_type='posts',
                target_url=target_url,
                source_name=f'{platform.title()} Scraper',
                status='pending'
            )
            
            # Prepare request payload
            payload = self._prepare_request_payload(platform, batch_job, scraper_request)
            
            # Execute the scraping request
            success = self._execute_brightdata_request(scraper_request, payload)
            
            if success:
                self.logger.info(f"Successfully started scraping for {platform}")
                return True
            else:
                self.logger.error(f"Failed to start scraping for {platform}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing platform {platform}: {str(e)}")
            return False

    def _get_target_url_for_platform(self, batch_job: BrightDataBatchJob, platform: str) -> str:
        """Get the actual target URL for scraping from batch job data"""
        try:
            # Check platform params first
            platform_params = batch_job.platform_params.get(platform, {})
            
            # Option 1: Direct URL from platform params
            if 'url' in platform_params:
                return platform_params['url']
            
            # Option 2: Get URL from InputCollection if available
            if 'input_collection_id' in platform_params:
                try:
                    from workflow.models import InputCollection
                    input_collection = InputCollection.objects.get(id=platform_params['input_collection_id'])
                    
                    if input_collection.urls and len(input_collection.urls) > 0:
                        return input_collection.urls[0]
                        
                except Exception as e:
                    self.logger.error(f"Error getting URL from InputCollection: {str(e)}")
            
            # Option 3: Get URL from ScrapingJob if available
            try:
                from workflow.models import ScrapingJob
                scraping_jobs = ScrapingJob.objects.filter(batch_job=batch_job, platform=platform.lower())
                if scraping_jobs.exists():
                    scraping_job = scraping_jobs.first()
                    if scraping_job.url:
                        return scraping_job.url
            except Exception as e:
                self.logger.error(f"Error getting URL from ScrapingJob: {str(e)}")
            
            self.logger.warning(f"No URL found for platform {platform}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting target URL for platform {platform}: {str(e)}")
            return None

    def _prepare_request_payload(self, platform: str, batch_job: BrightDataBatchJob, 
                                scraper_request: BrightDataScraperRequest) -> List[Dict[str, Any]]:
        """Prepare request payload for platform-specific scraping"""
        
        target_url = scraper_request.target_url
        
        if platform == 'instagram':
            # Extract username from Instagram URL
            username = self._extract_instagram_username(target_url)
            return [{
                'url': f'https://www.instagram.com/{username}/',
                'num_of_posts': batch_job.num_of_posts,
                'start_date': batch_job.start_date.strftime('%Y-%m-%d') if batch_job.start_date else '',
                'end_date': batch_job.end_date.strftime('%Y-%m-%d') if batch_job.end_date else '',
                'post_type': 'Post'
            }]
            
        elif platform == 'facebook':
            return [{
                'url': target_url,
                'num_of_posts': batch_job.num_of_posts,
                'start_date': batch_job.start_date.strftime('%Y-%m-%d') if batch_job.start_date else '',
                'end_date': batch_job.end_date.strftime('%Y-%m-%d') if batch_job.end_date else '',
                'post_type': 'Post'
            }]
            
        elif platform == 'tiktok':
            # Extract username from TikTok URL
            username = self._extract_tiktok_username(target_url)
            return [{
                'url': f'https://www.tiktok.com/@{username}',
                'num_of_posts': batch_job.num_of_posts,
                'start_date': batch_job.start_date.strftime('%Y-%m-%d') if batch_job.start_date else '',
                'end_date': batch_job.end_date.strftime('%Y-%m-%d') if batch_job.end_date else ''
            }]
            
        elif platform == 'linkedin':
            return [{
                'url': target_url,
                'limit': batch_job.num_of_posts,
                'include_posts': True,
                'include_articles': True,
                'max_comments': 30
            }]
            
        else:
            # Generic payload
            return [{
                'url': target_url,
                'limit': batch_job.num_of_posts
            }]

    def _execute_brightdata_request(self, scraper_request: BrightDataScraperRequest, 
                                   payload: List[Dict[str, Any]]) -> bool:
        """Execute a BrightData scraping request"""
        try:
            config = scraper_request.config
            
            # Get webhook base URL from settings
            webhook_base_url = getattr(settings, 'BRIGHTDATA_WEBHOOK_BASE_URL', 
                                     getattr(settings, 'BRIGHTDATA_BASE_URL', 'http://localhost:8000'))
            
            # Prepare the API request
            url = f"{self.base_url}/trigger"
            headers = {
                'Authorization': f'Bearer {config.api_token}',
                'Content-Type': 'application/json'
            }
            
            # Prepare URL parameters (this is the correct format for BrightData API)
            params = {
                'dataset_id': config.dataset_id,
                'include_errors': 'true',
                'type': 'discover_new',
                'discover_by': 'url',
                'endpoint': f"{webhook_base_url}/api/brightdata/webhook/",
                'notify': f"{webhook_base_url}/api/brightdata/notify/",
                'format': 'json',
                'uncompressed_webhook': 'true'
            }
            
            # Make the request to start the scraping (payload goes in body, params in URL)
            response = requests.post(
                url,
                params=params,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                
                # Update scraper request with response information
                scraper_request.request_id = response_data.get('id', response_data.get('request_id'))
                scraper_request.snapshot_id = response_data.get('snapshot_id')
                scraper_request.status = 'processing'
                scraper_request.started_at = timezone.now()
                scraper_request.save()
                
                self.logger.info(f"Started BrightData request: {scraper_request.request_id} for {scraper_request.platform}")
                return True
            else:
                error_msg = f"BrightData API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                
                scraper_request.status = 'failed'
                scraper_request.error_message = error_msg
                scraper_request.save()
                return False
                
        except Exception as e:
            error_msg = f"Error executing BrightData request: {str(e)}"
            self.logger.error(error_msg)
            
            scraper_request.status = 'failed'
            scraper_request.error_message = error_msg
            scraper_request.save()
            return False

    def _extract_instagram_username(self, url: str) -> str:
        """Extract Instagram username from URL"""
        try:
            # Handle various Instagram URL formats
            url = url.strip().rstrip('/')
            if 'instagram.com/' in url:
                username = url.split('instagram.com/')[-1].split('/')[0]
                return username.replace('@', '')
            return url.replace('@', '')
        except:
            return url

    def _extract_tiktok_username(self, url: str) -> str:
        """Extract TikTok username from URL"""
        try:
            # Handle various TikTok URL formats
            url = url.strip().rstrip('/')
            if 'tiktok.com/@' in url:
                username = url.split('tiktok.com/@')[-1].split('/')[0]
                return username
            elif 'tiktok.com/' in url:
                username = url.split('tiktok.com/')[-1].split('/')[0]
                return username.replace('@', '')
            return url.replace('@', '')
        except:
            return url.replace('@', '')

    def test_brightdata_connection(self, config: BrightDataConfig) -> Dict[str, Any]:
        """Test connection to BrightData API with a specific configuration"""
        try:
            url = f"{self.base_url}/datasets/{config.dataset_id}"
            headers = {
                'Authorization': f'Bearer {config.api_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Connection successful',
                    'dataset_info': response.json()
                }
            else:
                return {
                    'success': False,
                    'message': f'API error: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection error: {str(e)}'
            }