"""
Apify Integration Services

This module provides services for interacting with the Apify API
for social media scraping operations.
"""

import logging
import os
import requests
from typing import Optional, Dict, Any, List
from django.conf import settings
from django.utils import timezone

from .models import ApifyConfig, ApifyBatchJob, ApifyScraperRequest

logger = logging.getLogger(__name__)

class ApifyAutomatedBatchScraper:
    """Service for managing Apify batch scraping operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.apify.com/v2"
        
        # Platform-specific actor configurations
        self.platform_actors = {
            'instagram_posts': 'apify/instagram-scraper',
            'facebook_posts': 'apify/facebook-scraper', 
            'tiktok_posts': 'apify/tiktok-scraper',
            'linkedin_posts': 'apify/linkedin-company-scraper',
        }

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
            
            # Validate platforms
            if not batch_job.platforms_to_scrape:
                self.logger.error("No platforms specified for batch job")
                batch_job.status = 'failed'
                batch_job.error_log = "No platforms specified"
                batch_job.save()
                return False
            
            # Update batch job status
            batch_job.status = 'processing'
            batch_job.started_at = timezone.now()
            batch_job.total_sources = len(batch_job.platforms_to_scrape)
            batch_job.save()
            
            # Process each platform
            success_count = 0
            for platform in batch_job.platforms_to_scrape:
                if self._process_platform_scraping(batch_job, platform):
                    success_count += 1
                    
            # Update batch job final status
            if success_count == len(batch_job.platforms_to_scrape):
                batch_job.status = 'completed'
            elif success_count > 0:
                batch_job.status = 'completed'  # Partial success
            else:
                batch_job.status = 'failed'
                
            batch_job.successful_requests = success_count
            batch_job.failed_requests = len(batch_job.platforms_to_scrape) - success_count
            batch_job.completed_at = timezone.now()
            batch_job.save()
            
            self.logger.info(f"Executed batch job: {batch_job.name} - {success_count}/{len(batch_job.platforms_to_scrape)} successful")
            return success_count > 0
            
        except ApifyBatchJob.DoesNotExist:
            self.logger.error(f"Batch job {batch_job_id} not found")
            return False
        except Exception as e:
            self.logger.error(f"Error executing batch job: {str(e)}")
            try:
                batch_job = ApifyBatchJob.objects.get(id=batch_job_id)
                batch_job.status = 'failed'
                batch_job.error_log = str(e)
                batch_job.save()
            except:
                pass
            return False

    def _process_platform_scraping(self, batch_job: ApifyBatchJob, platform: str) -> bool:
        """Process scraping for a specific platform"""
        try:
            # Map platform to config
            platform_key = f"{platform}_posts" if not platform.endswith('_posts') else platform
            
            # Get configuration for this platform
            config = ApifyConfig.objects.filter(
                platform=platform_key,
                is_active=True
            ).first()
            
            if not config:
                self.logger.error(f"No active config found for platform: {platform_key}")
                return False
            
            # Get the actual target URL from platform params or workflow
            target_url = self._get_target_url_for_platform(batch_job, platform)
            if not target_url:
                self.logger.error(f"No target URL found for platform {platform} in batch job {batch_job.id}")
                return False
            
            # Create scraper request
            scraper_request = ApifyScraperRequest.objects.create(
                config=config,
                batch_job=batch_job,
                platform=platform_key,
                content_type='posts',
                target_url=target_url,
                source_name=f'{platform.title()} Scraper',
                status='pending'
            )
            
            # Prepare actor input based on platform
            actor_input = self._prepare_actor_input(platform, batch_job, scraper_request)
            
            # Execute the scraping request
            success = self._execute_apify_actor(scraper_request, actor_input)
            
            if success:
                self.logger.info(f"Successfully started scraping for {platform}")
                return True
            else:
                self.logger.error(f"Failed to start scraping for {platform}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing platform {platform}: {str(e)}")
            return False

    def _get_target_url_for_platform(self, batch_job: ApifyBatchJob, platform: str) -> str:
        """Get the actual target URL for scraping from batch job data"""
        try:
            # Check if we have URLs in platform_params
            platform_params = batch_job.platform_params or {}
            
            # Option 1: Direct URLs in platform_params
            if 'urls' in platform_params:
                urls = platform_params['urls']
                if urls and len(urls) > 0:
                    return urls[0]  # Use the first URL
            
            # Option 2: Get URL from TrackSource if track_source_id is provided
            if 'track_source_id' in platform_params:
                try:
                    from track_accounts.models import TrackSource
                    track_source = TrackSource.objects.get(id=platform_params['track_source_id'])
                    
                    # Get URL based on platform
                    if platform.lower() == 'instagram' and track_source.instagram_link:
                        return track_source.instagram_link
                    elif platform.lower() == 'facebook' and track_source.facebook_link:
                        return track_source.facebook_link
                    elif platform.lower() == 'linkedin' and track_source.linkedin_link:
                        return track_source.linkedin_link
                    elif platform.lower() == 'tiktok' and track_source.tiktok_link:
                        return track_source.tiktok_link
                    elif track_source.other_social_media:
                        return track_source.other_social_media
                        
                except Exception as e:
                    self.logger.error(f"Error getting URL from TrackSource: {str(e)}")
            
            # Option 3: Get URL from InputCollection if input_collection_id is provided
            if 'input_collection_id' in platform_params:
                try:
                    from workflow.models import InputCollection
                    input_collection = InputCollection.objects.get(id=platform_params['input_collection_id'])
                    
                    if input_collection.urls and len(input_collection.urls) > 0:
                        return input_collection.urls[0]
                        
                except Exception as e:
                    self.logger.error(f"Error getting URL from InputCollection: {str(e)}")
            
            # Option 4: Get URL from ScrapingJob if available
            try:
                from workflow.models import ScrapingJob
                scraping_jobs = ScrapingJob.objects.filter(batch_job=batch_job, platform=platform.lower())
                if scraping_jobs.exists():
                    scraping_job = scraping_jobs.first()
                    if scraping_job.url:
                        return scraping_job.url
            except Exception as e:
                self.logger.error(f"Error getting URL from ScrapingJob: {str(e)}")
            
            # Fallback: Use a generic explore URL
            self.logger.warning(f"No specific URL found for platform {platform}, using generic explore URL")
            return f'https://{platform}.com/explore'
            
        except Exception as e:
            self.logger.error(f"Error getting target URL for platform {platform}: {str(e)}")
            return f'https://{platform}.com/explore'

    def _prepare_actor_input(self, platform: str, batch_job: ApifyBatchJob, scraper_request: ApifyScraperRequest) -> Dict[str, Any]:
        """Prepare input data for platform-specific actors"""
        
        # Get the actor ID to determine input format
        config = scraper_request.config
        actor_id = config.actor_id
        
        # Get the actual target URL
        target_url = scraper_request.target_url
        
        # Platform-specific input configurations
        if platform.startswith('instagram'):
            # Extract username from Instagram URL
            username = self._extract_instagram_username(target_url)
            
            # For Instagram Post Scraper (apify~instagram-post-scraper)
            return {
                'username': [username] if username else ['instagram'],  # Array of usernames to scrape from
                'resultsLimit': batch_job.num_of_posts,
                'addParentData': False,
                'enhanceUserInformation': True,
                'isUserReelFeed': False,
                'isUserTaggedFeed': False,
                'onlyPostsWithLocation': False,
                'likedByInfluencer': False,
                'followedByInfluencer': False
            }
            
        elif platform.startswith('facebook'):
            # For Facebook Posts Scraper (apify~facebook-posts-scraper)
            return {
                'startUrls': [
                    {'url': target_url}
                ],
                'maxItems': batch_job.num_of_posts,
                'scrollDown': True,
                'resultsLimit': batch_job.num_of_posts,
                'scrapeComments': False,
                'scrapeReactionsCount': True,
                'scrapeSharesCount': True,
                'maxCommentsCount': 0
            }
            
        elif platform.startswith('tiktok'):
            # For TikTok Scraper (apify~tiktok-scraper)
            tiktok_username = self._extract_tiktok_username(target_url)
            return {
                'profiles': [tiktok_username] if tiktok_username else ['trending'],
                'resultsPerPage': batch_job.num_of_posts,
                'shouldDownloadCovers': False,
                'shouldDownloadSlideshowImages': False,
                'shouldDownloadSubtitles': False,
                'shouldDownloadVideos': False,
                'proxyCountryCode': 'US'
            }
            
        elif platform.startswith('linkedin'):
            # For LinkedIn Scraper (apify~linkedin-scraper)
            return {
                'startUrls': [
                    {'url': target_url}
                ],
                'maxItems': batch_job.num_of_posts,
                'minDelay': 2,
                'maxDelay': 5,
                'scrollDown': True,
                'includePosts': True,
                'includeComments': False
            }
            
        else:
            # Fallback for unknown platforms - use generic web scraper format
            return {
                'startUrls': [{'url': 'https://example.com'}],
                'maxRequestRetries': 3,
                'maxPagesPerCrawl': batch_job.num_of_posts,
                'initialCookies': [],
                'proxyConfiguration': {'useApifyProxy': True},
                'pageFunction': '''
                    function pageFunction(context) {
                        return {
                            url: context.request.url,
                            title: $('title').text(),
                            content: $('body').text().substring(0, 1000),
                            platform: 'generic'
                        };
                    }
                '''
            }

    def _execute_apify_actor(self, scraper_request: ApifyScraperRequest, actor_input: Dict[str, Any]) -> bool:
        """Execute an Apify actor"""
        try:
            config = scraper_request.config
            actor_id = config.actor_id
            api_token = config.api_token
            
            # Prepare the API request
            url = f"{self.base_url}/acts/{actor_id}/runs"
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            }
            
            # Add webhook notifications
            webhook_base = "http://127.0.0.1:8000"  # For development
            actor_input.update({
                'webhookUrl': f"{webhook_base}/api/apify/webhook/",
                'notifyOnceFinished': True
            })
            
            # Make the request to start the actor
            response = requests.post(
                url,
                json=actor_input,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                run_data = response.json()['data']
                
                # Update scraper request with run information
                scraper_request.request_id = run_data['id']
                scraper_request.status = 'processing'
                scraper_request.started_at = timezone.now()
                scraper_request.save()
                
                self.logger.info(f"Started Apify actor run: {run_data['id']} for {scraper_request.platform}")
                return True
            else:
                error_msg = f"Apify API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                
                scraper_request.status = 'failed'
                scraper_request.error_message = error_msg
                scraper_request.save()
                return False
                
        except Exception as e:
            error_msg = f"Error executing Apify actor: {str(e)}"
            self.logger.error(error_msg)
            
            scraper_request.status = 'failed'
            scraper_request.error_message = error_msg
            scraper_request.save()
            return False

    def test_apify_connection(self, config: ApifyConfig) -> Dict[str, Any]:
        """Test connection to Apify API with a specific configuration"""
        try:
            # Test with a simple actor info request
            url = f"{self.base_url}/acts/{config.actor_id}"
            headers = {
                'Authorization': f'Bearer {config.api_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                actor_info = response.json()['data']
                return {
                    'success': True,
                    'actor_name': actor_info.get('name', 'Unknown'),
                    'actor_id': actor_info.get('id'),
                    'message': f"Successfully connected to {config.platform} scraper"
                }
            else:
                return {
                    'success': False,
                    'error': f"API returned {response.status_code}: {response.text}",
                    'message': f"Failed to connect to {config.platform} scraper"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Connection test failed for {config.platform}"
            }

    def _extract_instagram_username(self, url: str) -> str:
        """Extract Instagram username from URL"""
        try:
            # Instagram URL patterns:
            # https://www.instagram.com/nike/
            # https://instagram.com/nike/
            # https://www.instagram.com/nike
            import re
            pattern = r'instagram\.com/([^/?]+)'
            match = re.search(pattern, url)
            if match:
                username = match.group(1)
                # Remove trailing slash if present
                username = username.rstrip('/')
                self.logger.info(f"Extracted Instagram username: {username} from URL: {url}")
                return username
            else:
                self.logger.warning(f"Could not extract Instagram username from URL: {url}")
                return 'instagram'
        except Exception as e:
            self.logger.error(f"Error extracting Instagram username from {url}: {str(e)}")
            return 'instagram'
    
    def _extract_tiktok_username(self, url: str) -> str:
        """Extract TikTok username from URL"""
        try:
            # TikTok URL patterns:
            # https://www.tiktok.com/@nike
            # https://tiktok.com/@nike
            import re
            pattern = r'tiktok\.com/@([^/?]+)'
            match = re.search(pattern, url)
            if match:
                username = match.group(1)
                self.logger.info(f"Extracted TikTok username: {username} from URL: {url}")
                return username
            else:
                self.logger.warning(f"Could not extract TikTok username from URL: {url}")
                return 'trending'
        except Exception as e:
            self.logger.error(f"Error extracting TikTok username from {url}: {str(e)}")
            return 'trending'
