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
from .models import BrightdataConfig, ScraperRequest, BatchScraperJob
from .serializers import (
    BrightdataConfigSerializer, ScraperRequestSerializer, ScraperRequestCreateSerializer,
    BatchScraperJobSerializer, BatchScraperJobCreateSerializer
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

                response = requests.post(url, headers=headers, params=params, json=data)

                print("\n==== DEBUG: BRIGHTDATA API RESPONSE (INSTAGRAM) ====")
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
    Enhanced webhook endpoint with enterprise-grade security and monitoring
    """
    from .webhook_security import webhook_security
    from .webhook_monitor import webhook_monitor
    import time

    start_time = time.time()
    client_ip = webhook_security.get_client_ip(request)
    user_agent = request.headers.get('User-Agent', '')

    try:
        # Comprehensive security validation
        is_valid, validation_result = webhook_security.comprehensive_webhook_validation(request)

        if not is_valid:
            error_message = f"Security validation failed: {', '.join(validation_result['errors'])}"
            logger.warning(f"Webhook security validation failed from {client_ip}: {error_message}")

            # Record security event
            webhook_monitor.record_webhook_event(
                event_type='webhook_data',
                status='security_error',
                response_time=time.time() - start_time,
                payload_size=len(request.body) if request.body else 0,
                client_ip=client_ip,
                user_agent=user_agent,
                error_message=error_message,
                metadata={'validation_result': validation_result}
            )

            return JsonResponse({
                'error': 'Security validation failed',
                'details': validation_result['errors'],
                'security_score': validation_result['security_score']
            }, status=401)

        # Parse the incoming data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            error_message = f"Unsupported content type: {request.content_type}"
            logger.error(error_message)

            webhook_monitor.record_webhook_event(
                event_type='webhook_data',
                status='error',
                response_time=time.time() - start_time,
                payload_size=len(request.body) if request.body else 0,
                client_ip=client_ip,
                user_agent=user_agent,
                error_message=error_message
            )

            return JsonResponse({'error': 'Unsupported content type'}, status=400)

        # Extract metadata from headers or data
        snapshot_id = request.headers.get('X-Snapshot-Id') or data.get('snapshot_id')
        platform = request.headers.get('X-Platform') or data.get('platform', 'unknown')

        logger.info(f"Received webhook data for snapshot_id: {snapshot_id}, platform: {platform}")

        # Find the corresponding scraper request
        scraper_request = None
        if snapshot_id:
            try:
                scraper_request = ScraperRequest.objects.get(request_id=snapshot_id)
            except ScraperRequest.DoesNotExist:
                logger.warning(f"No scraper request found for snapshot_id: {snapshot_id}")

        # Process the data based on platform
        success = _process_webhook_data(data, platform, scraper_request)

        if success:
            # Update scraper request status
            if scraper_request:
                scraper_request.status = 'completed'
                scraper_request.save()

            # Record successful event
            webhook_monitor.record_webhook_event(
                event_type='webhook_data',
                status='success',
                response_time=time.time() - start_time,
                payload_size=len(request.body) if request.body else 0,
                client_ip=client_ip,
                user_agent=user_agent,
                metadata={
                    'snapshot_id': snapshot_id,
                    'platform': platform,
                    'data_items': len(data) if isinstance(data, list) else 1,
                    'validation_warnings': validation_result.get('warnings', [])
                }
            )

            logger.info(f"Webhook processed successfully: {snapshot_id}")
            return JsonResponse({
                'status': 'success',
                'message': 'Data processed successfully',
                'snapshot_id': snapshot_id,
                'processing_time': round(time.time() - start_time, 3),
                'security_score': validation_result['security_score']
            })
        else:
            # Update scraper request status to failed
            if scraper_request:
                scraper_request.status = 'failed'
                scraper_request.error_message = 'Failed to process webhook data'
                scraper_request.save()

            error_message = 'Failed to process webhook data'
            webhook_monitor.record_webhook_event(
                event_type='webhook_data',
                status='processing_error',
                response_time=time.time() - start_time,
                payload_size=len(request.body) if request.body else 0,
                client_ip=client_ip,
                user_agent=user_agent,
                error_message=error_message,
                metadata={'snapshot_id': snapshot_id, 'platform': platform}
            )

            return JsonResponse({
                'status': 'error',
                'message': error_message,
                'processing_time': round(time.time() - start_time, 3)
            }, status=500)

    except json.JSONDecodeError as e:
        error_message = f"Invalid JSON in webhook request: {str(e)}"
        logger.error(error_message)

        webhook_monitor.record_webhook_event(
            event_type='webhook_data',
            status='json_error',
            response_time=time.time() - start_time,
            payload_size=len(request.body) if request.body else 0,
            client_ip=client_ip,
            user_agent=user_agent,
            error_message=error_message
        )

        return JsonResponse({'error': 'Invalid JSON', 'details': str(e)}, status=400)
    except Exception as e:
        error_message = f"Error processing webhook: {str(e)}"
        logger.error(error_message)

        webhook_monitor.record_webhook_event(
            event_type='webhook_data',
            status='error',
            response_time=time.time() - start_time,
            payload_size=len(request.body) if request.body else 0,
            client_ip=client_ip,
            user_agent=user_agent,
            error_message=error_message
        )

        return JsonResponse({'error': 'Internal server error', 'details': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def brightdata_notify(request):
    """
    Notification endpoint to receive status updates from BrightData
    """
    try:
        # Verify authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not _verify_webhook_auth(auth_header):
            logger.warning(f"Unauthorized notify request from {request.META.get('REMOTE_ADDR')}")
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        # Parse notification data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            # Handle form-encoded data
            data = dict(request.POST.items())

        snapshot_id = data.get('snapshot_id')
        status_update = data.get('status')
        message = data.get('message', '')

        logger.info(f"Received notification: snapshot_id={snapshot_id}, status={status_update}, message={message}")

        # Find and update the corresponding scraper request
        if snapshot_id:
            try:
                scraper_request = ScraperRequest.objects.get(request_id=snapshot_id)

                # Update status based on notification
                if status_update in ['completed', 'finished']:
                    scraper_request.status = 'completed'
                elif status_update in ['failed', 'error']:
                    scraper_request.status = 'failed'
                    scraper_request.error_message = message
                elif status_update in ['running', 'processing']:
                    scraper_request.status = 'processing'

                # Store notification metadata
                if not scraper_request.response_metadata:
                    scraper_request.response_metadata = {}

                scraper_request.response_metadata['notifications'] = scraper_request.response_metadata.get('notifications', [])
                scraper_request.response_metadata['notifications'].append({
                    'timestamp': request.headers.get('Date') or 'unknown',
                    'status': status_update,
                    'message': message,
                    'data': data
                })

                scraper_request.save()

                logger.info(f"Updated scraper request {scraper_request.id} status to {scraper_request.status}")

            except ScraperRequest.DoesNotExist:
                logger.warning(f"No scraper request found for snapshot_id: {snapshot_id}")

        return JsonResponse({
            'status': 'success',
            'message': 'Notification processed successfully'
        })

    except json.JSONDecodeError:
        logger.error("Invalid JSON in notification request")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing notification: {str(e)}")
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

def _process_webhook_data(data, platform: str, scraper_request=None):
    """
    Process incoming webhook data and store it in the appropriate platform model
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

        folder_id = scraper_request.folder_id if scraper_request else None
        created_count = 0

        for post_data in posts_data:
            try:
                # Map common fields (you'll need to adjust based on your model fields)
                post_fields = _map_post_fields(post_data, platform)

                # Handle folder assignment for Facebook posts
                if folder_id and platform.lower() == 'facebook':
                    from facebook_data.models import Folder
                    try:
                        folder = Folder.objects.get(id=folder_id)
                        post_fields['folder'] = folder
                    except Folder.DoesNotExist:
                        logger.warning(f"Folder with ID {folder_id} not found, creating default folder")
                        folder = Folder.objects.create(name=f"Auto-created folder {folder_id}")
                        post_fields['folder'] = folder

                # Create or update post
                post_id = post_data.get('post_id') or post_data.get('id')
                if post_id and platform.lower() == 'facebook':
                    # For Facebook, check uniqueness by post_id and folder
                    folder = post_fields.get('folder')
                    if folder:
                        post, created = PostModel.objects.get_or_create(
                            post_id=post_id,
                            folder=folder,
                            defaults=post_fields
                        )
                    else:
                        post, created = PostModel.objects.get_or_create(
                            post_id=post_id,
                            defaults=post_fields
                        )
                    if created:
                        created_count += 1
                elif post_id:
                    # For other platforms
                    post, created = PostModel.objects.get_or_create(
                        post_id=post_id,
                        defaults=post_fields
                    )
                    if created:
                        created_count += 1
                else:
                    # Create new post without checking for duplicates
                    PostModel.objects.create(**post_fields)
                    created_count += 1

            except Exception as e:
                logger.error(f"Error processing individual post: {str(e)}")
                continue

        logger.info(f"Successfully processed {created_count} posts for platform {platform}")
        return True

    except Exception as e:
        logger.error(f"Error processing webhook data: {str(e)}")
        return False

def _map_post_fields(post_data: dict, platform: str) -> dict:
    """
    Map BrightData post fields to our model fields based on actual BrightData JSON structure
    """

    if platform.lower() == 'facebook':
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

    @action(detail=False, methods=['POST'])
    def create_and_execute(self, request):
        """Create and execute a batch scraper job"""
        try:
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
                output_folder_pattern=request.data.get('output_folder_pattern')
            )

            return Response({
                'job_id': job.id,
                'success': success,
                'message': f'Batch job {"completed successfully" if success else "failed"}'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
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
