"""
Apify Integration Services

This module provides services for interacting with the Apify API
for social media scraping operations.
"""

import logging
import os
from typing import Optional, Dict, Any, List
from django.conf import settings
from django.utils import timezone

from .models import ApifyConfig, ApifyBatchJob, ApifyScraperRequest

logger = logging.getLogger(__name__)

class ApifyAutomatedBatchScraper:
    """Service for managing Apify batch scraping operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.apify_client = None

    def _get_apify_client(self, api_token: str):
        """Get or create Apify client instance"""
        try:
            from apify_client import ApifyClient
            if not self.apify_client or self.apify_client.token != api_token:
                self.apify_client = ApifyClient(api_token)
            return self.apify_client
        except ImportError:
            self.logger.error("Apify client not installed. Run: pip install apify-client")
            return None

    def create_batch_job(self, name: str, project_id: int, source_folder_ids: List[int], 
                        platforms_to_scrape: List[str], content_types_to_scrape: Dict[str, List[str]], 
                        num_of_posts: int = 10, **kwargs) -> Optional[ApifyBatchJob]:
        """
        Create a new Apify batch job
        
        Args:
            name: Name of the batch job
            project_id: ID of the project
            source_folder_ids: List of source folder IDs
            platforms_to_scrape: List of platforms to scrape
            content_types_to_scrape: Dictionary mapping platforms to content types
            num_of_posts: Number of posts to scrape
            **kwargs: Additional parameters
            
        Returns:
            ApifyBatchJob: Created batch job or None if failed
        """
        try:
            from users.models import Project
            
            project = Project.objects.get(id=project_id)
            
            batch_job = ApifyBatchJob.objects.create(
                name=name,
                project=project,
                source_folder_ids=source_folder_ids,
                platforms_to_scrape=platforms_to_scrape,
                content_types_to_scrape=content_types_to_scrape,
                num_of_posts=num_of_posts,
                **kwargs
            )
            
            self.logger.info(f"Created Apify batch job: {batch_job.name} (ID: {batch_job.id})")
            return batch_job
            
        except Exception as e:
            self.logger.error(f"Error creating batch job: {str(e)}")
            return None

    def execute_batch_job(self, batch_job_id: int) -> bool:
        """
        Execute a batch job using Apify
        
        Args:
            batch_job_id: ID of the batch job to execute
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            batch_job = ApifyBatchJob.objects.get(id=batch_job_id)
            
            # Get the first active config for the first platform
            if not batch_job.platforms_to_scrape:
                self.logger.error("No platforms specified for batch job")
                return False
                
            platform = batch_job.platforms_to_scrape[0]
            config = ApifyConfig.objects.filter(
                platform__startswith=platform.split('_')[0],
                is_active=True
            ).first()
            
            if not config:
                self.logger.error(f"No active config found for platform: {platform}")
                return False
            
            # Get Apify client
            client = self._get_apify_client(config.api_token)
            if not client:
                return False
            
            # Update batch job status
            batch_job.status = 'processing'
            batch_job.started_at = timezone.now()
            batch_job.save()
            
            # Create scraper requests for each source
            self._create_scraper_requests(batch_job, config)
            
            self.logger.info(f"Executed batch job: {batch_job.name}")
            return True
            
        except ApifyBatchJob.DoesNotExist:
            self.logger.error(f"Batch job {batch_job_id} not found")
            return False
        except Exception as e:
            self.logger.error(f"Error executing batch job: {str(e)}")
            return False

    def _create_scraper_requests(self, batch_job: ApifyBatchJob, config: ApifyConfig):
        """Create scraper requests for a batch job"""
        try:
            # This is a simplified version - in practice, you'd get actual sources
            # For now, create a single test request
            scraper_request = ApifyScraperRequest.objects.create(
                config=config,
                batch_job=batch_job,
                platform=config.platform,
                content_type='post',
                target_url='https://example.com/test',
                source_name='Test Source',
                status='pending'
            )
            
            self.logger.info(f"Created scraper request: {scraper_request.id}")
            
        except Exception as e:
            self.logger.error(f"Error creating scraper requests: {str(e)}")

    def _make_apify_request(self, scraper_request: ApifyScraperRequest, actor_input: Dict) -> bool:
        """
        Make the actual API request to Apify
        
        Args:
            scraper_request: Scraper request instance
            actor_input: Input data for the Apify actor
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            client = self._get_apify_client(scraper_request.config.api_token)
            if not client:
                return False
            
            # Run the actor
            run = client.actor(scraper_request.config.actor_id).call(actor_input)
            
            # Update scraper request with run ID
            scraper_request.request_id = run['id']
            scraper_request.status = 'processing'
            scraper_request.started_at = timezone.now()
            scraper_request.save()
            
            self.logger.info(f"Started Apify run: {run['id']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error making Apify request: {str(e)}")
            scraper_request.status = 'failed'
            scraper_request.error_message = str(e)
            scraper_request.save()
            return False
