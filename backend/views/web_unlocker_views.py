from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import requests
import logging
from datetime import datetime
from .models import UnifiedRunFolder, BrightDataScrapedPost, BrightDataWebhookEvent

logger = logging.getLogger(__name__)

class WebUnlockerAPIView(View):
    """Web Unlocker API integration endpoint"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Handle Web Unlocker scraping requests"""
        try:
            data = json.loads(request.body)
            target_url = data.get('url')
            scraper_name = data.get('scraper_name', 'Web Unlocker')
            
            if not target_url:
                return JsonResponse({
                    'error': 'URL is required',
                    'success': False
                }, status=400)
            
            # Call Web Unlocker API
            result = self.scrape_with_web_unlocker(target_url, scraper_name)
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'message': 'Scraping completed successfully',
                    'folder_id': result['folder_id'],
                    'data_size': result['data_size']
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                }, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data',
                'success': False
            }, status=400)
        except Exception as e:
            logger.error(f"Web Unlocker API error: {str(e)}")
            return JsonResponse({
                'error': f'Internal server error: {str(e)}',
                'success': False
            }, status=500)
    
    def scrape_with_web_unlocker(self, target_url, scraper_name):
        """Execute Web Unlocker API request"""
        try:
            # BrightData Web Unlocker API configuration
            api_url = "https://api.brightdata.com/request"
            api_key = "8af6995e-3baa-4b69-9df7-8d7671e621eb"  # Your API token
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "zone": "web_unlocker1",
                "url": target_url,
                "format": "raw"
            }
            
            # Make Web Unlocker API request
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                # Create UnifiedRunFolder entry
                folder = UnifiedRunFolder.objects.create(
                    project_id=2,  # Your project ID
                    folder_name=f"Web Unlocker - {scraper_name}",
                    folder_emoji="🔓",
                    created_by="Web Unlocker API",
                    description=f"Scraped from: {target_url}"
                )
                
                # Store scraped content
                scraped_post = BrightDataScrapedPost.objects.create(
                    folder=folder,
                    original_data=response.text,
                    url=target_url,
                    platform="Web Unlocker",
                    post_type="web_content"
                )
                
                # Create webhook event for tracking
                BrightDataWebhookEvent.objects.create(
                    event_type="web_unlocker_scrape",
                    webhook_data={
                        "url": target_url,
                        "status": "success",
                        "scraper": scraper_name,
                        "data_size": len(response.text)
                    },
                    processed=True,
                    folder=folder
                )
                
                logger.info(f"Web Unlocker scraping successful: {target_url}")
                
                return {
                    'success': True,
                    'folder_id': folder.id,
                    'data_size': len(response.text)
                }
                
            else:
                error_msg = f"Web Unlocker API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except requests.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }