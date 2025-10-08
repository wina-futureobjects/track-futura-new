"""
BrightData Integration Services

RESTORED FROM WORKING OLD PROJECT - EXACT IMPLEMENTATION
This module provides services for interacting with the BrightData API
for social media scraping operations using the proven working approach.
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
    """Service for managing BrightData batch scraping operations - WORKING IMPLEMENTATION"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.brightdata.com/datasets/v3"
        
        # EXACT WORKING DATASET IDS FROM OLD PROJECT
        self.platform_datasets = {
            'instagram': 'gd_lk5ns7kz21pck8jpis',  # CONFIRMED WORKING Instagram dataset
            'facebook': 'gd_lkaxegm826bjpoo9m5',   # CONFIRMED WORKING Facebook dataset
            'tiktok': 'gd_l7q7dkf244hwps8lu2',     # TikTok dataset ID
            'linkedin': 'gd_l7q7dkf244hwps8lu3',   # LinkedIn dataset ID
        }

    def trigger_scraper(self, platform: str, urls: List[str]) -> Dict[str, Any]:
        """
        Main scraper trigger method - EXACT WORKING IMPLEMENTATION
        Uses the proven BrightData Dataset API format from old project
        """
        try:
            self.logger.info(f"🚀 TRIGGERING {platform.upper()} SCRAPER - WORKING IMPLEMENTATION")
            self.logger.info(f"📋 URLs: {urls}")
            
            # Get the dataset ID for this platform
            dataset_id = self.platform_datasets.get(platform)
            if not dataset_id:
                return {'success': False, 'error': f'No dataset configured for platform: {platform}'}
            
            # Create scraper request for tracking
            try:
                config = self._get_or_create_config(platform)
                if not config:
                    return {'success': False, 'error': f'Could not get configuration for {platform}'}
                
                scraper_request = BrightDataScraperRequest.objects.create(
                    config=config,
                    platform=f"{platform}_posts",
                    content_type='posts',
                    target_url=urls[0] if urls else f"https://www.{platform}.com/nike/",
                    source_name=f'{platform.title()} Batch Scraper',
                    status='pending'
                )
            except Exception as e:
                self.logger.warning(f"Could not create scraper request: {str(e)}")
                scraper_request = None
            
            # Execute the actual BrightData request
            success = self._make_brightdata_batch_request([scraper_request] if scraper_request else [], urls, platform)
            
            if success:
                return {
                    'success': True,
                    'batch_job_id': getattr(scraper_request, 'request_id', 'batch_created'),
                    'platform': platform,
                    'message': f'BrightData {platform} scraper triggered successfully!',
                    'urls_count': len(urls),
                    'dataset_id': dataset_id
                }
            else:
                return {'success': False, 'error': f'Failed to trigger {platform} scraper'}
                
        except Exception as e:
            error_msg = f"Failed to trigger {platform} scraper: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}

    def _make_brightdata_batch_request(self, scraper_requests: List[BrightDataScraperRequest], 
                                     urls: List[str], platform: str) -> bool:
        """
        Make a batch API request to BrightData - EXACT WORKING IMPLEMENTATION FROM OLD PROJECT
        """
        try:
            self.logger.info(f"🔄 Making BrightData batch request for {platform}")
            
            # Get dataset ID and API token
            dataset_id = self.platform_datasets.get(platform)
            api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"  # WORKING TOKEN
            
            if not dataset_id:
                self.logger.error(f"No dataset ID for platform: {platform}")
                return False
            
            # Prepare the request
            url = "https://api.brightdata.com/datasets/v3/trigger"
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
            }

            # Get webhook base URL from settings
            try:
                webhook_base_url = getattr(settings, 'BRIGHTDATA_WEBHOOK_BASE_URL', 
                                        'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site')
            except:
                webhook_base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'

            # Base parameters - EXACT FORMAT FROM WORKING OLD PROJECT
            params = {
                "dataset_id": dataset_id,
                "endpoint": f"{webhook_base_url}/api/brightdata/webhook/",
                "notify": f"{webhook_base_url}/api/brightdata/notify/",
                "format": "json",
                "uncompressed_webhook": "true",
                "include_errors": "true",
            }

            # Add platform-specific parameters - EXACT FROM OLD PROJECT
            if platform == 'instagram':
                params.update({
                    "type": "discover_new",
                    "discover_by": "url",
                })
            elif platform == 'facebook':
                # Facebook-specific parameters - NO discovery parameters needed
                # The dataset gd_lkaxegm826bjpoo9m5 works with URL payload without discovery params
                pass
            elif platform == 'linkedin':
                # LinkedIn-specific parameters - using profile_url discovery
                params.update({
                    "type": "discover_new",
                    "discover_by": "profile_url",
                })

            # Prepare payload - EXACT FORMAT FROM OLD PROJECT
            payload = []
            for url in urls:
                if platform == 'instagram':
                    # Instagram Posts API format - EXACT WORKING FORMAT
                    item = {
                        "url": url,
                        "num_of_posts": 10,
                        "start_date": "01-01-2025",
                        "end_date": "03-01-2025",
                        "post_type": "Post",
                        "posts_to_not_include": [],
                    }
                elif platform == 'facebook':
                    # Facebook Posts API format - EXACT WORKING FORMAT
                    item = {
                        "url": url,
                        "num_of_posts": 50,
                        "start_date": "01-01-2025", 
                        "end_date": "02-28-2025",
                        "posts_to_not_include": [],
                    }
                elif platform == 'tiktok':
                    # TikTok batch API needs URL field with uppercase "URL"
                    item = {
                        "URL": url,
                    }
                else:
                    # Generic format
                    item = {
                        "url": url,
                        "num_of_posts": 10,
                    }
                
                payload.append(item)

            # DEBUG LOGGING - EXACT FROM OLD PROJECT
            self.logger.info("🛠 BRIGHTDATA API REQUEST DEBUG - RESTORED WORKING VERSION")
            self.logger.info(f"  URL: {url}")
            self.logger.info(f"  Headers: {headers}")
            self.logger.info(f"  Params: {params}")
            self.logger.info(f"  Payload: {payload}")
            self.logger.info(f"  Webhook endpoint: {webhook_base_url}/api/brightdata/webhook/")
            
            print("🛠 BRIGHTDATA API REQUEST DEBUG - RESTORED WORKING VERSION")
            print(f"  Dataset ID: {dataset_id}")
            print(f"  API Token: {api_token[:10]}...")
            print(f"  Platform: {platform}")
            print(f"  Payload items: {len(payload)}")
            print(f"  endpoint: {webhook_base_url}/api/brightdata/webhook/")
            print()

            # Make the actual API request
            response = requests.post(url, headers=headers, params=params, json=payload, timeout=30)

            # DETAILED RESPONSE LOGGING - EXACT FROM OLD PROJECT
            print("\n🔥 BRIGHTDATA API RESPONSE:")
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Text: {response.text}")
            print("="*80 + "\n")

            if response.status_code == 200:
                try:
                    response_data = response.json()
                except json.JSONDecodeError as json_err:
                    response_data = {
                        "error": "Invalid or empty JSON response",
                        "raw_response": response.text,
                        "json_error": str(json_err)
                    }

                # Update scraper requests with response data
                snapshot_id = response_data.get('snapshot_id') or response_data.get('request_id')
                
                for scraper_request in scraper_requests:
                    if scraper_request:
                        scraper_request.request_id = snapshot_id
                        scraper_request.response_metadata = response_data
                        scraper_request.status = 'processing'
                        scraper_request.started_at = timezone.now()
                        scraper_request.save()

                self.logger.info(f"Successfully triggered batch scrape for {platform} with {len(payload)} sources. Request ID: {snapshot_id}")
                print(f"✅ SUCCESS! Request ID: {snapshot_id}")
                return True
            else:
                error_msg = f"BrightData API error for {platform} batch: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                
                # Update scraper requests with error
                for scraper_request in scraper_requests:
                    if scraper_request:
                        scraper_request.status = 'failed'
                        scraper_request.error_message = error_msg
                        scraper_request.save()
                        
                print(f"❌ FAILED! Status: {response.status_code}, Error: {response.text}")
                return False

        except Exception as e:
            error_msg = f"Exception during BrightData batch request for {platform}: {str(e)}"
            self.logger.error(error_msg)
            
            # Update scraper requests with error
            for scraper_request in scraper_requests:
                if scraper_request:
                    scraper_request.status = 'failed'
                    scraper_request.error_message = error_msg
                    scraper_request.save()
                    
            print(f"❌ EXCEPTION! Error: {str(e)}")
            print("="*80 + "\n")
            return False

    def _get_or_create_config(self, platform: str) -> Optional[BrightDataConfig]:
        """Get or create BrightData configuration for platform - WORKING VERSION"""
        try:
            # Try to get existing config
            config = BrightDataConfig.objects.filter(
                platform=platform,
                is_active=True
            ).first()
            
            if config:
                self.logger.info(f"Found existing config for {platform}")
                return config
            
            # Create default config with WORKING CREDENTIALS FROM OLD PROJECT
            dataset_id = self.platform_datasets.get(platform)
            if not dataset_id:
                self.logger.error(f"No dataset ID available for platform: {platform}")
                return None
            
            config = BrightDataConfig.objects.create(
                name=f"{platform.title()} Posts Scraper",
                platform=platform,
                dataset_id=dataset_id,
                api_token="8af6995e-3baa-4b69-9df7-8d7671e621eb",  # WORKING TOKEN
                is_active=True
            )
            
            self.logger.info(f"Created working config for {platform}: {dataset_id}")
            return config
            
        except Exception as e:
            self.logger.error(f"Error getting/creating config for {platform}: {str(e)}")
            return None

    # ========== LEGACY METHODS FOR BACKWARD COMPATIBILITY ==========
    
    def create_batch_job(self, name: str, project_id: int, source_folder_ids: List[int], 
                        platforms_to_scrape: List[str], content_types_to_scrape: Dict[str, List[str]], 
                        num_of_posts: int = 10, **kwargs) -> Optional[BrightDataBatchJob]:
        """Legacy method for creating batch jobs - redirects to new implementation"""
        urls = kwargs.get('urls', [])
        self.logger.info(f"Legacy create_batch_job called, redirecting to trigger_scraper")
        
        # For each platform, trigger the scraper
        for platform in platforms_to_scrape:
            result = self.trigger_scraper(platform, urls)
            if result['success']:
                self.logger.info(f"Successfully triggered {platform} via legacy method")
            else:
                self.logger.error(f"Failed to trigger {platform} via legacy method: {result.get('error')}")
        
        return None  # Legacy compatibility

    def execute_batch_job(self, batch_job_id: int) -> bool:
        """Legacy method for executing batch jobs - now handled automatically"""
        self.logger.info(f"Legacy execute_batch_job called for ID {batch_job_id}")
        return True