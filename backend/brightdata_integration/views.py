from django.shortcuts import render
import json
import requests
import logging
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import BrightdataConfig, ScraperRequest, BatchScraperJob, BrightdataNotification
from .serializers import (
    BrightdataConfigSerializer, ScraperRequestSerializer, ScraperRequestCreateSerializer,
    BatchScraperJobSerializer, BatchScraperJobCreateSerializer, BrightdataNotificationSerializer
)
from .services import AutomatedBatchScraper, create_and_execute_batch_job
import traceback
from urllib.parse import urlencode, urlparse, urlunparse

# Set up logger
logger = logging.getLogger(__name__)

class BrightdataConfigViewSet(viewsets.ModelViewSet):
    """API endpoint for Brightdata configuration"""
    queryset = BrightdataConfig.objects.all()
    serializer_class = BrightdataConfigSerializer
    permission_classes = [AllowAny]  # For testing, use proper permissions in production

    def get_queryset(self):
        """Filter by platform if specified"""
        queryset = BrightdataConfig.objects.all()
        platform = self.request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(platform=platform)
        return queryset.order_by('platform', 'name')

    @action(detail=True, methods=['POST'])
    def set_active(self, request, pk=None):
        """Set the current configuration as active and deactivate others for the same platform"""
        config = self.get_object()

        # Deactivate all other configurations for this platform
        BrightdataConfig.objects.filter(platform=config.platform, is_active=True).exclude(pk=config.pk).update(is_active=False)

        # Activate the current configuration
        config.is_active = True
        config.save()

        return Response({'status': f'{config.platform.title()} configuration activated'})

    @action(detail=False, methods=['GET'])
    def active(self, request):
        """Get all active configurations by platform"""
        platform = request.query_params.get('platform')
        if platform:
            config = BrightdataConfig.objects.filter(platform=platform, is_active=True).first()
            if not config:
                return Response({'error': f'No active configuration found for {platform}'}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        else:
            # Return all active configurations grouped by platform
            configs = BrightdataConfig.objects.filter(is_active=True).order_by('platform')
            serializer = self.get_serializer(configs, many=True)
            return Response(serializer.data)

class ScraperRequestViewSet(viewsets.ModelViewSet):
    """API endpoint for Brightdata scraper requests"""
    queryset = ScraperRequest.objects.all()
    serializer_class = ScraperRequestSerializer
    permission_classes = [AllowAny]  # For testing, use proper permissions in production

    def get_serializer_class(self):
        if self.action == 'create':
            return ScraperRequestCreateSerializer
        return self.serializer_class

    @action(detail=False, methods=['POST'])
    def trigger_facebook_scrape(self, request):
        """Endpoint to trigger a Facebook scrape using Brightdata API"""
        logger = logging.getLogger(__name__)

        try:
            # Log the incoming request data for debugging
            logger.info(f"Facebook scraper request data: {request.data}")
            print("\n\n==== DEBUG: FACEBOOK SCRAPER REQUEST DATA ====")
            print(f"Request data: {request.data}")
            print("=======================================\n")

            # Get request parameters
            target_url = request.data.get('target_url')
            if not target_url:
                return Response({'error': 'Target URL is required'},
                               status=status.HTTP_400_BAD_REQUEST)

            # Get content type and determine platform configuration key
            content_type = request.data.get('content_type', 'post')
            platform_config_key = f'facebook_{content_type}s'  # facebook_posts, facebook_reels, facebook_comments

            # Get the active Facebook configuration for specific content type
            config = BrightdataConfig.objects.filter(platform=platform_config_key, is_active=True).first()
            if not config:
                return Response({'error': f'No active {platform_config_key} Brightdata configuration found'},
                               status=status.HTTP_400_BAD_REQUEST)

            # Optional parameters with defaults
            num_of_posts = request.data.get('num_of_posts', 10)
            posts_to_not_include = request.data.get('posts_to_not_include', [])

            # Date handling - save original YYYY-MM-DD dates for database
            db_start_date = request.data.get('start_date', '')
            db_end_date = request.data.get('end_date', '')

            # Create API date versions in MM-DD-YYYY format
            api_start_date = ''
            api_end_date = ''

            # Validate and convert dates if provided
            if db_start_date:
                try:
                    # Verify it's in YYYY-MM-DD format
                    date_obj = datetime.strptime(db_start_date, '%Y-%m-%d')
                    # Convert to MM-DD-YYYY for API
                    api_start_date = date_obj.strftime('%m-%d-%Y')
                except ValueError:
                    return Response({'error': 'Invalid start_date format. Use YYYY-MM-DD format.'},
                                   status=status.HTTP_400_BAD_REQUEST)

            if db_end_date:
                try:
                    # Verify it's in YYYY-MM-DD format
                    date_obj = datetime.strptime(db_end_date, '%Y-%m-%d')
                    # Convert to MM-DD-YYYY for API
                    api_end_date = date_obj.strftime('%m-%d-%Y')
                except ValueError:
                    return Response({'error': 'Invalid end_date format. Use YYYY-MM-DD format.'},
                                   status=status.HTTP_400_BAD_REQUEST)

            folder_id = request.data.get('folder_id')

            # Prepare Brightdata API request
            url = "https://api.brightdata.com/datasets/v3/trigger"
            headers = {
                "Authorization": f"Bearer {config.api_token}",
                "Content-Type": "application/json",
            }
            params = {
                "dataset_id": config.dataset_id,
                "include_errors": "true",
            }

            # Create request payload as a direct array (not nested)
            # Use MM-DD-YYYY format for API
            data = [{
                "url": target_url,
                "num_of_posts": num_of_posts,
                "posts_to_not_include": posts_to_not_include,
                "start_date": api_start_date,
                "end_date": api_end_date,
            }]

            # Log the request payload for debugging
            print(f"\n\n==== DEBUG: BRIGHTDATA API REQUEST ({platform_config_key.upper()}) ====")
            print(f"URL: {url}")
            print(f"Headers: {headers}")
            print(f"Params: {params}")
            print(f"Data: {data}")
            print(f"DB dates: start={db_start_date}, end={db_end_date}")
            print(f"API dates: start={api_start_date}, end={api_end_date}")
            print(f"Configuration: {config.name} - {config.get_platform_display()}")

            # Show the actual request that would be made
            print(f"Final request URL: {url}?{urlencode(params)}")
            print(f"Final request body: {json.dumps(data)}")

            print("\nSample request from Brightdata documentation:")
            print("""[
	{"url":"https://www.facebook.com/LeBron/","num_of_posts":1,"posts_to_not_include":["1029318335225728","1029509225206639"],"start_date":"","end_date":""},
	{"url":"https://www.facebook.com/SamsungIsrael/","num_of_posts":50,"start_date":"01-01-2025","end_date":"02-28-2025"},
	{"url":"https://www.facebook.com/gagadaily/","num_of_posts":100,"start_date":"","end_date":""},
]""")
            print("=======================================\n")

            # Create a scraper request record - use original YYYY-MM-DD for database
            scraper_request = ScraperRequest.objects.create(
                config=config,
                platform=platform_config_key,
                content_type=content_type,
                target_url=target_url,
                num_of_posts=num_of_posts,
                posts_to_not_include=str(posts_to_not_include) if posts_to_not_include else None,
                start_date=db_start_date if db_start_date else None,
                end_date=db_end_date if db_end_date else None,
                folder_id=folder_id,
                request_payload=data,
                status='pending'
            )

            try:
                # Make the API request to Brightdata
                print("\n\n==== DEBUG: BRIGHTDATA API REQUEST ====")
                print(f"URL: {url}")
                print(f"Headers: {headers}")
                print(f"Params: {params}")
                print(f"Data: {data}")
                print(f"DB dates: start={db_start_date}, end={db_end_date}")
                print(f"API dates: start={api_start_date}, end={api_end_date}")
                print("\nSample request from Brightdata documentation:")
                print("""[
	{"url":"https://www.facebook.com/LeBron/","num_of_posts":1,"posts_to_not_include":["1029318335225728","1029509225206639"],"start_date":"","end_date":""},
	{"url":"https://www.facebook.com/SamsungIsrael/","num_of_posts":50,"start_date":"01-01-2025","end_date":"02-28-2025"},
	{"url":"https://www.facebook.com/gagadaily/","num_of_posts":100,"start_date":"","end_date":""},
]""")
                print("=======================================\n")

                response = requests.post(url, headers=headers, params=params, json=data)

                print("\n==== DEBUG: BRIGHTDATA API RESPONSE ====")
                print(f"Status code: {response.status_code}")
                print(f"Response text: {response.text}")
                print("=======================================\n\n")

                # Try to parse the response as JSON
                try:
                    if response.text.strip():  # Check if response is not empty
                        response_data = response.json()
                    else:
                        # Handle empty response
                        response_data = {"error": "Empty response from Brightdata API"}
                        print("WARNING: Empty response from Brightdata API")
                except json.JSONDecodeError as json_err:
                    # Handle invalid JSON
                    print(f"ERROR: Could not parse Brightdata API response as JSON: {str(json_err)}")
                    response_data = {
                        "error": f"Invalid JSON response from Brightdata API: {str(json_err)}",
                        "raw_response": response.text
                    }

                # Log the API response for debugging
                logger.info(f"Brightdata API response: {response_data}")

                # Update the scraper request record
                scraper_request.response_metadata = response_data

                if response.status_code == 200 and "error" not in response_data:
                    scraper_request.status = 'processing'
                    # Try to get request_id safely
                    scraper_request.request_id = response_data.get('request_id', '') if isinstance(response_data, dict) else ''
                    return Response({
                        'status': 'Scraper request sent successfully',
                        'request_id': scraper_request.request_id,
                        'brightdata_response': response_data
                    })
                else:
                    scraper_request.status = 'failed'
                    error_message = response_data.get('error', 'Unknown error') if isinstance(response_data, dict) else str(response_data)
                    scraper_request.error_message = error_message
                    return Response({
                        'error': 'Failed to trigger Brightdata scraper',
                        'brightdata_response': response_data,
                        'status_code': response.status_code,
                        'raw_response': response.text
                    }, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                # Handle any exceptions in the API request
                logger.error(f"Error making Brightdata API request: {str(e)}")
                logger.error(traceback.format_exc())

                print("\n\n==== DEBUG: API REQUEST ERROR ====")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                print(f"Traceback:\n{traceback.format_exc()}")
                print("=======================================\n\n")

                scraper_request.status = 'failed'
                scraper_request.error_message = str(e)
                return Response({
                    'error': 'Error triggering Brightdata scraper',
                    'details': str(e),
                    'error_type': type(e).__name__
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            finally:
                # Save the scraper request record
                scraper_request.save()

        except Exception as outer_exception:
            # Catch-all for any unexpected errors
            logger.error(f"Unexpected error in trigger_facebook_scrape: {str(outer_exception)}")
            logger.error(traceback.format_exc())

            print("\n\n==== DEBUG: OUTER EXCEPTION ERROR ====")
            print(f"Error type: {type(outer_exception).__name__}")
            print(f"Error message: {str(outer_exception)}")
            print(f"Traceback:\n{traceback.format_exc()}")
            print("=======================================\n\n")

            return Response({
                'error': 'Unexpected server error',
                'details': str(outer_exception),
                'error_type': type(outer_exception).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['POST'])
    def trigger_instagram_scrape(self, request):
        """Endpoint to trigger an Instagram scrape using Brightdata API"""
        logger = logging.getLogger(__name__)

        try:
            # Log the incoming request data for debugging
            logger.info(f"Instagram scraper request data: {request.data}")
            print("\n\n==== DEBUG: INSTAGRAM SCRAPER REQUEST DATA ====")
            print(f"Request data: {request.data}")
            print("=======================================\n")

            # Get request parameters
            target_url = request.data.get('target_url')
            if not target_url:
                return Response({'error': 'Target URL is required'},
                               status=status.HTTP_400_BAD_REQUEST)

            # Clean Instagram URLs by removing query parameters
            # BrightData API expects clean URLs like: https://www.instagram.com/username/
            # but rejects URLs with query params like: https://www.instagram.com/username/?hl=en
            try:
                parsed = urlparse(target_url)
                # Remove query parameters and fragments for Instagram URLs
                cleaned_parsed = parsed._replace(query='', fragment='')
                cleaned_url = urlunparse(cleaned_parsed)
                logger.info(f"Cleaned Instagram URL: {target_url} -> {cleaned_url}")
                target_url = cleaned_url
            except Exception as e:
                logger.warning(f"Could not clean Instagram URL {target_url}: {str(e)}")
                # Continue with original URL if parsing fails

            # Get content type and determine platform configuration key
            content_type = request.data.get('content_type', 'post')
            platform_config_key = f'instagram_{content_type}s'  # instagram_posts, instagram_reels, instagram_comments

            # Get the active Instagram configuration for specific content type
            config = BrightdataConfig.objects.filter(platform=platform_config_key, is_active=True).first()
            if not config:
                return Response({'error': f'No active {platform_config_key} Brightdata configuration found'},
                               status=status.HTTP_400_BAD_REQUEST)

            # Get optional parameters
            folder_id = request.data.get('folder_id')

            # Date handling - only include if provided
            start_date = request.data.get('start_date', '')
            end_date = request.data.get('end_date', '')

            # Prepare Brightdata API request
            url = "https://api.brightdata.com/datasets/v3/trigger"
            headers = {
                "Authorization": f"Bearer {config.api_token}",
                "Content-Type": "application/json",
            }
            params = {
                "dataset_id": config.dataset_id,
                "endpoint": "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/",
                "format": "json",
                "uncompressed_webhook": "true",
                "include_errors": "true",
                "type": "discover_new",
                "discover_by": "url",
            }

            # Create request payload based on content type
            if content_type == 'reel':
                # Instagram Reels API format
                data = [{
                    "url": target_url,
                    "start_date": start_date,
                    "end_date": end_date,
                    "all_reels": False,  # Default to specific date range
                }]
            else:
                # Instagram Posts API format (includes posts and other content types)
                data = [{
                    "url": target_url,
                    "num_of_posts": request.data.get('num_of_posts', 10),
                    "start_date": start_date,
                    "end_date": end_date,
                    "post_type": "Post" if content_type == 'post' else content_type.title(),
                    "posts_to_not_include": request.data.get('posts_to_not_include', []),
                }]

            # Log the request payload for debugging
            print(f"\n\n==== DEBUG: BRIGHTDATA API REQUEST ({platform_config_key.upper()}) ====")
            print(f"URL: {url}")
            print(f"Headers: {headers}")
            print(f"Params: {params}")
            print(f"Data: {data}")
            print(f"Configuration: {config.name} - {config.get_platform_display()}")

            # Show the actual request that would be made
            print(f"Final request URL: {url}?{urlencode(params)}")
            print(f"Final request body: {json.dumps(data)}")

            print("=======================================\n")

            # Create a scraper request record
            scraper_request = ScraperRequest.objects.create(
                config=config,
                platform=platform_config_key,
                content_type=content_type,
                target_url=target_url,
                num_of_posts=request.data.get('num_of_posts', 10),  # Use actual value from request
                folder_id=folder_id,
                request_payload=data,
                status='pending'
            )

            try:
                # Make the API request to Brightdata
                print("\n\n==== DEBUG: BRIGHTDATA API REQUEST (INSTAGRAM) ====")
                print(f"URL: {url}")
                print(f"Headers: {headers}")
                print(f"Params: {params}")
                print(f"Data: {data}")

                # Show the actual request that would be made
                print(f"Final request URL: {url}?{urlencode(params)}")
                print(f"Final request body: {json.dumps(data)}")

                print("=======================================\n")

                # ===== DETAILED DEBUG LOGGING FOR INDIVIDUAL REQUESTS =====
                print("\n" + "="*80)
                print("🐛 BRIGHTDATA API REQUEST DEBUG - INDIVIDUAL SCRAPER")
                print("="*80)
                print(f"Platform: {platform_config_key}")
                print(f"Config Name: {config.name}")
                print(f"Config ID: {config.id}")
                print()
                print("📡 REQUEST DETAILS:")
                print(f"URL: {url}")
                print(f"Headers: {headers}")
                print(f"Params: {params}")
                print(f"Data: {data}")
                print()
                print("🔍 COMPARISON WITH WORKING manualrun.py:")
                print("Working script uses:")
                print('  Authorization: Bearer c20a28d5-5c6c-43c3-9567-a6d7c193e727')
                print('  dataset_id: gd_lk5ns7kz21pck8jpis')
                print('  endpoint: https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/')
                print()
                print("This request uses:")
                print(f'  Authorization: {headers["Authorization"]}')
                print(f'  dataset_id: {params["dataset_id"]}')
                print(f'  endpoint: {params["endpoint"]}')
                print()

                # Check for differences
                working_token = "c20a28d5-5c6c-43c3-9567-a6d7c193e727"
                working_dataset = "gd_lk5ns7kz21pck8jpis"
                working_endpoint = "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/"

                if headers["Authorization"] != f"Bearer {working_token}":
                    print("❌ API TOKEN MISMATCH!")
                    print(f"   Expected: Bearer {working_token}")
                    print(f"   Got:      {headers['Authorization']}")
                else:
                    print("✅ API Token matches")

                if params["dataset_id"] != working_dataset:
                    print("❌ DATASET ID MISMATCH!")
                    print(f"   Expected: {working_dataset}")
                    print(f"   Got:      {params['dataset_id']}")
                else:
                    print("✅ Dataset ID matches")

                if params["endpoint"] != working_endpoint:
                    print("❌ ENDPOINT MISMATCH!")
                    print(f"   Expected: {working_endpoint}")
                    print(f"   Got:      {params['endpoint']}")
                else:
                    print("✅ Endpoint matches")

                print()
                print("🚀 MAKING API REQUEST...")
                print("="*80)

                response = requests.post(url, headers=headers, params=params, json=data)

                print("\n📥 BRIGHTDATA API RESPONSE:")
                print(f"Status Code: {response.status_code}")
                print(f"Response Headers: {dict(response.headers)}")
                print(f"Response Text: {response.text}")
                print("="*80 + "\n")

                # Try to parse the response as JSON
                try:
                    if response.text.strip():  # Check if response is not empty
                        response_data = response.json()
                    else:
                        # Handle empty response
                        response_data = {"error": "Empty response from Brightdata API"}
                        print("WARNING: Empty response from Brightdata API")
                except json.JSONDecodeError as json_err:
                    # Handle invalid JSON
                    print(f"ERROR: Could not parse Brightdata API response as JSON: {str(json_err)}")
                    response_data = {
                        "error": f"Invalid JSON response from Brightdata API: {str(json_err)}",
                        "raw_response": response.text
                    }

                # Log the API response for debugging
                logger.info(f"Brightdata API response: {response_data}")

                # Update the scraper request record
                scraper_request.response_metadata = response_data

                if response.status_code == 200 and "error" not in response_data:
                    scraper_request.status = 'processing'
                    # Try to get request_id safely
                    scraper_request.request_id = response_data.get('request_id', '') if isinstance(response_data, dict) else ''
                    return Response({
                        'status': 'Scraper request sent successfully',
                        'request_id': scraper_request.request_id,
                        'brightdata_response': response_data
                    })
                else:
                    scraper_request.status = 'failed'
                    error_message = response_data.get('error', 'Unknown error') if isinstance(response_data, dict) else str(response_data)
                    scraper_request.error_message = error_message
                    return Response({
                        'error': 'Failed to trigger Brightdata scraper',
                        'brightdata_response': response_data,
                        'status_code': response.status_code,
                        'raw_response': response.text
                    }, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                # Handle any exceptions in the API request
                logger.error(f"Error making Brightdata API request: {str(e)}")
                logger.error(traceback.format_exc())

                print("\n\n==== DEBUG: API REQUEST ERROR ====")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                print(f"Traceback:\n{traceback.format_exc()}")
                print("=======================================\n\n")

                scraper_request.status = 'failed'
                scraper_request.error_message = str(e)
                return Response({
                    'error': 'Error triggering Brightdata scraper',
                    'details': str(e),
                    'error_type': type(e).__name__
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            finally:
                # Save the scraper request record
                scraper_request.save()

        except Exception as outer_exception:
            # Catch-all for any unexpected errors
            logger.error(f"Unexpected error in trigger_instagram_scrape: {str(outer_exception)}")
            logger.error(traceback.format_exc())

            print("\n\n==== DEBUG: OUTER EXCEPTION ERROR ====")
            print(f"Error type: {type(outer_exception).__name__}")
            print(f"Error message: {str(outer_exception)}")
            print(f"Traceback:\n{traceback.format_exc()}")
            print("=======================================\n\n")

            return Response({
                'error': 'Unexpected server error',
                'details': str(outer_exception),
                'error_type': type(outer_exception).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['POST'])
    def trigger_linkedin_scrape(self, request):
        """Endpoint to trigger a LinkedIn scrape using Brightdata API"""
        logger = logging.getLogger(__name__)

        try:
            # Log the incoming request data for debugging
            logger.info(f"LinkedIn scraper request data: {request.data}")
            print("\n\n==== DEBUG: LINKEDIN SCRAPER REQUEST DATA ====")
            print(f"Request data: {request.data}")
            print("=======================================\n")

            # Get the active configuration
            config = BrightdataConfig.objects.filter(is_active=True).first()
            if not config:
                return Response({'error': 'No active Brightdata configuration found'},
                               status=status.HTTP_400_BAD_REQUEST)

            # Get request parameters
            target_url = request.data.get('target_url')
            if not target_url:
                return Response({'error': 'Target URL is required'},
                               status=status.HTTP_400_BAD_REQUEST)

            # Optional parameters with defaults
            content_type = request.data.get('content_type', 'post')
            num_of_posts = request.data.get('num_of_posts', 10)
            posts_to_not_include = request.data.get('posts_to_not_include', [])

            # Date handling - save original YYYY-MM-DD dates for database
            db_start_date = request.data.get('start_date', '')
            db_end_date = request.data.get('end_date', '')

            # Create API date versions in MM-DD-YYYY format
            api_start_date = ''
            api_end_date = ''

            # Validate and convert dates if provided
            if db_start_date:
                try:
                    # Verify it's in YYYY-MM-DD format
                    date_obj = datetime.strptime(db_start_date, '%Y-%m-%d')
                    # Convert to MM-DD-YYYY for API
                    api_start_date = date_obj.strftime('%m-%d-%Y')
                except ValueError:
                    return Response({'error': 'Invalid start_date format. Use YYYY-MM-DD format.'},
                                   status=status.HTTP_400_BAD_REQUEST)

            if db_end_date:
                try:
                    # Verify it's in YYYY-MM-DD format
                    date_obj = datetime.strptime(db_end_date, '%Y-%m-%d')
                    # Convert to MM-DD-YYYY for API
                    api_end_date = date_obj.strftime('%m-%d-%Y')
                except ValueError:
                    return Response({'error': 'Invalid end_date format. Use YYYY-MM-DD format.'},
                                   status=status.HTTP_400_BAD_REQUEST)

            folder_id = request.data.get('folder_id')

            # Prepare Brightdata API request
            url = "https://api.brightdata.com/datasets/v3/trigger"
            headers = {
                "Authorization": f"Bearer {config.api_token}",
                "Content-Type": "application/json",
            }
            params = {
                "dataset_id": config.dataset_id,
                "include_errors": "true",
            }

            # Create request payload as a direct array (not nested)
            # Use MM-DD-YYYY format for API
            data = [{
                "url": target_url,
                "num_of_posts": num_of_posts,
                "posts_to_not_include": posts_to_not_include,
                "start_date": api_start_date,
                "end_date": api_end_date,
            }]

            # Log the request payload for debugging
            print("\n\n==== DEBUG: BRIGHTDATA API REQUEST (LINKEDIN) ====")
            print(f"URL: {url}")
            print(f"Headers: {headers}")
            print(f"Params: {params}")
            print(f"Data: {data}")
            print(f"DB dates: start={db_start_date}, end={db_end_date}")
            print(f"API dates: start={api_start_date}, end={api_end_date}")

            # Show the actual request that would be made
            print(f"Final request URL: {url}?{urlencode(params)}")
            print(f"Final request body: {json.dumps(data)}")

            print("=======================================\n")

            # Create a scraper request record - use original YYYY-MM-DD for database
            scraper_request = ScraperRequest.objects.create(
                config=config,
                platform='linkedin',
                content_type=content_type,
                target_url=target_url,
                num_of_posts=num_of_posts,
                posts_to_not_include=str(posts_to_not_include) if posts_to_not_include else None,
                start_date=db_start_date if db_start_date else None,
                end_date=db_end_date if db_end_date else None,
                folder_id=folder_id,
                request_payload=data,
                status='pending'
            )

            try:
                # Make the API request to Brightdata
                print("\n\n==== DEBUG: BRIGHTDATA API REQUEST (LINKEDIN) ====")
                print(f"URL: {url}")
                print(f"Headers: {headers}")
                print(f"Params: {params}")
                print(f"Data: {data}")
                print(f"DB dates: start={db_start_date}, end={db_end_date}")
                print(f"API dates: start={api_start_date}, end={api_end_date}")

                # Show the actual request that would be made
                print(f"Final request URL: {url}?{urlencode(params)}")
                print(f"Final request body: {json.dumps(data)}")

                print("=======================================\n")

                response = requests.post(url, headers=headers, params=params, json=data)

                print("\n==== DEBUG: BRIGHTDATA API RESPONSE (LINKEDIN) ====")
                print(f"Status code: {response.status_code}")
                print(f"Response text: {response.text}")
                print("=======================================\n\n")

                # Try to parse the response as JSON
                try:
                    if response.text.strip():  # Check if response is not empty
                        response_data = response.json()
                    else:
                        # Handle empty response
                        response_data = {"error": "Empty response from Brightdata API"}
                        print("WARNING: Empty response from Brightdata API")
                except json.JSONDecodeError as json_err:
                    # Handle invalid JSON
                    print(f"ERROR: Could not parse Brightdata API response as JSON: {str(json_err)}")
                    response_data = {
                        "error": f"Invalid JSON response from Brightdata API: {str(json_err)}",
                        "raw_response": response.text
                    }

                # Log the API response for debugging
                logger.info(f"Brightdata API response: {response_data}")

                # Update the scraper request record
                scraper_request.response_metadata = response_data

                if response.status_code == 200 and "error" not in response_data:
                    scraper_request.status = 'processing'
                    # Try to get request_id safely
                    scraper_request.request_id = response_data.get('request_id', '') if isinstance(response_data, dict) else ''
                    return Response({
                        'status': 'Scraper request sent successfully',
                        'request_id': scraper_request.request_id,
                        'brightdata_response': response_data
                    })
                else:
                    scraper_request.status = 'failed'
                    error_message = response_data.get('error', 'Unknown error') if isinstance(response_data, dict) else str(response_data)
                    scraper_request.error_message = error_message
                    return Response({
                        'error': 'Failed to trigger Brightdata scraper',
                        'brightdata_response': response_data,
                        'status_code': response.status_code,
                        'raw_response': response.text
                    }, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                # Handle any exceptions in the API request
                logger.error(f"Error making Brightdata API request: {str(e)}")
                logger.error(traceback.format_exc())

                print("\n\n==== DEBUG: API REQUEST ERROR ====")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                print(f"Traceback:\n{traceback.format_exc()}")
                print("=======================================\n\n")

                scraper_request.status = 'failed'
                scraper_request.error_message = str(e)
                return Response({
                    'error': 'Error triggering Brightdata scraper',
                    'details': str(e),
                    'error_type': type(e).__name__
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            finally:
                # Save the scraper request record
                scraper_request.save()

        except Exception as outer_exception:
            # Catch-all for any unexpected errors
            logger.error(f"Unexpected error in trigger_linkedin_scrape: {str(outer_exception)}")
            logger.error(traceback.format_exc())

            print("\n\n==== DEBUG: OUTER EXCEPTION ERROR ====")
            print(f"Error type: {type(outer_exception).__name__}")
            print(f"Error message: {str(outer_exception)}")
            print(f"Traceback:\n{traceback.format_exc()}")
            print("=======================================\n\n")

            return Response({
                'error': 'Unexpected server error',
                'details': str(outer_exception),
                'error_type': type(outer_exception).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['POST'])
    def trigger_tiktok_scrape(self, request):
        """Endpoint to trigger a TikTok scrape using Brightdata API"""
        logger = logging.getLogger(__name__)

        try:
            # Log the incoming request data for debugging
            logger.info(f"TikTok scraper request data: {request.data}")
            print("\n\n==== DEBUG: TIKTOK SCRAPER REQUEST DATA ====")
            print(f"Request data: {request.data}")
            print("=======================================\n")

            # Get the active configuration
            config = BrightdataConfig.objects.filter(is_active=True).first()
            if not config:
                return Response({'error': 'No active Brightdata configuration found'},
                               status=status.HTTP_400_BAD_REQUEST)

            # Get request parameters
            target_url = request.data.get('target_url')
            if not target_url:
                return Response({'error': 'Target URL is required'},
                               status=status.HTTP_400_BAD_REQUEST)

            # Optional parameters with defaults
            content_type = request.data.get('content_type', 'post')
            num_of_posts = request.data.get('num_of_posts', 10)
            posts_to_not_include = request.data.get('posts_to_not_include', [])

            # Date handling - save original YYYY-MM-DD dates for database
            db_start_date = request.data.get('start_date', '')
            db_end_date = request.data.get('end_date', '')

            # Create API date versions in MM-DD-YYYY format
            api_start_date = ''
            api_end_date = ''

            # Validate and convert dates if provided
            if db_start_date:
                try:
                    # Verify it's in YYYY-MM-DD format
                    date_obj = datetime.strptime(db_start_date, '%Y-%m-%d')
                    # Convert to MM-DD-YYYY for API
                    api_start_date = date_obj.strftime('%m-%d-%Y')
                except ValueError:
                    return Response({'error': 'Invalid start_date format. Use YYYY-MM-DD format.'},
                                   status=status.HTTP_400_BAD_REQUEST)

            if db_end_date:
                try:
                    # Verify it's in YYYY-MM-DD format
                    date_obj = datetime.strptime(db_end_date, '%Y-%m-%d')
                    # Convert to MM-DD-YYYY for API
                    api_end_date = date_obj.strftime('%m-%d-%Y')
                except ValueError:
                    return Response({'error': 'Invalid end_date format. Use YYYY-MM-DD format.'},
                                   status=status.HTTP_400_BAD_REQUEST)

            folder_id = request.data.get('folder_id')

            # Prepare Brightdata API request
            url = "https://api.brightdata.com/datasets/v3/trigger"
            headers = {
                "Authorization": f"Bearer {config.api_token}",
                "Content-Type": "application/json",
            }
            params = {
                "dataset_id": config.dataset_id,
                "include_errors": "true",
            }

            # Create request payload as a direct array (not nested)
            # Use MM-DD-YYYY format for API
            data = [{
                "url": target_url,
                "num_of_posts": num_of_posts,
                "posts_to_not_include": posts_to_not_include,
                "start_date": api_start_date,
                "end_date": api_end_date,
            }]

            # Log the request payload for debugging
            print("\n\n==== DEBUG: BRIGHTDATA API REQUEST (TIKTOK) ====")
            print(f"URL: {url}")
            print(f"Headers: {headers}")
            print(f"Params: {params}")
            print(f"Data: {data}")
            print(f"DB dates: start={db_start_date}, end={db_end_date}")
            print(f"API dates: start={api_start_date}, end={api_end_date}")

            # Show the actual request that would be made
            print(f"Final request URL: {url}?{urlencode(params)}")
            print(f"Final request body: {json.dumps(data)}")

            print("=======================================\n")

            # Create a scraper request record - use original YYYY-MM-DD for database
            scraper_request = ScraperRequest.objects.create(
                config=config,
                platform='tiktok',
                content_type=content_type,
                target_url=target_url,
                num_of_posts=num_of_posts,
                posts_to_not_include=str(posts_to_not_include) if posts_to_not_include else None,
                start_date=db_start_date if db_start_date else None,
                end_date=db_end_date if db_end_date else None,
                folder_id=folder_id,
                request_payload=data,
                status='pending'
            )

            try:
                # Make the API request to Brightdata
                print("\n\n==== DEBUG: BRIGHTDATA API REQUEST (TIKTOK) ====")
                print(f"URL: {url}")
                print(f"Headers: {headers}")
                print(f"Params: {params}")
                print(f"Data: {data}")
                print(f"DB dates: start={db_start_date}, end={db_end_date}")
                print(f"API dates: start={api_start_date}, end={api_end_date}")

                # Show the actual request that would be made
                print(f"Final request URL: {url}?{urlencode(params)}")
                print(f"Final request body: {json.dumps(data)}")

                print("=======================================\n")

                response = requests.post(url, headers=headers, params=params, json=data)

                print("\n==== DEBUG: BRIGHTDATA API RESPONSE (TIKTOK) ====")
                print(f"Status code: {response.status_code}")
                print(f"Response text: {response.text}")
                print("=======================================\n\n")

                # Try to parse the response as JSON
                try:
                    if response.text.strip():  # Check if response is not empty
                        response_data = response.json()
                    else:
                        # Handle empty response
                        response_data = {"error": "Empty response from Brightdata API"}
                        print("WARNING: Empty response from Brightdata API")
                except json.JSONDecodeError as json_err:
                    # Handle invalid JSON
                    print(f"ERROR: Could not parse Brightdata API response as JSON: {str(json_err)}")
                    response_data = {
                        "error": f"Invalid JSON response from Brightdata API: {str(json_err)}",
                        "raw_response": response.text
                    }

                # Log the API response for debugging
                logger.info(f"Brightdata API response: {response_data}")

                # Update the scraper request record
                scraper_request.response_metadata = response_data

                if response.status_code == 200 and "error" not in response_data:
                    scraper_request.status = 'processing'
                    # Try to get request_id safely
                    scraper_request.request_id = response_data.get('request_id', '') if isinstance(response_data, dict) else ''
                    return Response({
                        'status': 'Scraper request sent successfully',
                        'request_id': scraper_request.request_id,
                        'brightdata_response': response_data
                    })
                else:
                    scraper_request.status = 'failed'
                    error_message = response_data.get('error', 'Unknown error') if isinstance(response_data, dict) else str(response_data)
                    scraper_request.error_message = error_message
                    return Response({
                        'error': 'Failed to trigger Brightdata scraper',
                        'brightdata_response': response_data,
                        'status_code': response.status_code,
                        'raw_response': response.text
                    }, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                # Handle any exceptions in the API request
                logger.error(f"Error making Brightdata API request: {str(e)}")
                logger.error(traceback.format_exc())

                print("\n\n==== DEBUG: API REQUEST ERROR ====")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                print(f"Traceback:\n{traceback.format_exc()}")
                print("=======================================\n\n")

                scraper_request.status = 'failed'
                scraper_request.error_message = str(e)
                return Response({
                    'error': 'Error triggering Brightdata scraper',
                    'details': str(e),
                    'error_type': type(e).__name__
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            finally:
                # Save the scraper request record
                scraper_request.save()

        except Exception as outer_exception:
            # Catch-all for any unexpected errors
            logger.error(f"Unexpected error in trigger_tiktok_scrape: {str(outer_exception)}")
            logger.error(traceback.format_exc())

            print("\n\n==== DEBUG: OUTER EXCEPTION ERROR ====")
            print(f"Error type: {type(outer_exception).__name__}")
            print(f"Error message: {str(outer_exception)}")
            print(f"Traceback:\n{traceback.format_exc()}")
            print("=======================================\n\n")

            return Response({
                'error': 'Unexpected server error',
                'details': str(outer_exception),
                'error_type': type(outer_exception).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['POST'])
    def test_connection(self, request):
        """Test the connection to Brightdata API with active configuration"""
        import traceback
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Get the active configuration
            config = BrightdataConfig.objects.filter(is_active=True).first()
            if not config:
                return Response({'error': 'No active Brightdata configuration found'},
                               status=status.HTTP_400_BAD_REQUEST)

            # Test URL for Brightdata API
            url = "https://api.brightdata.com/datasets/v3/status"  # Use status endpoint for testing
            headers = {
                "Authorization": f"Bearer {config.api_token}",
                "Content-Type": "application/json",
            }
            params = {
                "dataset_id": config.dataset_id,
            }

            # Log the test request
            print("\n\n==== DEBUG: BRIGHTDATA TEST CONNECTION ====")
            print(f"URL: {url}")
            print(f"Headers: {headers}")
            print(f"Params: {params}")
            print("=======================================\n")

            # Make the API request to Brightdata
            response = requests.get(url, headers=headers, params=params)

            # Log the test response
            print("\n==== DEBUG: BRIGHTDATA TEST RESPONSE ====")
            print(f"Status code: {response.status_code}")
            print(f"Response text: {response.text}")
            print("=======================================\n\n")

            # Process response
            if response.status_code == 200:
                try:
                    if response.text.strip():  # Check if response is not empty
                        response_data = response.json()
                        return Response({
                            'status': 'Connection successful',
                            'brightdata_response': response_data
                        })
                    else:
                        return Response({
                            'status': 'Connection successful but response is empty',
                            'response_text': response.text
                        })
                except json.JSONDecodeError as json_err:
                    # Handle invalid JSON
                    print(f"ERROR: Could not parse Brightdata API response as JSON: {str(json_err)}")
                    return Response({
                        'status': 'Connection successful but response is not valid JSON',
                        'error': f"Invalid JSON response: {str(json_err)}",
                        'response_text': response.text
                    })
            else:
                try:
                    if response.text.strip():  # Check if response is not empty
                        try:
                            error_data = response.json()
                            return Response({
                                'error': 'Connection failed',
                                'brightdata_error': error_data,
                                'status_code': response.status_code,
                            }, status=status.HTTP_400_BAD_REQUEST)
                        except json.JSONDecodeError:
                            return Response({
                                'error': 'Connection failed',
                                'response_text': response.text,
                                'status_code': response.status_code,
                            }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({
                            'error': 'Connection failed',
                            'response_text': 'Empty response',
                            'status_code': response.status_code,
                        }, status=status.HTTP_400_BAD_REQUEST)
                except Exception as parse_err:
                    return Response({
                        'error': 'Connection failed',
                        'response_text': response.text,
                        'parse_error': str(parse_err),
                        'status_code': response.status_code,
                    }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any exceptions
            logger.error(f"Error testing Brightdata connection: {str(e)}")
            logger.error(traceback.format_exc())

            print("\n\n==== DEBUG: TEST CONNECTION ERROR ====")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print(f"Traceback:\n{traceback.format_exc()}")
            print("=======================================\n\n")

            return Response({
                'error': 'Error testing Brightdata connection',
                'details': str(e),
                'error_type': type(e).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
def brightdata_webhook(request):
    """
    Simplified webhook endpoint for reliable data processing
    """
    import time

    start_time = time.time()
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')

    try:
        # Parse the incoming data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            logger.error(f"Unsupported content type: {request.content_type}")
            return JsonResponse({'error': 'Unsupported content type'}, status=400)

        # Extract metadata from headers or query params
        snapshot_id = (request.headers.get('X-Snapshot-Id') or
                      request.headers.get('X-Brightdata-Snapshot-Id') or
                      request.GET.get('snapshot_id'))
        platform = (request.headers.get('X-Platform') or
                   request.GET.get('platform', 'instagram'))

        logger.info(f"Received webhook data for snapshot_id: {snapshot_id}, platform: {platform}")

        # Find ALL corresponding scraper requests (for batch jobs, multiple requests share the same snapshot_id)
        scraper_requests = []
        if snapshot_id:
            try:
                scraper_requests = list(ScraperRequest.objects.filter(request_id=snapshot_id))
                if scraper_requests:
                    logger.info(f"Found {len(scraper_requests)} scraper requests for snapshot_id: {snapshot_id}")
                    for req in scraper_requests:
                        logger.info(f"  - Request {req.id}: {req.target_url} -> folder_id: {req.folder_id}")
                else:
                    logger.warning(f"No scraper requests found for snapshot_id: {snapshot_id}")
            except Exception as e:
                logger.error(f"Error finding scraper requests for snapshot_id {snapshot_id}: {str(e)}")

        # Process the data based on platform
        success = _process_webhook_data_with_batch_support(data, platform, scraper_requests)

        if success:
            # Update all scraper request statuses
            for scraper_request in scraper_requests:
                scraper_request.status = 'completed'
                scraper_request.save()

            # Update workflow task statuses if this is part of a workflow
            workflow_tasks_updated = 0
            scraping_jobs_updated = 0
            for scraper_request in scraper_requests:
                if scraper_request.batch_job:
                    try:
                        # Update WorkflowTask statuses (legacy)
                        from workflow.models import WorkflowTask
                        workflow_tasks = WorkflowTask.objects.filter(batch_job=scraper_request.batch_job)
                        for workflow_task in workflow_tasks:
                            workflow_task.status = 'completed'
                            workflow_task.save()
                            workflow_tasks_updated += 1
                        
                        # Update specific ScrapingJob statuses (new workflow system)
                        # Match by URL and platform to ensure we update the correct job
                        from workflow.models import ScrapingJob
                        matching_scraping_jobs = ScrapingJob.objects.filter(
                            batch_job=scraper_request.batch_job,
                            url=scraper_request.target_url
                        )
                        for scraping_job in matching_scraping_jobs:
                            scraping_job.status = 'completed'
                            scraping_job.completed_at = timezone.now()
                            scraping_job.save()
                            scraping_jobs_updated += 1
                            logger.info(f"Updated ScrapingJob {scraping_job.id} to completed for URL: {scraper_request.target_url}")
                            
                    except Exception as e:
                        logger.error(f"Error updating workflow statuses: {str(e)}")

            if scraper_requests:
                logger.info(f"Updated {len(scraper_requests)} scraper request statuses to completed")
            if workflow_tasks_updated > 0:
                logger.info(f"Updated {workflow_tasks_updated} workflow task statuses to completed")
            if scraping_jobs_updated > 0:
                logger.info(f"Updated {scraping_jobs_updated} scraping job statuses to completed")

            processing_time = round(time.time() - start_time, 3)
            logger.info(f"Webhook processed successfully: {snapshot_id} in {processing_time}s")

            return JsonResponse({
                'status': 'success',
                'message': 'Data processed successfully',
                'snapshot_id': snapshot_id,
                'processing_time': processing_time,
                'items_processed': len(data) if isinstance(data, list) else 1,
                'scraper_requests_updated': len(scraper_requests),
                'workflow_tasks_updated': workflow_tasks_updated,
                'scraping_jobs_updated': scraping_jobs_updated
            })
        else:
            # Update all scraper request statuses to failed
            for scraper_request in scraper_requests:
                scraper_request.status = 'failed'
                scraper_request.error_message = 'Failed to process webhook data'
                scraper_request.save()

            # Update workflow task statuses to failed if this is part of a workflow
            workflow_tasks_failed = 0
            scraping_jobs_failed = 0
            for scraper_request in scraper_requests:
                if scraper_request.batch_job:
                    try:
                        # Update WorkflowTask statuses to failed (legacy)
                        from workflow.models import WorkflowTask
                        workflow_tasks = WorkflowTask.objects.filter(batch_job=scraper_request.batch_job)
                        for workflow_task in workflow_tasks:
                            workflow_task.status = 'failed'
                            workflow_task.save()
                            workflow_tasks_failed += 1
                        
                        # Update specific ScrapingJob statuses to failed (new workflow system)
                        # Match by URL and platform to ensure we update the correct job
                        from workflow.models import ScrapingJob
                        matching_scraping_jobs = ScrapingJob.objects.filter(
                            batch_job=scraper_request.batch_job,
                            url=scraper_request.target_url
                        )
                        for scraping_job in matching_scraping_jobs:
                            scraping_job.status = 'failed'
                            scraping_job.error_message = 'Failed to process webhook data'
                            scraping_job.completed_at = timezone.now()
                            scraping_job.save()
                            scraping_jobs_failed += 1
                            logger.info(f"Updated ScrapingJob {scraping_job.id} to failed for URL: {scraper_request.target_url}")
                            
                    except Exception as e:
                        logger.error(f"Error updating workflow statuses to failed: {str(e)}")

            if workflow_tasks_failed > 0:
                logger.info(f"Updated {workflow_tasks_failed} workflow task statuses to failed")
            if scraping_jobs_failed > 0:
                logger.info(f"Updated {scraping_jobs_failed} scraping job statuses to failed")

            logger.error(f"Failed to process webhook data for snapshot_id: {snapshot_id}")
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to process webhook data',
                'processing_time': round(time.time() - start_time, 3)
            }, status=500)

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook request: {str(e)}")
        return JsonResponse({'error': 'Invalid JSON', 'details': str(e)}, status=400)

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'error': 'Internal server error',
            'details': str(e),
            'processing_time': round(time.time() - start_time, 3)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def brightdata_notify(request):
    """
    Notification endpoint to receive status updates from BrightData
    """
    from .models import BrightdataNotification

    try:
        # Parse notification data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            # Handle form-encoded data
            data = dict(request.POST.items())

        # Handle both dict and list data structures
        if isinstance(data, dict):
            snapshot_id = data.get('snapshot_id') or data.get('request_id')
            status_update = data.get('status', 'unknown')
            message = data.get('message', '')
        else:
            # If data is not a dict (e.g., list), try to get from query params
            snapshot_id = request.GET.get('snapshot_id') or request.GET.get('request_id')
            status_update = request.GET.get('status', 'unknown')
            message = request.GET.get('message', '')

        logger.info(f"Received notification: snapshot_id={snapshot_id}, status={status_update}, message={message}")

        # Find the corresponding scraper request
        scraper_request = None
        if snapshot_id:
            try:
                scraper_request = ScraperRequest.objects.get(request_id=snapshot_id)
                logger.info(f"Found scraper request {scraper_request.id} for snapshot_id: {snapshot_id}")
            except ScraperRequest.DoesNotExist:
                logger.warning(f"No scraper request found for snapshot_id: {snapshot_id}")

        # Create notification record
        notification = BrightdataNotification.objects.create(
            snapshot_id=snapshot_id or 'unknown',
            status=status_update,
            message=message,
            scraper_request=scraper_request,
            raw_data=data,
            request_ip=request.META.get('REMOTE_ADDR'),
            request_headers=dict(request.headers),
            processed_at=timezone.now()
        )

        # Update scraper request status if found
        if scraper_request:
            # Update status based on notification
            if status_update in ['completed', 'finished']:
                scraper_request.status = 'completed'
                scraper_request.completed_at = timezone.now()
            elif status_update in ['failed', 'error']:
                scraper_request.status = 'failed'
                scraper_request.error_message = message
            elif status_update in ['running', 'processing']:
                scraper_request.status = 'processing'
                if not scraper_request.started_at:
                    scraper_request.started_at = timezone.now()

            scraper_request.save()
            logger.info(f"Updated scraper request {scraper_request.id} status to {scraper_request.status}")

        return JsonResponse({
            'status': 'success',
            'message': 'Notification processed successfully',
            'notification_id': notification.id,
            'scraper_request_updated': scraper_request is not None
        })

    except json.JSONDecodeError:
        logger.error("Invalid JSON in notification request")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing notification: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def _verify_webhook_auth(auth_header: str) -> bool:
    """
    Verify webhook authentication
    """
    try:
        # Get webhook auth token from BrightData config
        # You can store this in your BrightdataConfig model or settings
        from django.conf import settings
        expected_token = getattr(settings, 'BRIGHTDATA_WEBHOOK_TOKEN', 'your-webhook-secret-token')

        # Support both "Bearer token" and "token" formats
        token = auth_header.replace('Bearer ', '').strip()
        return token == expected_token

    except Exception as e:
        logger.error(f"Error verifying webhook auth: {str(e)}")
        return False

def _process_webhook_data_with_batch_support(data, platform: str, scraper_requests):
    """
    Process incoming webhook data with support for batch jobs (multiple scraper requests)
    All posts from the same job go into the SAME shared folder
    """
    try:
        # Import platform-specific models
        from facebook_data.models import FacebookPost
        from instagram_data.models import InstagramPost
        from linkedin_data.models import LinkedInPost
        from tiktok_data.models import TikTokPost

        # Platform to model mapping
        platform_models = {
            'facebook': FacebookPost,
            'instagram': InstagramPost,
            'linkedin': LinkedInPost,
            'tiktok': TikTokPost,
        }

        PostModel = platform_models.get(platform.lower())
        if not PostModel:
            logger.error(f"No model found for platform: {platform}")
            return False

        # Extract posts from data
        posts_data = data if isinstance(data, list) else data.get('data', [])

        # Filter out invalid entries (warnings, errors, entries without required fields)
        valid_posts = []
        skipped_count = 0

        for post_data in posts_data:
            # Skip entries with warnings or errors
            if post_data.get('warning') or post_data.get('error') or post_data.get('warning_code'):
                skipped_count += 1
                logger.info(f"Skipping warning/error entry: {post_data.get('warning', post_data.get('error', 'Unknown warning'))}")
                continue

            # Skip entries without essential fields
            if platform.lower() == 'instagram':
                # For Instagram, we need either 'url' or 'post_id'
                if not (post_data.get('url') or post_data.get('post_id') or post_data.get('pk')):
                    skipped_count += 1
                    logger.info(f"Skipping Instagram entry without URL or post_id: {post_data}")
                    continue
            elif platform.lower() == 'facebook':
                # For Facebook, we need either 'url' or 'post_id'
                if not (post_data.get('url') or post_data.get('post_id')):
                    skipped_count += 1
                    logger.info(f"Skipping Facebook entry without URL or post_id: {post_data}")
                    continue
            else:
                # For other platforms, we need at least 'url' or 'post_id'
                if not (post_data.get('url') or post_data.get('post_id') or post_data.get('id')):
                    skipped_count += 1
                    logger.info(f"Skipping {platform} entry without URL or ID: {post_data}")
                    continue

            valid_posts.append(post_data)

        logger.info(f"Processing {len(valid_posts)} valid posts, skipped {skipped_count} invalid entries")

        # 🔧 SIMPLIFIED LOGIC: Use the SAME folder for ALL posts in this batch job
        # All scraper requests in the same batch job should have the same folder_id
        shared_folder_id = None
        if scraper_requests:
            # Get the folder_id from the first request (all should be the same now)
            shared_folder_id = scraper_requests[0].folder_id
            logger.info(f"✅ Using SHARED folder_id: {shared_folder_id} for ALL posts in this batch")

            # Log all folder_ids to verify they're the same
            folder_ids = [req.folder_id for req in scraper_requests if req.folder_id]
            if len(set(folder_ids)) > 1:
                logger.warning(f"⚠️  Multiple folder_ids found in batch: {folder_ids}. Using first one: {shared_folder_id}")
            else:
                logger.info(f"✅ All {len(scraper_requests)} requests use the same folder_id: {shared_folder_id}")

        created_count = 0

        for post_data in valid_posts:
            try:
                # Map common fields
                post_fields = _map_post_fields(post_data, platform)

                # 🔧 SIMPLIFIED: ALL posts go to the SAME shared folder
                folder_id = shared_folder_id

                # Handle folder assignment for all platforms
                if folder_id:
                    if platform.lower() == 'facebook':
                        from facebook_data.models import Folder
                        try:
                            folder = Folder.objects.get(id=folder_id)
                            post_fields['folder'] = folder
                        except Folder.DoesNotExist:
                            logger.warning(f"Facebook folder with ID {folder_id} not found, creating default folder")
                            folder = Folder.objects.create(name=f"Auto-created folder {folder_id}")
                            post_fields['folder'] = folder

                    elif platform.lower() == 'instagram':
                        from instagram_data.models import Folder
                        try:
                            folder = Folder.objects.get(id=folder_id)
                            post_fields['folder'] = folder
                            logger.info(f"✅ Assigned Instagram post to SHARED folder: {folder.name} (ID: {folder_id})")
                        except Folder.DoesNotExist:
                            logger.warning(f"Instagram folder with ID {folder_id} not found, creating default folder")
                            folder = Folder.objects.create(name=f"Auto-created folder {folder_id}")
                            post_fields['folder'] = folder

                    elif platform.lower() == 'linkedin':
                        from linkedin_data.models import Folder
                        try:
                            folder = Folder.objects.get(id=folder_id)
                            post_fields['folder'] = folder
                        except Folder.DoesNotExist:
                            logger.warning(f"LinkedIn folder with ID {folder_id} not found, creating default folder")
                            folder = Folder.objects.create(name=f"Auto-created folder {folder_id}")
                            post_fields['folder'] = folder

                    elif platform.lower() == 'tiktok':
                        from tiktok_data.models import Folder
                        try:
                            folder = Folder.objects.get(id=folder_id)
                            post_fields['folder'] = folder
                        except Folder.DoesNotExist:
                            logger.warning(f"TikTok folder with ID {folder_id} not found, creating default folder")
                            folder = Folder.objects.create(name=f"Auto-created folder {folder_id}")
                            post_fields['folder'] = folder
                else:
                    logger.warning(f"No shared folder_id available for posts")

                # Create or update post
                post_id = post_data.get('post_id') or post_data.get('id') or post_data.get('pk')
                if post_id:
                    # For all platforms, check uniqueness by post_id and folder (if folder exists)
                    folder = post_fields.get('folder')
                    if folder:
                        # If post has a folder, check uniqueness by post_id and folder
                        post, created = PostModel.objects.get_or_create(
                            post_id=post_id,
                            folder=folder,
                            defaults=post_fields
                        )
                    else:
                        # If no folder, check uniqueness by post_id only
                        post, created = PostModel.objects.get_or_create(
                            post_id=post_id,
                            defaults=post_fields
                        )
                    if created:
                        created_count += 1
                        user_posted = post_data.get('user_posted', 'Unknown')
                        logger.info(f"✅ Created new {platform} post: {post_id} from @{user_posted} in SHARED folder: {folder.name if folder else 'No folder'}")
                    else:
                        logger.info(f"Updated existing {platform} post: {post_id}")
                else:
                    # Create new post without checking for duplicates
                    post = PostModel.objects.create(**post_fields)
                    created_count += 1
                    user_posted = post_data.get('user_posted', 'Unknown')
                    logger.info(f"Created new {platform} post from @{user_posted} without ID in SHARED folder: {folder.name if post_fields.get('folder') else 'No folder'}")

            except Exception as e:
                logger.error(f"Error processing individual post: {str(e)}")
                logger.error(f"Post data: {post_data}")
                continue

        logger.info(f"✅ Successfully processed {created_count} valid posts for platform {platform} into SHARED folder")
        return True

    except Exception as e:
        logger.error(f"Error processing webhook data: {str(e)}")
        return False

def _process_webhook_data(data, platform: str, scraper_request=None):
    """
    Legacy function - redirects to batch support version
    """
    scraper_requests = [scraper_request] if scraper_request else []
    return _process_webhook_data_with_batch_support(data, platform, scraper_requests)

def _map_post_fields(post_data: dict, platform: str) -> dict:
    """
    Map BrightData post fields to our model fields based on actual BrightData JSON structure
    """

    if platform.lower() == 'instagram':
        # Map Instagram-specific fields based on actual BrightData structure
        mapped_data = {
            'url': post_data.get('url', ''),
            'post_id': post_data.get('post_id', '') or post_data.get('pk', ''),
            'user_posted': post_data.get('user_posted', '') or post_data.get('user_name', '') or post_data.get('username', ''),
            'description': post_data.get('description', '') or post_data.get('caption', '') or post_data.get('text', ''),
            'hashtags': post_data.get('hashtags', []),
            'num_comments': post_data.get('num_comments', 0) or post_data.get('comments', 0) or post_data.get('comments_count', 0),
            'date_posted': post_data.get('date_posted', '') or post_data.get('date', '') or post_data.get('timestamp', ''),
            'likes': post_data.get('likes', 0) or post_data.get('likes_count', 0),
            'photos': post_data.get('photos', []),
            'videos': post_data.get('videos', []),
            'thumbnail': post_data.get('thumbnail', ''),
            'views': post_data.get('views', 0),
            'video_play_count': post_data.get('video_play_count', 0),
            'video_view_count': post_data.get('video_view_count', 0),
            'length': post_data.get('length', ''),
            'video_url': post_data.get('video_url', ''),
            'audio_url': post_data.get('audio_url', ''),
            'shortcode': post_data.get('shortcode', ''),
            'content_id': post_data.get('content_id', ''),
            'instagram_pk': post_data.get('pk', '') or post_data.get('instagram_pk', ''),
            'content_type': post_data.get('content_type', ''),
            'platform_type': post_data.get('platform_type', ''),
            'product_type': post_data.get('product_type', ''),
            'user_posted_id': post_data.get('user_posted_id', '') or post_data.get('user_id', ''),
            'followers': post_data.get('followers', 0),
            'posts_count': post_data.get('posts_count', 0),
            'following': post_data.get('following', 0),
            'profile_image_link': post_data.get('profile_image_link', ''),
            'user_profile_url': post_data.get('user_profile_url', ''),
            'profile_url': post_data.get('profile_url', ''),
            'is_verified': post_data.get('is_verified', False),
            'is_paid_partnership': post_data.get('is_paid_partnership', False),
            'partnership_details': post_data.get('partnership_details', {}),
            'coauthor_producers': post_data.get('coauthor_producers', []),
            'location': post_data.get('location', ''),
            'latest_comments': post_data.get('latest_comments', []),
            'top_comments': post_data.get('top_comments', []),
            'engagement_score': post_data.get('engagement_score', 0.0),
            'engagement_score_view': post_data.get('engagement_score_view', 0),
            'tagged_users': post_data.get('tagged_users', []),
            'audio': post_data.get('audio', {}),
            'post_content': post_data.get('post_content', {}),
            'videos_duration': post_data.get('videos_duration', {}),
            'images': post_data.get('images', []),
            'photos_number': post_data.get('photos_number', 0),
            'alt_text': post_data.get('alt_text', ''),
            'discovery_input': post_data.get('discovery_input', ''),
            'has_handshake': post_data.get('has_handshake', False),
        }
        return mapped_data

    elif platform.lower() == 'facebook':
        # Map Facebook-specific fields based on actual BrightData structure
        mapped_data = {
            'url': post_data.get('url', ''),
            'post_id': post_data.get('post_id', ''),
            'user_url': post_data.get('user_url', ''),
            'user_username_raw': post_data.get('user_username_raw', ''),
            'content': post_data.get('content', ''),
            'date_posted': post_data.get('date_posted'),
            'num_comments': post_data.get('num_comments', 0),
            'num_shares': post_data.get('num_shares', 0),
            'likes': post_data.get('likes', 0),
            'video_view_count': post_data.get('video_view_count'),
            'page_name': post_data.get('page_name', ''),
            'profile_id': post_data.get('profile_id', ''),
            'page_intro': post_data.get('page_intro', ''),
            'page_category': post_data.get('page_category', ''),
            'page_logo': post_data.get('page_logo', ''),
            'page_external_website': post_data.get('page_external_website', ''),
            'page_likes': post_data.get('page_likes'),
            'page_followers': post_data.get('page_followers'),
            'page_is_verified': post_data.get('page_is_verified', False),
            'page_phone': post_data.get('page_phone', ''),
            'page_email': post_data.get('page_email', ''),
            'page_creation_time': post_data.get('page_creation_time'),
            'page_reviews_score': post_data.get('page_reviews_score', ''),
            'page_reviewers_amount': post_data.get('page_reviewers_amount'),
            'page_price_range': post_data.get('page_price_range', ''),
            'attachments_data': post_data.get('attachments'),
            'post_external_image': post_data.get('post_external_image'),
            'page_url': post_data.get('page_url', ''),
            'header_image': post_data.get('header_image', ''),
            'avatar_image_url': post_data.get('avatar_image_url', ''),
            'profile_handle': post_data.get('profile_handle', ''),
            'is_sponsored': post_data.get('is_sponsored', False),
            'shortcode': post_data.get('shortcode', ''),
            'is_page': post_data.get('is_page', False),
            'about': post_data.get('about'),
            'active_ads_urls': post_data.get('active_ads_urls'),
            'delegate_page_id': post_data.get('delegate_page_id', ''),
            'post_type': post_data.get('post_type', ''),
            'timestamp': post_data.get('timestamp'),
            'input': post_data.get('input'),
            'num_likes_type': post_data.get('num_likes_type'),
            'count_reactions_type': post_data.get('count_reactions_type'),
        }
        return mapped_data

    # Generic mapping for other platforms
    common_mapping = {
        'url': post_data.get('url', ''),
        'post_id': post_data.get('post_id') or post_data.get('id', ''),
        'content': post_data.get('text') or post_data.get('content') or post_data.get('description', ''),
        'date_posted': post_data.get('date') or post_data.get('created_time') or post_data.get('timestamp'),
        'likes': post_data.get('likes_count') or post_data.get('likes') or 0,
        'num_comments': post_data.get('comments_count') or post_data.get('comments') or 0,
        'num_shares': post_data.get('shares_count') or post_data.get('shares') or 0,
        'user_posted': post_data.get('username') or post_data.get('author') or post_data.get('user', ''),
    }

    return common_mapping

class BatchScraperJobViewSet(viewsets.ModelViewSet):
    """API endpoint for automated batch scraper jobs"""
    queryset = BatchScraperJob.objects.all()
    serializer_class = BatchScraperJobSerializer
    permission_classes = [AllowAny]  # For testing, use proper permissions in production

    def get_serializer_class(self):
        if self.action == 'create':
            return BatchScraperJobCreateSerializer
        return self.serializer_class

    def get_queryset(self):
        """Filter by project if specified"""
        queryset = BatchScraperJob.objects.all()
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset.order_by('-created_at')

    @action(detail=True, methods=['POST'])
    def execute(self, request, pk=None):
        """Execute a batch scraper job"""
        job = self.get_object()

        if job.status != 'pending':
            return Response({'error': 'Job can only be executed if it is in pending status'},
                           status=status.HTTP_400_BAD_REQUEST)

        try:
            scraper = AutomatedBatchScraper()
            success = scraper.execute_batch_job(job.id)

            if success:
                return Response({'status': 'Job execution started successfully'})
            else:
                return Response({'error': 'Failed to start job execution'},
                               status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': f'Error executing job: {str(e)}'},
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk=None):
        """Cancel a batch scraper job"""
        job = self.get_object()

        if job.status in ['completed', 'failed', 'cancelled']:
            return Response({'error': 'Job cannot be cancelled in its current status'},
                           status=status.HTTP_400_BAD_REQUEST)

        job.status = 'cancelled'
        job.completed_at = timezone.now()
        job.save()

        return Response({'status': 'Job cancelled successfully'})

    def update(self, request, *args, **kwargs):
        """Update a batch scraper job"""
        try:
            # ===== DETAILED CONSOLE LOGGING FOR FRONTEND =====
            print("\n" + "="*80)
            print("🔄 BATCH JOB UPDATE - BACKEND DEBUG")
            print("="*80)
            print(f"Request Data: {request.data}")
            print(f"Request Method: {request.method}")
            print(f"Request Path: {request.path}")
            print("="*80)

            # Get the job instance
            job = self.get_object()
            
            # Update the job with the new data
            job.name = request.data.get('name', job.name)
            job.platforms_to_scrape = request.data.get('platforms_to_scrape', job.platforms_to_scrape)
            job.content_types_to_scrape = request.data.get('content_types_to_scrape', job.content_types_to_scrape)
            job.num_of_posts = request.data.get('num_of_posts', job.num_of_posts)
            job.start_date = request.data.get('start_date', job.start_date)
            job.end_date = request.data.get('end_date', job.end_date)
            job.auto_create_folders = request.data.get('auto_create_folders', job.auto_create_folders)
            job.output_folder_pattern = request.data.get('output_folder_pattern', job.output_folder_pattern)
            job.platform_params = request.data.get('platform_params', job.platform_params)
            
            job.save()

            print(f"✅ Job Updated:")
            print(f"   Job ID: {job.id}")
            print(f"   Job Name: {job.name}")
            print(f"   Platforms: {job.platforms_to_scrape}")
            print(f"   Content Types: {job.content_types_to_scrape}")
            print("="*80 + "\n")

            return Response({
                'job_id': job.id,
                'success': True,
                'message': 'Batch job updated successfully',
                'debug_info': {
                    'platforms': job.platforms_to_scrape,
                    'content_types': job.content_types_to_scrape,
                    'num_of_posts': job.num_of_posts,
                    'job_name': job.name
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ Exception in update:")
            print(f"   Error: {str(e)}")
            print("="*80 + "\n")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def create_and_execute(self, request):
        """Create and execute a batch scraper job"""
        try:
            # ===== DETAILED CONSOLE LOGGING FOR FRONTEND =====
            print("\n" + "="*80)
            print("🚀 BATCH JOB CREATE_AND_EXECUTE - BACKEND DEBUG")
            print("="*80)
            print(f"Request Data: {request.data}")
            print(f"Request Method: {request.method}")
            print(f"Request Path: {request.path}")
            print("="*80)

            job, success = create_and_execute_batch_job(
                name=request.data.get('name'),
                project_id=request.data.get('project'),
                source_folder_ids=request.data.get('source_folder_ids', []),
                platforms_to_scrape=request.data.get('platforms_to_scrape'),
                content_types_to_scrape=request.data.get('content_types_to_scrape', {}),
                num_of_posts=request.data.get('num_of_posts', 10),
                start_date=request.data.get('start_date'),
                end_date=request.data.get('end_date'),
                auto_create_folders=request.data.get('auto_create_folders', True),
                output_folder_pattern=request.data.get('output_folder_pattern'),
                platform_params=request.data.get('platform_params', {})
            )

            print(f"✅ Job Created and Executed:")
            print(f"   Job ID: {job.id}")
            print(f"   Job Name: {job.name}")
            print(f"   Success: {success}")
            print(f"   Platforms: {job.platforms_to_scrape}")
            print(f"   Content Types: {job.content_types_to_scrape}")
            print("="*80 + "\n")

            return Response({
                'job_id': job.id,
                'success': success,
                'message': f'Batch job {"completed successfully" if success else "failed"}',
                'debug_info': {
                    'platforms': job.platforms_to_scrape,
                    'content_types': job.content_types_to_scrape,
                    'num_of_posts': job.num_of_posts,
                    'job_name': job.name
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"❌ Exception in create_and_execute:")
            print(f"   Error: {str(e)}")
            print("="*80 + "\n")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def scrape_comments(request):
    """
    Cross-platform comments scraping endpoint

    Expected payload:
    {
        "platform": "facebook_comments" | "instagram_comments",
        "post_urls": ["url1", "url2", ...],
        "comment_limit": 10,
        "get_all_replies": false,
        "result_folder_name": "Comments_Campaign_2024"
    }
    """
    try:
        # Get request parameters
        platform = request.data.get('platform')
        post_urls = request.data.get('post_urls', [])
        comment_limit = request.data.get('comment_limit', 10)
        get_all_replies = request.data.get('get_all_replies', False)
        result_folder_name = request.data.get('result_folder_name')

        # Validate required parameters
        if not platform:
            return Response({'error': 'Platform is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not post_urls or not isinstance(post_urls, list):
            return Response({'error': 'Post URLs list is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not result_folder_name:
            return Response({'error': 'Result folder name is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate platform is a comment platform
        if not platform.endswith('_comments'):
            return Response({'error': 'Invalid platform. Must be a comments platform (e.g., facebook_comments, instagram_comments)'},
                          status=status.HTTP_400_BAD_REQUEST)

        # Check if configuration exists for the platform
        try:
            config = BrightdataConfig.objects.get(platform=platform, is_active=True)
        except BrightdataConfig.DoesNotExist:
            return Response({'error': f'No active configuration found for {platform}. Please configure it in BrightData Settings.'},
                          status=status.HTTP_400_BAD_REQUEST)

        # Determine the base platform (facebook, instagram)
        base_platform = platform.split('_')[0]

        # Import the appropriate service based on platform
        if base_platform == 'facebook':
            from facebook_data.services import scrape_facebook_comments_from_urls

            # Get project ID from request or default
            project_id = request.data.get('project_id', 1)

            # Use the URL-based Facebook comment scraper
            result, success = scrape_facebook_comments_from_urls(
                post_urls=post_urls,
                comment_limit=comment_limit,
                get_all_replies=get_all_replies,
                result_folder_name=result_folder_name,
                project_id=project_id
            )

            return Response({
                'success': success,
                'message': 'Facebook comment scraping job submitted successfully' if success else 'Job submission failed',
                'platform': platform,
                'urls_count': len(post_urls),
                'result': result
            }, status=status.HTTP_201_CREATED if success else status.HTTP_400_BAD_REQUEST)

        elif base_platform == 'instagram':
            # For Instagram comments, use the new Instagram service
            from instagram_data.services import scrape_instagram_comments_from_urls

            # Get project ID from request or default
            project_id = request.data.get('project_id', 1)

            # Use the Instagram comment scraper
            result, success = scrape_instagram_comments_from_urls(
                post_urls=post_urls,
                result_folder_name=result_folder_name,
                project_id=project_id
            )

            return Response({
                'success': success,
                'message': 'Instagram comment scraping job submitted successfully' if success else 'Job submission failed',
                'platform': platform,
                'urls_count': len(post_urls),
                'result': result
            }, status=status.HTTP_201_CREATED if success else status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'error': f'Unsupported platform: {base_platform}'},
                          status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error in scrape_comments: {str(e)}")
        return Response({'error': f'Internal server error: {str(e)}'},
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BrightdataNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing BrightData notifications"""
    queryset = BrightdataNotification.objects.all()
    serializer_class = BrightdataNotificationSerializer
    permission_classes = [AllowAny]  # For testing, use proper permissions in production

    def get_queryset(self):
        """Filter notifications by scraper request or status if specified"""
        queryset = BrightdataNotification.objects.all()

        # Filter by scraper request ID
        scraper_request_id = self.request.query_params.get('scraper_request')
        if scraper_request_id:
            queryset = queryset.filter(scraper_request_id=scraper_request_id)

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by snapshot ID
        snapshot_id = self.request.query_params.get('snapshot_id')
        if snapshot_id:
            queryset = queryset.filter(snapshot_id=snapshot_id)

        return queryset.order_by('-created_at')

    @action(detail=False, methods=['GET'])
    def recent(self, request):
        """Get recent notifications (last 50)"""
        notifications = self.get_queryset()[:50]
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def by_status(self, request):
        """Get notifications grouped by status"""
        from django.db.models import Count

        status_counts = BrightdataNotification.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')

        return Response({
            'status_counts': list(status_counts),
            'total_notifications': BrightdataNotification.objects.count()
        })

@api_view(['GET'])
@permission_classes([AllowAny])
def webhook_metrics(request):
    """
    Get current webhook performance metrics
    """
    try:
        from .webhook_monitor import webhook_monitor

        metrics = webhook_monitor.get_current_metrics()

        return Response({
            'metrics': {
                'total_requests': metrics.total_requests,
                'successful_requests': metrics.successful_requests,
                'failed_requests': metrics.failed_requests,
                'success_rate': round((metrics.successful_requests / metrics.total_requests * 100) if metrics.total_requests > 0 else 0, 2),
                'error_rate': round(metrics.error_rate * 100, 2),
                'avg_response_time': round(metrics.avg_response_time, 3),
                'max_response_time': round(metrics.max_response_time, 3),
                'min_response_time': round(metrics.min_response_time, 3) if metrics.min_response_time != float('inf') else 0,
                'last_success': metrics.last_success.isoformat() if metrics.last_success else None,
                'last_failure': metrics.last_failure.isoformat() if metrics.last_failure else None,
            },
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting webhook metrics: {str(e)}")
        return Response({'error': 'Failed to get metrics'}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def webhook_health(request):
    """
    Get webhook health status and diagnostics
    """
    try:
        from .webhook_monitor import webhook_monitor

        health_data = webhook_monitor.get_health_status()

        return Response({
            'health': health_data,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting webhook health: {str(e)}")
        return Response({'error': 'Failed to get health status'}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def webhook_events(request):
    """
    Get recent webhook events with filtering
    """
    try:
        from .webhook_monitor import webhook_monitor

        limit = min(int(request.GET.get('limit', 50)), 500)  # Max 500 events
        event_type = request.GET.get('event_type')

        events = webhook_monitor.get_recent_events(limit=limit, event_type=event_type)

        return Response({
            'events': events,
            'count': len(events),
            'limit': limit,
            'filters': {
                'event_type': event_type
            },
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting webhook events: {str(e)}")
        return Response({'error': 'Failed to get events'}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def webhook_alerts(request):
    """
    Get webhook alerts with optional severity filtering
    """
    try:
        from .webhook_monitor import webhook_monitor

        severity = request.GET.get('severity')  # 'error', 'warning', etc.

        alerts = webhook_monitor.get_alerts(severity=severity)

        return Response({
            'alerts': alerts,
            'count': len(alerts),
            'filters': {
                'severity': severity
            },
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting webhook alerts: {str(e)}")
        return Response({'error': 'Failed to get alerts'}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def webhook_analytics(request):
    """
    Get detailed webhook performance analytics
    """
    try:
        from .webhook_monitor import webhook_monitor

        hours = min(int(request.GET.get('hours', 24)), 168)  # Max 7 days

        analytics = webhook_monitor.get_performance_analytics(hours=hours)

        return Response({
            'analytics': analytics,
            'time_window_hours': hours,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting webhook analytics: {str(e)}")
        return Response({'error': 'Failed to get analytics'}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def test_webhook_security(request):
    """
    Test webhook security configuration and validation
    """
    try:
        from .webhook_security import webhook_security
        import time

        # Simulate a webhook request for testing
        test_payload = request.data.get('payload', {'test': 'data'})

        # Create a mock request for testing
        class MockRequest:
            def __init__(self, body, headers, meta):
                self.body = json.dumps(test_payload).encode()
                self.headers = headers
                self.META = meta
                self.content_type = 'application/json'

        # Test with provided headers or defaults
        test_headers = request.data.get('headers', {
            'Authorization': f"Bearer {getattr(settings, 'BRIGHTDATA_WEBHOOK_TOKEN', 'test-token')}",
            'X-BrightData-Timestamp': str(int(time.time())),
            'User-Agent': 'BrightData-Test/1.0'
        })

        test_meta = {
            'REMOTE_ADDR': request.data.get('client_ip', '127.0.0.1'),
            'HTTP_X_FORWARDED_FOR': request.data.get('client_ip', '127.0.0.1')
        }

        mock_request = MockRequest(
            body=json.dumps(test_payload),
            headers=test_headers,
            meta=test_meta
        )

        # Run comprehensive validation
        is_valid, validation_result = webhook_security.comprehensive_webhook_validation(mock_request)

        # Additional individual tests
        signature_valid = webhook_security.verify_webhook_signature(mock_request, mock_request.body)
        timestamp_valid = webhook_security.verify_timestamp(mock_request)
        rate_limit_ok = webhook_security.check_rate_limit(mock_request)
        ip_whitelisted = webhook_security.verify_ip_whitelist(mock_request)

        payload_valid, payload_errors = webhook_security.validate_webhook_payload(test_payload)

        return Response({
            'test_results': {
                'overall_valid': is_valid,
                'validation_result': validation_result,
                'individual_tests': {
                    'signature_verification': signature_valid,
                    'timestamp_verification': timestamp_valid,
                    'rate_limiting': rate_limit_ok,
                    'ip_whitelist': ip_whitelisted,
                    'payload_validation': payload_valid,
                    'payload_errors': payload_errors
                }
            },
            'test_configuration': {
                'webhook_token_configured': bool(getattr(settings, 'BRIGHTDATA_WEBHOOK_TOKEN', '')),
                'rate_limit': getattr(settings, 'WEBHOOK_RATE_LIMIT', 100),
                'timestamp_max_age': getattr(settings, 'WEBHOOK_MAX_TIMESTAMP_AGE', 300),
                'ip_whitelist_enabled': bool(getattr(settings, 'WEBHOOK_ALLOWED_IPS', [])),
            },
            'recommendations': _generate_security_recommendations(validation_result),
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error testing webhook security: {str(e)}")
        return Response({'error': f'Security test failed: {str(e)}'}, status=500)

def _generate_security_recommendations(validation_result):
    """Generate security recommendations based on validation results"""
    recommendations = []

    if validation_result['security_score'] < 80:
        recommendations.append("Security score is below 80. Consider implementing additional security measures.")

    if 'Invalid signature' in validation_result.get('errors', []):
        recommendations.append("Configure a strong webhook token using BRIGHTDATA_WEBHOOK_TOKEN environment variable.")

    if 'Rate limit exceeded' in validation_result.get('errors', []):
        recommendations.append("Consider implementing rate limiting or increasing the limit if legitimate traffic is high.")

    if 'IP not whitelisted' in validation_result.get('errors', []):
        recommendations.append("Configure IP whitelisting using WEBHOOK_ALLOWED_IPS for additional security.")

    if validation_result.get('warnings'):
        recommendations.append("Address timestamp validation warnings to prevent replay attacks.")

    if not recommendations:
        recommendations.append("Webhook security configuration looks good!")

    return recommendations
