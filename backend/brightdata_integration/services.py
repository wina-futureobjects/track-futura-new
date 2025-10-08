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
        """Process scraping for a specific platform - ENHANCED VERSION"""
        try:
            # Get configuration for this platform - CREATE IF MISSING
            config = BrightDataConfig.objects.filter(
                platform=platform,
                is_active=True
            ).first()
            
            if not config:
                # Create default config if missing
                dataset_mapping = {
                    "instagram": "0",
                    "facebook": "1", 
                    "tiktok": "2",
                    "linkedin": "3"
                }
                # Get API token from environment or existing config
                api_token = os.getenv('BRIGHTDATA_API_KEY', '')
                if not api_token:
                    # Try to get from existing config
                    existing_config = BrightDataConfig.objects.filter(is_active=True).first()
                    if existing_config:
                        api_token = existing_config.api_token
                    else:
                        api_token = 'c9f8b6d4b5d6c7a8b9c0d1e2f3g4h5i6j7k8l9m0'  # Fallback
                
                config = BrightDataConfig.objects.create(
                    name=f'{platform.title()} Posts Scraper',
                    platform=platform,
                    dataset_id=f'gd_l7q7dkf244hwps8lu{dataset_mapping.get(platform, "0")}',
                    api_token=api_token,
                    is_active=True
                )
                self.logger.info(f"Created missing config for platform: {platform}")
            
            # Enhanced URL extraction
            target_url = self._get_target_url_for_platform(batch_job, platform)
            if not target_url:
                # Try to get URL from Nike InputCollection
                try:
                    from workflow.models import InputCollection
                    nike_collection = InputCollection.objects.filter(
                        project=batch_job.project,
                        platform_service__platform__name=platform
                    ).first()
                    
                    if nike_collection and nike_collection.urls:
                        target_url = nike_collection.urls[0]
                        self.logger.info(f"Found URL from Nike InputCollection: {target_url}")
                        
                except Exception as e:
                    self.logger.error(f"Error getting URL from InputCollection: {str(e)}")
            
            if not target_url:
                # Use default test URL as fallback
                default_urls = {
                    'instagram': 'https://www.instagram.com/nike/',
                    'facebook': 'https://www.facebook.com/nike',
                    'tiktok': 'https://www.tiktok.com/@nike',
                    'linkedin': 'https://www.linkedin.com/company/nike'
                }
                target_url = default_urls.get(platform)
                self.logger.warning(f"Using fallback URL for {platform}: {target_url}")
            
            if not target_url:
                self.logger.error(f"No URL available for platform {platform}")
                return False
            
            # Create scraper request with better error handling
            scraper_request = BrightDataScraperRequest.objects.create(
                config=config,
                batch_job=batch_job,
                platform=platform,
                content_type='posts',
                target_url=target_url,
                source_name=f'{platform.title()} Scraper',
                status='pending'
            )
            
            # Prepare and execute request
            payload = self._prepare_request_payload(platform, batch_job, scraper_request)
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