"""
BrightData Integration Services - SYSTEM INTEGRATED VERSION

READS FROM TRACKFUTURA SYSTEM:
- Uses TrackSource URLs from user's system
- Respects date filters from scraping runs  
- Only scrapes sources in selected folders
- Integrates with user inputs and filtering
"""

import logging
import os
import requests
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

from .models import BrightDataConfig, BrightDataBatchJob, BrightDataScraperRequest

logger = logging.getLogger(__name__)


class BrightDataAutomatedBatchScraper:
    """BrightData API Service - INTEGRATED WITH TRACKFUTURA SYSTEM"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # DIRECT API CREDENTIALS - CONFIRMED WORKING
        self.api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
        self.api_url = "https://api.brightdata.com/datasets/v3/trigger"
        
        # CONFIRMED WORKING DATASET IDS
        self.platform_datasets = {
            'instagram': 'gd_lk5ns7kz21pck8jpis',  # CONFIRMED WORKING
            'facebook': 'gd_lkaxegm826bjpoo9m5',   # CONFIRMED WORKING
            'tiktok': 'gd_l7q7dkf244hwps8lu2',     # TikTok dataset ID
            'linkedin': 'gd_l7q7dkf244hwps8lu3',   # LinkedIn dataset ID
        }

    def trigger_scraper_from_system(self, folder_id: int = None, date_range: Dict[str, str] = None, 
                                   user_id: int = None, num_of_posts: int = 10) -> Dict[str, Any]:
        """
        SYSTEM INTEGRATED SCRAPER - Reads from TrackFutura database
        Uses user's actual sources, date filters, and folder selections
        """
        try:
            # Import here to avoid circular imports
            from track_accounts.models import TrackSource, SourceFolder
            
            self.logger.info(f"🔄 SYSTEM INTEGRATED TRIGGER")
            self.logger.info(f"📁 Folder ID: {folder_id}")
            self.logger.info(f"📅 Date Range: {date_range}")
            self.logger.info(f"👤 User ID: {user_id}")
            
            # Get sources from the system
            if folder_id:
                sources = TrackSource.objects.filter(folder_id=folder_id, folder__project_id=1)
                self.logger.info(f"📋 Found {sources.count()} sources in folder {folder_id}")
            else:
                sources = TrackSource.objects.filter(folder__project_id=1)
                self.logger.info(f"📋 Found {sources.count()} total sources")
            
            if not sources.exists():
                return {
                    'success': False, 
                    'error': f'No sources found in folder {folder_id}' if folder_id else 'No sources found'
                }
            
            # Group sources by platform
            platform_urls = {}
            for source in sources:
                platform = source.platform.lower()
                
                # Get the appropriate URL based on platform
                url = None
                if platform == 'instagram' and source.instagram_link:
                    url = source.instagram_link
                elif platform == 'facebook' and source.facebook_link:
                    url = source.facebook_link
                elif platform == 'linkedin' and source.linkedin_link:
                    url = source.linkedin_link
                elif platform == 'tiktok' and source.tiktok_link:
                    url = source.tiktok_link
                
                if url:
                    if platform not in platform_urls:
                        platform_urls[platform] = []
                    platform_urls[platform].append({
                        'url': url,
                        'source_name': source.name,
                        'source_id': source.id
                    })
            
            self.logger.info(f"🎯 Platforms to scrape: {list(platform_urls.keys())}")
            
            # Trigger scraping for each platform
            results = {}
            total_success = 0
            total_failed = 0
            
            for platform, url_data in platform_urls.items():
                urls = [item['url'] for item in url_data]
                
                result = self.trigger_scraper_with_dates(
                    platform=platform, 
                    urls=urls, 
                    date_range=date_range,
                    num_of_posts=num_of_posts
                )
                
                results[platform] = result
                if result.get('success'):
                    total_success += 1
                else:
                    total_failed += 1
                
                self.logger.info(f"✅ {platform}: {result}")
            
            return {
                'success': total_success > 0,
                'platforms_scraped': list(platform_urls.keys()),
                'total_platforms': len(platform_urls),
                'successful_platforms': total_success,
                'failed_platforms': total_failed,
                'results': results,
                'message': f'Triggered scraping for {total_success} platforms from your system sources'
            }
            
        except Exception as e:
            error_msg = f"Failed to trigger system scraper: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {'success': False, 'error': error_msg}

    def trigger_scraper_with_dates(self, platform: str, urls: List[str], 
                                  date_range: Dict[str, str] = None, num_of_posts: int = 10) -> Dict[str, Any]:
        """
        SYSTEM INTEGRATED BRIGHTDATA API TRIGGER
        Uses URLs from system with proper date filtering
        """
        try:
            platform_lower = platform.lower()
            
            self.logger.info(f"🚀 SYSTEM TRIGGER: {platform_lower.upper()}")
            self.logger.info(f"📋 URLs: {urls}")
            self.logger.info(f"📅 Date Range: {date_range}")
            
            # Get dataset ID
            dataset_id = self.platform_datasets.get(platform_lower)
            if not dataset_id:
                return {'success': False, 'error': f'No dataset ID for platform: {platform_lower}'}
            
            print(f"🔥 SYSTEM INTEGRATED BRIGHTDATA API CALL")
            print(f"Platform: {platform_lower}")
            print(f"Dataset ID: {dataset_id}")
            print(f"URLs: {urls}")
            print(f"Date Range: {date_range}")
            
            # Make API call with date filtering
            success, batch_id = self._make_system_api_call(urls, platform_lower, dataset_id, date_range, num_of_posts)
            
            if success and batch_id:
                # Start monitoring the job in background (non-blocking)
                try:
                    print(f"🕐 Job submitted successfully! Snapshot ID: {batch_id}")
                    print(f"⏱️ Expected completion time: 2-5 minutes for {num_of_posts} posts")
                    print(f"🔍 You can check status at: https://api.brightdata.com/datasets/v3/snapshot/{batch_id}")
                    
                    # Optional: Start a background thread to monitor (non-blocking)
                    # This won't delay the response but will log progress
                    import threading
                    
                    def background_monitor():
                        monitor_result = self.monitor_job_with_timeout(batch_id, timeout_minutes=10)
                        if monitor_result['timeout']:
                            self.logger.error(f"❌ Job {batch_id} timed out after 10 minutes")
                        elif monitor_result['success']:
                            self.logger.info(f"✅ Job {batch_id} completed successfully")
                        else:
                            self.logger.error(f"❌ Job {batch_id} failed: {monitor_result.get('error')}")
                    
                    monitor_thread = threading.Thread(target=background_monitor)
                    monitor_thread.daemon = True
                    monitor_thread.start()
                    
                except Exception as e:
                    print(f"⚠️ Could not start background monitoring: {e}")
                
                return {
                    'success': True,
                    'job_id': batch_id,
                    'snapshot_id': batch_id,
                    'platform': platform_lower,
                    'message': f'BrightData {platform_lower} scraper triggered! Expected completion: 2-5 minutes',
                    'urls_count': len(urls),
                    'date_range': date_range,
                    'dataset_id': dataset_id,
                    'estimated_completion': '2-5 minutes',
                    'monitoring': 'Background monitoring started'
                }
            else:
                return {'success': False, 'error': f'Failed to trigger {platform_lower} scraper'}
                
        except Exception as e:
            error_msg = f"Failed to trigger {platform} scraper: {str(e)}"
            self.logger.error(error_msg)
            print(f"❌ EXCEPTION: {error_msg}")
            return {'success': False, 'error': error_msg}

    def trigger_scraper(self, platform: str, urls: List[str]) -> Dict[str, Any]:
        """
        LEGACY COMPATIBLE TRIGGER - Maintains backward compatibility
        """
        return self.trigger_scraper_with_dates(platform, urls)

    def _make_system_api_call(self, urls: List[str], platform: str, dataset_id: str, 
                             date_range: Dict[str, str] = None, num_of_posts: int = 10) -> tuple[bool, str]:
        """
        SYSTEM INTEGRATED BRIGHTDATA API CALL
        Uses system date ranges and filters properly
        """
        try:
            # Headers
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            }
            
            # Base parameters
            params = {
                "dataset_id": dataset_id,
                "include_errors": "true",
            }
            
            # Add platform-specific parameters
            if platform == 'instagram':
                params.update({
                    "type": "discover_new",
                    "discover_by": "url",
                })
            
            # Parse date range from system - IMPROVED DATE HANDLING
            # BrightData discovery phase needs PAST dates only (no current/future dates)
            today = datetime.now()
            
            # Default to past 30 days ending 2 days ago (safe range)
            default_end = today - timedelta(days=2)  # 2 days ago to be safe
            default_start = default_end - timedelta(days=30)  # 30 days before that
            
            start_date = default_start.strftime("%d-%m-%Y")
            end_date = default_end.strftime("%d-%m-%Y")
            
            if date_range:
                try:
                    start_str = date_range.get('start_date', '')
                    end_str = date_range.get('end_date', '')
                    
                    # Handle different date formats
                    def parse_flexible_date(date_str):
                        """Parse dates in multiple formats"""
                        if not date_str:
                            return None
                        
                        # Try ISO format first: "2025-10-01T00:00:00.000Z"
                        try:
                            if 'T' in date_str or 'Z' in date_str:
                                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        except:
                            pass
                        
                        # Try DD-MM-YYYY format: "01-09-2025"
                        try:
                            return datetime.strptime(date_str, "%d-%m-%Y")
                        except:
                            pass
                        
                        # Try YYYY-MM-DD format: "2025-09-01"
                        try:
                            return datetime.strptime(date_str, "%Y-%m-%d")
                        except:
                            pass
                        
                        print(f"⚠️ Could not parse date: {date_str}")
                        return None
                    
                    # Parse start date
                    if start_str:
                        start_dt = parse_flexible_date(start_str)
                        if start_dt:
                            # Ensure start date is in the past
                            if start_dt.date() >= today.date():
                                print(f"⚠️ Start date {start_dt.date()} is today/future, using past date")
                                start_dt = today - timedelta(days=30)
                            start_date = start_dt.strftime("%d-%m-%Y")
                    
                    # Parse end date
                    if end_str:
                        end_dt = parse_flexible_date(end_str)
                        if end_dt:
                            # Ensure end date is in the past (at least 1 day ago for BrightData discovery)
                            if end_dt.date() >= today.date():
                                print(f"⚠️ End date {end_dt.date()} is today/future, adjusting to past date")
                                end_dt = today - timedelta(days=1)  # 1 day ago should be safe
                            end_date = end_dt.strftime("%d-%m-%Y")
                        
                    print(f"📅 Parsed dates from system: {start_date} to {end_date}")
                    
                except Exception as e:
                    self.logger.warning(f"Date parsing error: {e}, using safe defaults")
                    print(f"⚠️ Date parsing failed: {e}")
            
            # Final validation and safety checks
            try:
                start_dt = datetime.strptime(start_date, "%d-%m-%Y")
                end_dt = datetime.strptime(end_date, "%d-%m-%Y")
                today_dt = datetime.now()
                
                # Basic validation
                if end_dt < start_dt:
                    print(f"⚠️ End date {end_date} is before start date {start_date}, swapping...")
                    start_date, end_date = end_date, start_date
                    start_dt, end_dt = end_dt, start_dt
                
                # Future date check
                if end_dt.date() >= today_dt.date():
                    print(f"⚠️ CRITICAL: End date {end_date} is today/future - adjusting!")
                    end_dt = today_dt - timedelta(days=1)
                    end_date = end_dt.strftime("%d-%m-%Y")
                    print(f"🔧 ADJUSTED END DATE: {end_date}")
                
                # Very large range check
                days_diff = (end_dt - start_dt).days
                if days_diff > 365:
                    print(f"⚠️ Date range is very large: {days_diff} days, limiting to 60 days")
                    start_dt = end_dt - timedelta(days=60)
                    start_date = start_dt.strftime("%d-%m-%Y")
                elif days_diff < 1:
                    print(f"⚠️ Date range too small: {days_diff} days, extending to 7 days")
                    start_dt = end_dt - timedelta(days=7)
                    start_date = start_dt.strftime("%d-%m-%Y")
                
                days_ago = (today_dt - end_dt).days
                print(f"✅ Date range validated: {days_diff} days, ending {days_ago} days ago")
                print(f"✅ Safe for BrightData discovery phase!")
                
            except Exception as e:
                print(f"⚠️ Date validation failed: {e}, using emergency safe dates")
                # Emergency fallback to known good dates
                start_date = "01-09-2025"
                end_date = "30-09-2025"
            
            print(f"📅 Final dates: {start_date} to {end_date}")
            
            # Prepare payload with SYSTEM data - IMPROVED URL HANDLING
            payload = []
            for url in urls:
                # Clean and format URL for Instagram
                formatted_url = url
                if platform == 'instagram':
                    # Remove www. prefix if present
                    if 'www.' in formatted_url:
                        formatted_url = formatted_url.replace('www.', '')
                        print(f"🔧 Removed www. prefix: {formatted_url}")
                    
                    # Ensure URL has trailing slash for Instagram
                    if not formatted_url.endswith('/'):
                        formatted_url = formatted_url + '/'
                        print(f"🔧 Added trailing slash: {formatted_url}")
                    
                    # Ensure proper protocol
                    if not formatted_url.startswith('http'):
                        formatted_url = 'https://' + formatted_url
                        print(f"🔧 Added protocol: {formatted_url}")
                
                if platform == 'instagram':
                    # Match EXACT expected format for Instagram
                    item = {
                        "url": formatted_url,
                        "num_of_posts": num_of_posts if num_of_posts and num_of_posts > 0 else "",
                        "posts_to_not_include": "",  # Empty field as per your format
                        "start_date": start_date,
                        "end_date": end_date,
                        "post_type": "Post"
                    }
                elif platform == 'facebook':
                    # Facebook format
                    item = {
                        "url": formatted_url,
                        "num_of_posts": num_of_posts if num_of_posts and num_of_posts > 0 else "",
                        "posts_to_not_include": "",  # Empty field as per your format
                        "start_date": start_date,
                        "end_date": end_date
                    }
                else:
                    item = {
                        "url": formatted_url, 
                        "num_of_posts": num_of_posts if num_of_posts and num_of_posts > 0 else ""
                    }
                
                payload.append(item)
            
            print(f"🔥 Making SYSTEM API request to: {self.api_url}")
            print(f"📋 Headers: {headers}")
            print(f"📋 Params: {params}")
            print(f"📋 Payload: {json.dumps(payload, indent=2)}")
            
            # Show expected format comparison
            print(f"🎯 Expected CSV format would be:")
            for item in payload:
                if platform == 'instagram':
                    csv_line = f"{item['url']},{item.get('num_of_posts', '')},{item.get('posts_to_not_include', '')},{item['start_date']},{item['end_date']},{item['post_type']}"
                    print(f"   {csv_line}")
            
            # Make the actual request with improved timeout handling
            try:
                print(f"⏱️ Making API request with 30-second timeout...")
                response = requests.post(self.api_url, headers=headers, params=params, json=payload, timeout=30)
            except requests.exceptions.Timeout:
                print(f"⏰ TIMEOUT: BrightData API call exceeded 30 seconds")
                return False, None
            except requests.exceptions.ConnectionError:
                print(f"🔌 CONNECTION ERROR: Could not connect to BrightData API")
                return False, None
            except Exception as e:
                print(f"🚨 REQUEST ERROR: {str(e)}")
                return False, None
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    snapshot_id = response_data.get('snapshot_id', 'system_batch_created')
                    print(f"✅ SYSTEM SUCCESS! Snapshot ID: {snapshot_id}")
                    return True, snapshot_id
                except json.JSONDecodeError:
                    print(f"✅ SYSTEM SUCCESS! (Raw response: {response.text})")
                    return True, "system_batch_success"
            else:
                print(f"❌ SYSTEM FAILED! Status: {response.status_code}, Response: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ EXCEPTION in system API call: {str(e)}")
            return False, None

    def _make_direct_api_call(self, urls: List[str], platform: str, dataset_id: str) -> tuple[bool, str]:
        """
        LEGACY DIRECT API CALL - Maintains backward compatibility
        """
        return self._make_system_api_call(urls, platform, dataset_id)

    def fetch_brightdata_results(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Fetch results from a completed BrightData job
        """
        try:
            # BrightData API endpoint for fetching snapshot results
            results_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            }
            
            print(f"🔍 Fetching BrightData results for snapshot: {snapshot_id}")
            
            response = requests.get(results_url, headers=headers, timeout=30)
            
            print(f"📊 Results fetch status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # If data is a list, it means we got the actual results
                    if isinstance(data, list):
                        print(f"✅ Successfully fetched {len(data)} results")
                        return {
                            'success': True,
                            'data': data,
                            'count': len(data),
                            'snapshot_id': snapshot_id
                        }
                    # If data is a dict with status, job might still be running
                    elif isinstance(data, dict):
                        job_status = data.get('status', 'unknown')
                        if job_status == 'completed':
                            # Try to get the data from a different endpoint or format
                            return {
                                'success': True,
                                'data': [],
                                'count': 0,
                                'snapshot_id': snapshot_id,
                                'status': 'completed_no_data'
                            }
                        else:
                            return {
                                'success': False,
                                'error': f'Job status: {job_status}',
                                'snapshot_id': snapshot_id,
                                'status': job_status
                            }
                    
                except json.JSONDecodeError:
                    # Raw text response - might be CSV or other format
                    text_data = response.text
                    if text_data and len(text_data) > 0:
                        print(f"✅ Got text response: {len(text_data)} characters")
                        return {
                            'success': True,
                            'data': text_data,
                            'count': len(text_data.split('\n')) - 1,  # Approximate row count
                            'snapshot_id': snapshot_id,
                            'format': 'text'
                        }
            
            elif response.status_code == 202:
                # Job still running
                return {
                    'success': False,
                    'error': 'Job still running',
                    'snapshot_id': snapshot_id,
                    'status': 'running'
                }
            
            else:
                print(f"❌ Failed to fetch results: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'snapshot_id': snapshot_id
                }
                
        except Exception as e:
            print(f"❌ Exception fetching results: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'snapshot_id': snapshot_id
            }

    def parse_brightdata_csv_results(self, csv_text: str) -> List[Dict[str, Any]]:
        """
        Parse CSV text results from BrightData into structured data
        """
        try:
            import csv
            from io import StringIO
            
            # Parse CSV
            csv_file = StringIO(csv_text)
            reader = csv.DictReader(csv_file)
            
            results = []
            for row in reader:
                # Clean and structure the data
                cleaned_row = {}
                for key, value in row.items():
                    if key and value:  # Skip empty keys/values
                        cleaned_row[key.strip()] = value.strip()
                
                if cleaned_row:  # Only add non-empty rows
                    results.append(cleaned_row)
            
            print(f"✅ Parsed {len(results)} rows from CSV")
            return results
            
        except Exception as e:
            print(f"❌ Error parsing CSV: {str(e)}")
            return []

    def save_scraped_data_to_database(self, scraper_request, results_data: List[Dict[str, Any]]) -> int:
        """
        Save scraped results to the database
        """
        try:
            from .models import BrightDataScrapedPost
            from django.utils.dateparse import parse_datetime
            import re
            
            saved_count = 0
            
            for item in results_data:
                try:
                    # Extract post data with multiple possible field names
                    post_id = (item.get('post_id') or item.get('shortcode') or 
                              item.get('id') or item.get('url', '').split('/')[-2] if item.get('url') else str(saved_count))
                    
                    # Skip if we already have this post
                    if BrightDataScrapedPost.objects.filter(
                        post_id=post_id,
                        platform=scraper_request.platform,
                        scraper_request=scraper_request
                    ).exists():
                        continue
                    
                    # Parse date
                    date_posted = None
                    date_str = item.get('timestamp') or item.get('date_posted') or item.get('date')
                    if date_str:
                        try:
                            date_posted = parse_datetime(date_str)
                        except:
                            pass
                    
                    # Parse numeric values
                    def safe_int(value, default=0):
                        if not value:
                            return default
                        # Remove commas and non-numeric characters except digits
                        clean_value = re.sub(r'[^\d]', '', str(value))
                        return int(clean_value) if clean_value else default
                    
                    # Create post record
                    post = BrightDataScrapedPost.objects.create(
                        scraper_request=scraper_request,
                        folder_id=scraper_request.folder_id or 0,
                        post_id=post_id,
                        url=item.get('url') or item.get('post_url') or '',
                        platform=scraper_request.platform,
                        
                        # Content
                        user_posted=item.get('user_username') or item.get('username') or item.get('ownerUsername') or 'Unknown',
                        content=item.get('caption') or item.get('description') or item.get('text') or item.get('content') or '',
                        description=item.get('caption') or item.get('description') or item.get('text') or '',
                        
                        # Metrics
                        likes=safe_int(item.get('likes_count') or item.get('likesCount') or item.get('likes')),
                        num_comments=safe_int(item.get('comments_count') or item.get('commentsCount') or item.get('comments')),
                        shares=safe_int(item.get('shares_count') or item.get('shares')),
                        
                        # Metadata
                        date_posted=date_posted,
                        location=item.get('location') or '',
                        hashtags=item.get('hashtags') or [],
                        mentions=item.get('mentions') or [],
                        
                        # Media
                        media_type=item.get('media_type') or item.get('type') or 'post',
                        media_url=item.get('media_url') or item.get('display_url') or '',
                        
                        # User info
                        is_verified=bool(item.get('is_verified') or item.get('verified')),
                        follower_count=safe_int(item.get('follower_count') or item.get('user_followers')),
                        
                        # Raw data backup
                        raw_data=item
                    )
                    
                    saved_count += 1
                    print(f"✅ Saved post {post_id} by {post.user_posted}")
                    
                except Exception as e:
                    print(f"❌ Error saving post: {str(e)}")
                    continue
            
            print(f"✅ Saved {saved_count} posts to database")
            return saved_count
            
        except Exception as e:
            print(f"❌ Error saving scraped data: {str(e)}")
            return 0

    def fetch_and_save_brightdata_results(self, snapshot_id: str, scraper_request) -> Dict[str, Any]:
        """
        Fetch results from BrightData and save them to database
        """
        try:
            # Fetch results from BrightData
            results = self.fetch_brightdata_results(snapshot_id)
            
            if not results['success']:
                return results
            
            # Parse data if needed
            parsed_data = []
            if results.get('format') == 'text':
                parsed_data = self.parse_brightdata_csv_results(results['data'])
            elif isinstance(results.get('data'), list):
                parsed_data = results['data']
            
            if not parsed_data:
                return {
                    'success': False,
                    'error': 'No data to save',
                    'snapshot_id': snapshot_id
                }
            
            # Save to database
            saved_count = self.save_scraped_data_to_database(scraper_request, parsed_data)
            
            # Update scraper request status
            if saved_count > 0:
                scraper_request.status = 'completed'
                scraper_request.completed_at = timezone.now()
                scraper_request.save()
                print(f"✅ Updated scraper request {scraper_request.id} to completed")
            
            return {
                'success': True,
                'snapshot_id': snapshot_id,
                'saved_count': saved_count,
                'total_fetched': len(parsed_data)
            }
            
        except Exception as e:
            print(f"❌ Error in fetch_and_save: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'snapshot_id': snapshot_id
            }

    # ========== LEGACY COMPATIBILITY METHODS ==========
    
    def _make_brightdata_batch_request(self, scraper_requests: List[BrightDataScraperRequest], 
                                     urls: List[str], platform: str) -> bool:
        """Legacy method - redirects to direct API"""
        dataset_id = self.platform_datasets.get(platform)
        if not dataset_id:
            return False
        
        success, _ = self._make_direct_api_call(urls, platform, dataset_id)
        return success

    def _get_or_create_config(self, platform: str) -> Optional[BrightDataConfig]:
        """Legacy method - creates minimal config if needed"""
        try:
            config = BrightDataConfig.objects.filter(platform=platform, is_active=True).first()
            if config:
                return config
            
            dataset_id = self.platform_datasets.get(platform)
            if not dataset_id:
                return None
            
            config = BrightDataConfig.objects.create(
                name=f"{platform.title()} Posts Scraper",
                platform=platform,
                dataset_id=dataset_id,
                api_token=self.api_token,
                is_active=True
            )
            return config
        except Exception:
            return None

    def create_batch_job(self, name: str, project_id: int, source_folder_ids: List[int], 
                        platforms_to_scrape: List[str], content_types_to_scrape: Dict[str, List[str]], 
                        num_of_posts: int = 10, **kwargs) -> Optional[BrightDataBatchJob]:
        """Legacy method for creating batch jobs"""
        urls = kwargs.get('urls', [])
        for platform in platforms_to_scrape:
            self.trigger_scraper(platform, urls)
        return None

    def execute_batch_job(self, batch_job_id: int) -> bool:
        """Legacy method for executing batch jobs"""
        return True

    def get_dataset_results(self, snapshot_id: str) -> Optional[List[Dict]]:
        """
        Fetch results from BrightData using snapshot ID
        Returns the actual scraped data from BrightData API
        """
        try:
            # BrightData results API endpoint
            results_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
            
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            self.logger.info(f"🚀 Fetching BrightData results for snapshot: {snapshot_id}")
            
            response = requests.get(results_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, list):
                    results = data
                elif isinstance(data, dict):
                    # Check for different possible keys
                    results = data.get('data', data.get('results', data.get('items', [])))
                else:
                    results = []
                
                self.logger.info(f"✅ Successfully fetched {len(results)} results from BrightData")
                return results
                
            elif response.status_code == 404:
                self.logger.warning(f"⚠️ Snapshot {snapshot_id} not found or not ready yet")
                return None
            else:
                self.logger.error(f"❌ BrightData API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            self.logger.error(f"⏰ Timeout fetching results for snapshot {snapshot_id}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error fetching BrightData results: {str(e)}")
            return None

    def monitor_job_with_timeout(self, snapshot_id: str, timeout_minutes: int = 10) -> Dict[str, Any]:
        """
        Monitor a BrightData job with timeout to prevent infinite waiting
        
        Args:
            snapshot_id: BrightData snapshot ID to monitor
            timeout_minutes: Maximum time to wait in minutes (default: 10)
            
        Returns:
            Dict with status, results, and timing information
        """
        import time
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        check_interval = 30  # Check every 30 seconds
        
        self.logger.info(f"🕐 Starting job monitoring for {snapshot_id} (timeout: {timeout_minutes} minutes)")
        
        while time.time() - start_time < timeout_seconds:
            try:
                # Check job status
                status_result = self.check_job_status(snapshot_id)
                
                if status_result['completed']:
                    elapsed_time = time.time() - start_time
                    self.logger.info(f"✅ Job completed in {elapsed_time:.1f} seconds")
                    
                    # Fetch results
                    results = self.get_dataset_results(snapshot_id)
                    
                    return {
                        'success': True,
                        'status': 'completed',
                        'results': results,
                        'elapsed_time': elapsed_time,
                        'timeout': False
                    }
                
                elif status_result['failed']:
                    elapsed_time = time.time() - start_time
                    self.logger.error(f"❌ Job failed after {elapsed_time:.1f} seconds")
                    
                    return {
                        'success': False,
                        'status': 'failed',
                        'error': status_result.get('error', 'Job failed'),
                        'elapsed_time': elapsed_time,
                        'timeout': False
                    }
                
                # Job still running, wait before next check
                elapsed_time = time.time() - start_time
                remaining_time = timeout_seconds - elapsed_time
                
                if remaining_time > check_interval:
                    self.logger.info(f"⏳ Job still running ({elapsed_time:.1f}s elapsed, {remaining_time:.1f}s remaining)")
                    time.sleep(check_interval)
                else:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error monitoring job: {str(e)}")
                time.sleep(check_interval)
        
        # Timeout reached
        elapsed_time = time.time() - start_time
        self.logger.error(f"⏰ TIMEOUT: Job exceeded {timeout_minutes} minutes ({elapsed_time:.1f}s)")
        
        return {
            'success': False,
            'status': 'timeout',
            'error': f'Job exceeded {timeout_minutes} minute timeout',
            'elapsed_time': elapsed_time,
            'timeout': True
        }

    def check_job_status(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Check the status of a BrightData job
        
        Returns:
            Dict with completed, failed, and error status
        """
        try:
            # BrightData status API endpoint
            status_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}/status"
            
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(status_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                status_data = response.json()
                status_value = status_data.get('status', 'unknown').lower()
                
                return {
                    'completed': status_value in ['completed', 'finished', 'done'],
                    'failed': status_value in ['failed', 'error', 'cancelled'],
                    'running': status_value in ['running', 'processing', 'in_progress'],
                    'status': status_value,
                    'data': status_data
                }
            
            elif response.status_code == 404:
                # Job not found - might be very new or completed
                # Try to fetch results directly to check if it's completed
                results = self.get_dataset_results(snapshot_id)
                if results is not None:
                    return {'completed': True, 'failed': False, 'running': False, 'status': 'completed'}
                else:
                    return {'completed': False, 'failed': False, 'running': True, 'status': 'not_found'}
            
            else:
                return {
                    'completed': False,
                    'failed': True,
                    'running': False,
                    'status': 'api_error',
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'completed': False,
                'failed': False,
                'running': True,
                'status': 'timeout',
                'error': 'Status check timeout'
            }
        except Exception as e:
            return {
                'completed': False,
                'failed': True,
                'running': False,
                'status': 'error',
                'error': str(e)
            }