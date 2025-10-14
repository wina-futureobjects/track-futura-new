from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import requests
import logging
from datetime import datetime
from track_accounts.models import UnifiedRunFolder
from brightdata_integration.models import BrightDataScrapedPost, BrightDataWebhookEvent

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
                    'data_size': result['data_size'],
                    'url_scraped': target_url,
                    'scraper_name': scraper_name
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
            # Get or create a default project with detailed logging
            from users.models import Project
            from django.contrib.auth import get_user_model
            
            logger.info("🔍 Checking for existing project...")
            
            User = get_user_model()
            
            # Use transaction to ensure atomicity
            from django.db import transaction
            
            with transaction.atomic():
                project = Project.objects.first()
                
                if not project:
                    logger.info("📋 No project found, creating default project...")
                    
                    # Create default user and project if none exist
                    user = User.objects.filter(is_superuser=True).first()
                    if not user:
                        logger.info("👤 Creating superuser...")
                        user = User.objects.create_superuser(
                            username='admin',
                            email='admin@trackfutura.com',
                            password='admin123'
                        )
                        logger.info(f"✅ Created superuser: {user.username} (ID: {user.id})")
                    else:
                        logger.info(f"✅ Found superuser: {user.username} (ID: {user.id})")
                    
                    logger.info("🏗️ Creating project...")
                    project = Project.objects.create(
                        name="TrackFutura Main Project",
                        description="Main project for BrightData Web Unlocker integration",
                        owner=user
                    )
                    logger.info(f"✅ Created project: {project.name} (ID: {project.id})")
                else:
                    logger.info(f"✅ Found existing project: {project.name} (ID: {project.id})")
                
                # Verify project exists before proceeding
                if not project or not project.id:
                    raise Exception("Failed to create or retrieve project")
                
                logger.info(f"🎯 Using project ID: {project.id} for Web Unlocker integration")
            
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
            
            logger.info(f"Making Web Unlocker API request to {target_url}")
            
            # Make Web Unlocker API request
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                # Create UnifiedRunFolder entry with correct field names
                folder = UnifiedRunFolder.objects.create(
                    name=f"Web Unlocker - {scraper_name}",
                    folder_type='job',  # Use valid choice from FOLDER_TYPE_CHOICES
                    platform_code=None,  # Web Unlocker is not a social platform
                    service_code=None,   # Web Unlocker is not a social service
                    project=project,     # Use project object, not project_id
                    parent_folder=None,  # Top-level folder
                    description=f"Scraped from: {target_url}"
                )
                
                # Store scraped content
                scraped_post = BrightDataScrapedPost.objects.create(
                    folder_id=folder.id,
                    content=response.text[:5000],  # Truncate content if too long
                    url=target_url,
                    platform="web_unlocker",
                    user_posted="Web Unlocker API",
                    likes=0,
                    num_comments=0,
                    media_type="web_content"
                )
                
                # Create webhook event for tracking
                BrightDataWebhookEvent.objects.create(
                    event_id=f"web_unlocker_{folder.id}",
                    snapshot_id=f"web_unlocker_snapshot_{folder.id}",
                    platform="web_unlocker",
                    status="completed",
                    raw_data={
                        "url": target_url,
                        "status": "success",
                        "scraper": scraper_name,
                        "data_size": len(response.text)
                    }
                )
                
                logger.info(f"Web Unlocker scraping successful: {target_url} -> Folder {folder.id}")
                
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
            logger.error(f"❌ Web Unlocker error: {error_msg}")
            logger.error(f"📍 Error type: {type(e).__name__}")
            
            # Log stack trace for debugging
            import traceback
            logger.error(f"📚 Stack trace: {traceback.format_exc()}")
            
            return {
                'success': False,
                'error': error_msg
            }