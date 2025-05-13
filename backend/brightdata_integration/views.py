from django.shortcuts import render
import json
import requests
import datetime
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import BrightdataConfig, ScraperRequest
from .serializers import BrightdataConfigSerializer, ScraperRequestSerializer, ScraperRequestCreateSerializer
import traceback
import logging
from urllib.parse import urlencode

class BrightdataConfigViewSet(viewsets.ModelViewSet):
    """API endpoint for Brightdata configuration"""
    queryset = BrightdataConfig.objects.all()
    serializer_class = BrightdataConfigSerializer
    permission_classes = [AllowAny]  # For testing, use proper permissions in production
    
    @action(detail=True, methods=['POST'])
    def set_active(self, request, pk=None):
        """Set the current configuration as active and deactivate others"""
        config = self.get_object()
        
        # Deactivate all other configurations
        BrightdataConfig.objects.exclude(pk=config.pk).update(is_active=False)
        
        # Activate the current configuration
        config.is_active = True
        config.save()
        
        return Response({'status': 'Configuration activated'})
    
    @action(detail=False, methods=['GET'])
    def active(self, request):
        """Get the active configuration"""
        config = BrightdataConfig.objects.filter(is_active=True).first()
        if not config:
            return Response({'error': 'No active configuration found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(config)
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
                    date_obj = datetime.datetime.strptime(db_start_date, '%Y-%m-%d')
                    # Convert to MM-DD-YYYY for API
                    api_start_date = date_obj.strftime('%m-%d-%Y')
                except ValueError:
                    return Response({'error': 'Invalid start_date format. Use YYYY-MM-DD format.'}, 
                                   status=status.HTTP_400_BAD_REQUEST)
            
            if db_end_date:
                try:
                    # Verify it's in YYYY-MM-DD format
                    date_obj = datetime.datetime.strptime(db_end_date, '%Y-%m-%d')
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
            print("\n\n==== DEBUG: BRIGHTDATA API REQUEST ====")
            print(f"URL: {url}")
            print(f"Headers: {headers}")
            print(f"Params: {params}")
            print(f"Data: {data}")
            print(f"DB dates: start={db_start_date}, end={db_end_date}")
            print(f"API dates: start={api_start_date}, end={api_end_date}")
            
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
                platform='facebook',
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
                    date_obj = datetime.datetime.strptime(db_start_date, '%Y-%m-%d')
                    # Convert to MM-DD-YYYY for API
                    api_start_date = date_obj.strftime('%m-%d-%Y')
                except ValueError:
                    return Response({'error': 'Invalid start_date format. Use YYYY-MM-DD format.'}, 
                                   status=status.HTTP_400_BAD_REQUEST)
            
            if db_end_date:
                try:
                    # Verify it's in YYYY-MM-DD format
                    date_obj = datetime.datetime.strptime(db_end_date, '%Y-%m-%d')
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
            print("\n\n==== DEBUG: BRIGHTDATA API REQUEST (INSTAGRAM) ====")
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
                platform='instagram',
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
                print("\n\n==== DEBUG: BRIGHTDATA API REQUEST (INSTAGRAM) ====")
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
                    date_obj = datetime.datetime.strptime(db_start_date, '%Y-%m-%d')
                    # Convert to MM-DD-YYYY for API
                    api_start_date = date_obj.strftime('%m-%d-%Y')
                except ValueError:
                    return Response({'error': 'Invalid start_date format. Use YYYY-MM-DD format.'}, 
                                   status=status.HTTP_400_BAD_REQUEST)
            
            if db_end_date:
                try:
                    # Verify it's in YYYY-MM-DD format
                    date_obj = datetime.datetime.strptime(db_end_date, '%Y-%m-%d')
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
                    date_obj = datetime.datetime.strptime(db_start_date, '%Y-%m-%d')
                    # Convert to MM-DD-YYYY for API
                    api_start_date = date_obj.strftime('%m-%d-%Y')
                except ValueError:
                    return Response({'error': 'Invalid start_date format. Use YYYY-MM-DD format.'}, 
                                   status=status.HTTP_400_BAD_REQUEST)
            
            if db_end_date:
                try:
                    # Verify it's in YYYY-MM-DD format
                    date_obj = datetime.datetime.strptime(db_end_date, '%Y-%m-%d')
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
def brightdata_webhook(request):
    """Webhook to receive data from Brightdata"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
    try:
        # Parse the webhook payload
        payload = json.loads(request.body)
        request_id = payload.get('request_id')
        
        # Find the corresponding scraper request
        scraper_request = ScraperRequest.objects.filter(request_id=request_id).first()
        if not scraper_request:
            return JsonResponse({'error': 'Unknown request ID'}, status=404)
        
        # Update the scraper request status
        scraper_request.status = 'completed'
        scraper_request.completed_at = timezone.now()
        scraper_request.response_metadata = payload
        scraper_request.save()
        
        # Process the scraped data based on platform
        if scraper_request.platform == 'facebook':
            _process_facebook_data(scraper_request, payload)
        elif scraper_request.platform == 'instagram':
            _process_instagram_data(scraper_request, payload)
        elif scraper_request.platform == 'linkedin':
            _process_linkedin_data(scraper_request, payload)
        elif scraper_request.platform == 'tiktok':
            _process_tiktok_data(scraper_request, payload)
        
        return JsonResponse({'status': 'Data received successfully'})
    
    except Exception as e:
        # Log the error
        print(f"Error processing webhook: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def _process_facebook_data(scraper_request, payload):
    """Process the Facebook data received from Brightdata"""
    from facebook_data.models import FacebookPost, Folder
    
    # Get the results from the payload
    results = payload.get('results', [])
    if not results:
        return
    
    # Get or create a folder if folder_id is provided
    folder = None
    if scraper_request.folder_id:
        try:
            folder = Folder.objects.get(id=scraper_request.folder_id)
        except Folder.DoesNotExist:
            # Folder doesn't exist, create a new one
            folder_name = f"Brightdata Import {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            folder = Folder.objects.create(name=folder_name)
    
    # Process each post in the results
    for post_data in results:
        try:
            # Skip if we don't have a post_id
            post_id = post_data.get('post_id')
            if not post_id:
                continue
            
            # Check if post already exists
            post, created = FacebookPost.objects.get_or_create(
                post_id=post_id,
                folder=folder,
                defaults={
                    # Handle the field mapping from Brightdata to our model
                    'url': post_data.get('url', ''),
                    'user_url': post_data.get('user_url', ''),
                    'user_posted': post_data.get('user_posted', ''),
                    'content': post_data.get('content', ''),
                    'hashtags': post_data.get('hashtags', ''),
                    'date_posted': post_data.get('date_posted', None),
                    'num_comments': post_data.get('num_comments', 0),
                    'num_shares': post_data.get('num_shares', 0),
                    'likes': post_data.get('likes', 0),
                    'page_name': post_data.get('page_name', ''),
                    'profile_id': post_data.get('profile_id', ''),
                    'content_type': scraper_request.content_type,
                    'platform_type': 'facebook',
                    'attachments_data': post_data.get('attachments', {}),
                    'thumbnail': post_data.get('thumbnail', ''),
                    'post_image': post_data.get('post_image', ''),
                    'is_page': post_data.get('is_page', False)
                }
            )
            
            # If post already exists, update relevant fields
            if not created:
                post.content = post_data.get('content', post.content)
                post.num_comments = post_data.get('num_comments', post.num_comments)
                post.num_shares = post_data.get('num_shares', post.num_shares)
                post.likes = post_data.get('likes', post.likes)
                post.save()
                
        except Exception as e:
            # Log individual post processing errors but continue with others
            print(f"Error processing post {post_data.get('post_id')}: {str(e)}")
            continue

def _process_instagram_data(scraper_request, payload):
    """Process the Instagram data received from Brightdata"""
    from instagram_data.models import InstagramPost, Folder
    
    # Get the results from the payload
    results = payload.get('results', [])
    if not results:
        return
    
    # Get or create a folder if folder_id is provided
    folder = None
    if scraper_request.folder_id:
        try:
            folder = Folder.objects.get(id=scraper_request.folder_id)
        except Folder.DoesNotExist:
            # Folder doesn't exist, create a new one
            folder_name = f"Brightdata Import {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            folder = Folder.objects.create(name=folder_name)
    
    # Process each post in the results
    for post_data in results:
        try:
            # Skip if we don't have a post_id
            post_id = post_data.get('post_id')
            if not post_id:
                continue
            
            # Check if post already exists
            post, created = InstagramPost.objects.get_or_create(
                post_id=post_id,
                folder=folder,
                defaults={
                    # Handle the field mapping from Brightdata to our model
                    'url': post_data.get('url', ''),
                    'username': post_data.get('username', ''),
                    'caption': post_data.get('caption', ''),
                    'hashtags': post_data.get('hashtags', ''),
                    'date_posted': post_data.get('date_posted', None),
                    'comments': post_data.get('comments', 0),
                    'likes': post_data.get('likes', 0),
                    'content_type': scraper_request.content_type,
                    'image_url': post_data.get('image_url', ''),
                    'platform_type': 'instagram'
                }
            )
            
            # If post already exists, update relevant fields
            if not created:
                post.caption = post_data.get('caption', post.caption)
                post.comments = post_data.get('comments', post.comments)
                post.likes = post_data.get('likes', post.likes)
                post.save()
                
        except Exception as e:
            # Log individual post processing errors but continue with others
            print(f"Error processing Instagram post {post_data.get('post_id')}: {str(e)}")
            continue

def _process_linkedin_data(scraper_request, payload):
    """Process the LinkedIn data received from Brightdata"""
    from linkedin_data.models import LinkedInPost, Folder
    
    # Get the results from the payload
    results = payload.get('results', [])
    if not results:
        return
    
    # Get or create a folder if folder_id is provided
    folder = None
    if scraper_request.folder_id:
        try:
            folder = Folder.objects.get(id=scraper_request.folder_id)
        except Folder.DoesNotExist:
            # Folder doesn't exist, create a new one
            folder_name = f"Brightdata Import {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            folder = Folder.objects.create(name=folder_name)
    
    # Process each post in the results
    for post_data in results:
        try:
            # Skip if we don't have a post_id
            post_id = post_data.get('post_id')
            if not post_id:
                continue
            
            # Check if post already exists
            post, created = LinkedInPost.objects.get_or_create(
                post_id=post_id,
                folder=folder,
                defaults={
                    # Handle the field mapping from Brightdata to our model
                    'url': post_data.get('url', ''),
                    'author': post_data.get('author', ''),
                    'content': post_data.get('content', ''),
                    'hashtags': post_data.get('hashtags', ''),
                    'date_posted': post_data.get('date_posted', None),
                    'comments': post_data.get('comments', 0),
                    'likes': post_data.get('likes', 0),
                    'company_name': post_data.get('company_name', ''),
                    'platform_type': 'linkedin',
                    'content_type': scraper_request.content_type,
                }
            )
            
            # If post already exists, update relevant fields
            if not created:
                post.content = post_data.get('content', post.content)
                post.comments = post_data.get('comments', post.comments)
                post.likes = post_data.get('likes', post.likes)
                post.save()
                
        except Exception as e:
            # Log individual post processing errors but continue with others
            print(f"Error processing LinkedIn post {post_data.get('post_id')}: {str(e)}")
            continue

def _process_tiktok_data(scraper_request, payload):
    """Process the TikTok data received from Brightdata"""
    from tiktok_data.models import TikTokPost, Folder
    
    # Get the results from the payload
    results = payload.get('results', [])
    if not results:
        return
    
    # Get or create a folder if folder_id is provided
    folder = None
    if scraper_request.folder_id:
        try:
            folder = Folder.objects.get(id=scraper_request.folder_id)
        except Folder.DoesNotExist:
            # Folder doesn't exist, create a new one
            folder_name = f"Brightdata Import {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            folder = Folder.objects.create(name=folder_name)
    
    # Process each post in the results
    for post_data in results:
        try:
            # Skip if we don't have a post_id
            post_id = post_data.get('post_id')
            if not post_id:
                continue
            
            # Check if post already exists
            post, created = TikTokPost.objects.get_or_create(
                post_id=post_id,
                folder=folder,
                defaults={
                    # Handle the field mapping from Brightdata to our model
                    'url': post_data.get('url', ''),
                    'creator': post_data.get('creator', ''),
                    'description': post_data.get('description', ''),
                    'hashtags': post_data.get('hashtags', ''),
                    'date_posted': post_data.get('date_posted', None),
                    'comments': post_data.get('comments', 0),
                    'likes': post_data.get('likes', 0),
                    'shares': post_data.get('shares', 0),
                    'views': post_data.get('views', 0),
                    'platform_type': 'tiktok',
                    'content_type': scraper_request.content_type,
                }
            )
            
            # If post already exists, update relevant fields
            if not created:
                post.description = post_data.get('description', post.description)
                post.comments = post_data.get('comments', post.comments)
                post.likes = post_data.get('likes', post.likes)
                post.shares = post_data.get('shares', post.shares)
                post.views = post_data.get('views', post.views)
                post.save()
                
        except Exception as e:
            # Log individual post processing errors but continue with others
            print(f"Error processing TikTok post {post_data.get('post_id')}: {str(e)}")
            continue
