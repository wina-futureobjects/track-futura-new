from django.shortcuts import render, get_object_or_404
import csv
import json
import io
import datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from .models import FacebookPost, Folder
from .serializers import FacebookPostSerializer, FolderSerializer
from django.db.models import Q

# Try to import dateparser, but provide a fallback if it's not available
try:
    import dateparser
    HAS_DATEPARSER = True
except ImportError:
    HAS_DATEPARSER = False
    print("Warning: dateparser module not available. Using basic date parsing.")

# Create your views here.

class FolderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Facebook data folders
    """
    serializer_class = FolderSerializer
    permission_classes = [AllowAny]  # For testing, use proper permissions in production
    
    def get_queryset(self):
        """
        Filter folders by project if project parameter is provided
        """
        queryset = Folder.objects.all()
        
        # Filter by project if specified
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Override create method to ensure project ID is saved
        """
        # Explicitly get project ID from request data
        project_id = request.data.get('project')
        
        # Validate and save using serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save with project ID explicitly set
        folder = serializer.save()
        
        # Double check the project ID is set correctly
        if project_id and not folder.project_id:
            folder.project_id = project_id
            folder.save()
            
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """
        Override update method to ensure project ID is preserved
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Get project ID from request or use existing
        project_id = request.data.get('project', instance.project_id)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Save with project ID explicitly set
        updated_instance = serializer.save()
        
        # Double check the project ID is preserved
        if project_id and updated_instance.project_id != project_id:
            updated_instance.project_id = project_id
            updated_instance.save()
        
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        
        return Response(serializer.data)

class FacebookPostViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Facebook Posts
    """
    serializer_class = FacebookPostSerializer
    permission_classes = [AllowAny]  # Allow any user to access these endpoints for testing
    
    def get_queryset(self):
        """
        Filter posts by folder if folder_id is provided
        """
        # Always use a try-except block for database queries
        try:
            queryset = FacebookPost.objects.all()
            
            # Filter by folder if specified
            folder_id = self.request.query_params.get('folder_id')
            if folder_id:
                queryset = queryset.filter(folder_id=folder_id)
            
            # Check if content_type field exists before filtering
            content_type = self.request.query_params.get('content_type')
            if content_type and 'content_type' in [f.name for f in FacebookPost._meta.get_fields()]:
                queryset = queryset.filter(content_type=content_type)
            
            # Add search functionality
            search_query = self.request.query_params.get('search', '')
            if search_query:
                # Build a dynamic Q object with fields that exist in the model
                search_filter = Q()
                available_fields = [f.name for f in FacebookPost._meta.get_fields()]
                
                # Check each field individually to avoid errors with missing fields
                if 'user_posted' in available_fields:
                    search_filter |= Q(user_posted__icontains=search_query)
                
                if 'description' in available_fields:
                    search_filter |= Q(description__icontains=search_query)
                
                if 'content' in available_fields:
                    search_filter |= Q(content__icontains=search_query)
                
                if 'hashtags' in available_fields:
                    search_filter |= Q(hashtags__icontains=search_query)
                
                if 'content_type' in available_fields:
                    search_filter |= Q(content_type__icontains=search_query)
                
                if 'post_id' in available_fields:
                    search_filter |= Q(post_id__icontains=search_query)
                
                if 'page_name' in available_fields:
                    search_filter |= Q(page_name__icontains=search_query)
                
                # Apply the search filter if we have any valid conditions
                if search_filter:
                    queryset = queryset.filter(search_filter)
            
            return queryset
        except Exception as e:
            # Log the error and return empty queryset
            print(f"Error in get_queryset: {str(e)}")
            return FacebookPost.objects.none()

    def _safe_int_convert(self, value):
        """
        Safely convert a value to integer, returning 0 if conversion fails
        """
        try:
            if value is None or value == '' or value == '""':
                return 0
            return int(value)
        except (ValueError, TypeError):
            return 0
    
    def _safe_float_convert(self, value):
        """
        Safely convert a value to float, returning 0.0 if conversion fails
        """
        try:
            if value is None or value == '' or value == '""':
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
            
    def _safe_bool_convert(self, value):
        """
        Safely convert a value to boolean
        """
        if value is None or value == '' or value == '""':
            return False
        
        if isinstance(value, bool):
            return value
        
        # Convert string values
        if isinstance(value, str):
            value = value.strip().lower()
            return value in ('true', 'yes', '1', 't', 'y')
        
        # Try to convert numbers to bool
        try:
            return bool(int(value))
        except (ValueError, TypeError):
            return False
    
    def _parse_date(self, date_str):
        """
        Parse a date string using dateparser if available, otherwise use basic parsing
        """
        if not date_str or not date_str.strip() or date_str.strip() == '""':
            return None
        
        # Remove any quotes that might be in the CSV data
        clean_date = date_str.strip().strip('"\'')
        if not clean_date:
            return None
        
        # Special handling for ISO format dates (like 2025-04-18T02:01:22.000Z)
        if 'T' in clean_date and (clean_date.endswith('Z') or '+' in clean_date):
            try:
                # Use Python's built-in ISO parser for efficiency
                from datetime import datetime
                return datetime.fromisoformat(clean_date.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                # If that fails, continue with the regular parsing methods
                print(f"ISO format detection failed for: {clean_date}")
                pass
        
        # Detect and fix common Facebook date formats
        # If it's a Unix timestamp (all digits)
        if clean_date.isdigit() and len(clean_date) >= 10:
            try:
                # Convert Unix timestamp to datetime
                timestamp = int(clean_date)
                # Check if it's in milliseconds (13 digits) or seconds (10 digits)
                if len(clean_date) >= 13:
                    timestamp = timestamp // 1000  # Convert from milliseconds to seconds
                return datetime.datetime.fromtimestamp(timestamp)
            except (ValueError, OverflowError):
                pass  # If conversion fails, continue with other methods
        
        try:
            if HAS_DATEPARSER:
                # Use dateparser if available with specific settings for Facebook
                return dateparser.parse(
                    clean_date,
                    settings={
                        'TIMEZONE': 'UTC',
                        'RETURN_AS_TIMEZONE_AWARE': False,
                        'DATE_ORDER': 'YMD',  # Prefer Year-Month-Day format
                    }
                )
            else:
                # Basic parsing for common formats
                formats_to_try = [
                    '%Y-%m-%dT%H:%M:%S.%fZ', # 2025-04-18T02:01:22.000Z
                    '%Y-%m-%dT%H:%M:%SZ',    # 2025-04-18T02:01:22Z
                    '%Y-%m-%dT%H:%M:%S.%f',  # 2025-04-18T02:01:22.000
                    '%Y-%m-%dT%H:%M:%S',     # 2025-04-18T02:01:22
                    '%Y-%m-%d',              # 2023-01-31
                    '%Y-%m-%d %H:%M:%S',     # 2023-01-31 12:30:45
                    '%Y-%m-%d %H:%M',        # 2023-01-31 12:30
                    '%d/%m/%Y',              # 31/01/2023
                    '%m/%d/%Y',              # 01/31/2023
                    '%Y/%m/%d',              # 2023/01/31
                    '%d-%m-%Y',              # 31-01-2023
                    '%m-%d-%Y',              # 01-31-2023
                    '%d.%m.%Y',              # 31.01.2023
                    '%m.%d.%Y',              # 01.31.2023
                    '%b %d, %Y',             # Jan 31, 2023
                    '%d %b %Y',              # 31 Jan 2023
                    '%B %d, %Y',             # January 31, 2023
                    '%d %B %Y',              # 31 January 2023
                ]
                
                for fmt in formats_to_try:
                    try:
                        return datetime.datetime.strptime(clean_date, fmt)
                    except ValueError:
                        continue
                    
                # If we get here, no format worked
                return None
        except Exception as e:
            print(f"Error parsing date '{clean_date}': {e}")
            return None
    
    @action(detail=False, methods=['POST'])
    def upload_csv(self, request):
        """
        Upload CSV file and parse the data
        """
        try:
            csv_file = request.FILES.get('file')
            if not csv_file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            folder_id = request.data.get('folder_id')
            folder = None
            if folder_id:
                try:
                    folder = Folder.objects.get(id=folder_id)
                except Folder.DoesNotExist:
                    return Response(
                        {'error': f'Folder with id {folder_id} does not exist'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            content_type = request.data.get('content_type', 'post')
            if content_type not in ['post', 'reel']:
                return Response(
                    {'error': 'Invalid content_type. Must be either "post" or "reel"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Decode and parse CSV
            decoded_file = csv_file.read().decode('utf-8-sig')  # Handle BOM
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            
            rows_processed = 0
            rows_added = 0
            rows_updated = 0
            rows_skipped = 0
            errors = []
            
            for row in csv_data:
                # Skip empty rows
                if not row or all(not v for v in row.values()):
                    continue
                
                rows_processed += 1
                
                # Extract and validate required fields
                url = row.get('url', '').strip('"')
                post_id = row.get('post_id', '').strip('"')
                
                if not url:
                    errors.append(f"Row {rows_processed}: Missing URL")
                    rows_skipped += 1
                    continue
                
                if not post_id:
                    # Generate a pseudo-ID from URL if missing
                    from hashlib import md5
                    post_id = md5(url.encode()).hexdigest()[:16]
                
                try:
                    # Parse date fields - handle empty strings 
                    date_posted_raw = row.get('date_posted', None)
                    parsed_date = self._parse_date(date_posted_raw)
                    
                    # If date parsing failed but timestamp is available, try to use that
                    if parsed_date is None and row.get('timestamp'):
                        parsed_date = self._parse_date(row.get('timestamp'))
                    
                    # Process hashtags
                    hashtags_raw = row.get('hashtags', '')
                    hashtags_value = hashtags_raw
                    
                    # If hashtags is in JSON format (array string), keep it as is
                    # Otherwise, assume it's comma-separated
                    if not (hashtags_raw.startswith('[') and hashtags_raw.endswith(']')):
                        if hashtags_raw and ',' in hashtags_raw:
                            hashtags_list = [tag.strip() for tag in hashtags_raw.split(',')]
                            hashtags_value = ','.join(hashtags_list)

                    # user_posted is optional and can be determined from various alternative fields
                    # We try to find it from these fields in the following order: user_posted -> page_name -> user_username_raw
                    user_posted = row.get('user_posted', '')
                    if not user_posted:
                        user_posted = row.get('page_name', '')
                    if not user_posted:
                        user_posted = row.get('user_username_raw', '')
                    
                    # Determine description/content from various possible fields
                    description = row.get('description', '')
                    if not description:
                        description = row.get('content', '')
                    
                    # Parse JSON fields if they exist
                    num_likes_type = None
                    if row.get('num_likes_type'):
                        try:
                            # Try parsing as JSON, but if that fails, store as text
                            num_likes_type = json.loads(row.get('num_likes_type'))
                        except json.JSONDecodeError:
                            # Just store as text
                            num_likes_type = row.get('num_likes_type')
                    
                    count_reactions_type = None
                    if row.get('count_reactions_type'):
                        try:
                            count_reactions_type = json.loads(row.get('count_reactions_type'))
                        except json.JSONDecodeError:
                            # Store as text if not valid JSON
                            count_reactions_type = row.get('count_reactions_type')
                    
                    attachments_data = None
                    if row.get('attachments'):
                        try:
                            attachments_data = json.loads(row.get('attachments'))
                        except json.JSONDecodeError:
                            # Store as text if not valid JSON
                            attachments_data = row.get('attachments')
                    
                    original_post = None
                    if row.get('original_post'):
                        try:
                            original_post = json.loads(row.get('original_post'))
                        except json.JSONDecodeError:
                            # Store as text if not valid JSON
                            original_post = row.get('original_post')
                    
                    active_ads_urls = None
                    if row.get('active_ads_urls'):
                        try:
                            active_ads_urls = json.loads(row.get('active_ads_urls'))
                        except json.JSONDecodeError:
                            # Store as text if not valid JSON
                            active_ads_urls = row.get('active_ads_urls')
                    
                    input_data = None
                    if row.get('input'):
                        try:
                            input_data = json.loads(row.get('input'))
                        except json.JSONDecodeError:
                            # Store as text if not valid JSON
                            input_data = row.get('input')
                    
                    # Prepare the default data dictionary with all possible fields from the CSV
                    default_data = {
                        # Basic fields
                        'url': url,
                        'post_id': post_id,
                        'user_url': row.get('user_url', ''),
                        'user_posted': user_posted,
                        'user_username_raw': row.get('user_username_raw', ''),
                        
                        # Content fields
                        'content': row.get('content', ''),
                        'description': description,
                        'hashtags': hashtags_value,
                        'date_posted': parsed_date,
                        
                        # Engagement metrics
                        'num_comments': self._safe_int_convert(row.get('num_comments')),
                        'num_shares': self._safe_int_convert(row.get('num_shares')),
                        'likes': self._safe_int_convert(row.get('likes')),
                        'video_view_count': self._safe_int_convert(row.get('video_view_count')),
                        'num_likes_type': num_likes_type,
                        'count_reactions_type': count_reactions_type,
                        
                        # Page/Profile information
                        'page_name': row.get('page_name', ''),
                        'profile_id': row.get('profile_id', ''),
                        'page_intro': row.get('page_intro', ''),
                        'page_category': row.get('page_category', ''),
                        'page_logo': row.get('page_logo', ''),
                        'page_external_website': row.get('page_external_website', ''),
                        'page_likes': self._safe_int_convert(row.get('page_likes')),
                        'page_followers': self._safe_int_convert(row.get('page_followers')),
                        'page_is_verified': self._safe_bool_convert(row.get('page_is_verified')),
                        'followers': self._safe_int_convert(row.get('followers')),
                        'page_phone': row.get('page_phone', ''),
                        'page_email': row.get('page_email', ''),
                        'page_creation_time': self._parse_date(row.get('page_creation_time')),
                        'page_reviews_score': row.get('page_reviews_score', ''),
                        'page_reviewers_amount': self._safe_int_convert(row.get('page_reviewers_amount')),
                        'page_price_range': row.get('page_price_range', ''),
                        
                        # Media content
                        'photos': row.get('photos', ''),
                        'videos': row.get('videos', ''),
                        'attachments_data': attachments_data,
                        'thumbnail': row.get('thumbnail', ''),
                        'external_link': row.get('external_link', ''),
                        'post_image': row.get('post_image', ''),
                        
                        # External content
                        'post_external_link': row.get('post_external_link', ''),
                        'post_external_title': row.get('post_external_title', ''),
                        'post_external_image': row.get('post_external_image', ''),
                        'link_description_text': row.get('link_description_text', ''),
                        
                        # Profile images and URLs
                        'page_url': row.get('page_url', ''),
                        'header_image': row.get('header_image', ''),
                        'avatar_image_url': row.get('avatar_image_url', ''),
                        'profile_handle': row.get('profile_handle', ''),
                        'profile_image_link': row.get('profile_image_link', ''),
                        
                        # Reel specific fields
                        'shortcode': row.get('shortcode', ''),
                        'length': self._safe_float_convert(row.get('length')),
                        'audio': row.get('audio', ''),
                        
                        # Metadata and flags
                        'is_verified': self._safe_bool_convert(row.get('is_verified')),
                        'has_handshake': self._safe_bool_convert(row.get('has_handshake')),
                        'is_sponsored': self._safe_bool_convert(row.get('is_sponsored')),
                        'sponsor_name': row.get('sponsor_name', ''),
                        'is_paid_partnership': self._safe_bool_convert(row.get('is_paid_partnership')),
                        'is_page': self._safe_bool_convert(row.get('is_page')),
                        'include_profile_data': self._safe_bool_convert(row.get('include_profile_data')),
                        
                        # Additional metadata
                        'location': row.get('location', ''),
                        'latest_comments': row.get('latest_comments', ''),
                        'about': row.get('about', ''),
                        'active_ads_urls': active_ads_urls,
                        'delegate_page_id': row.get('delegate_page_id', ''),
                        'original_post': original_post,
                        'other_posts_url': row.get('other_posts_url', ''),
                        
                        # Content type information
                        'content_type': content_type,  # Set from the request parameter
                        'platform_type': 'FB Post' if content_type == 'post' else 'FB Reel',
                        'post_type': row.get('post_type', ''),
                        
                        # Fetch parameters
                        'days_range': self._safe_int_convert(row.get('days_range')),
                        'num_of_posts': self._safe_int_convert(row.get('num_of_posts')),
                        'posts_count': self._safe_int_convert(row.get('posts_count')),
                        'posts_to_not_include': row.get('posts_to_not_include', ''),
                        'until_date': self._parse_date(row.get('until_date')),
                        'from_date': self._parse_date(row.get('from_date')),
                        'start_date': self._parse_date(row.get('start_date')),
                        'end_date': self._parse_date(row.get('end_date')),
                        'following': self._safe_int_convert(row.get('following')),
                        
                        # API response fields
                        'timestamp': self._parse_date(row.get('timestamp')),
                        'input': input_data,
                        'error': row.get('error', ''),
                        'error_code': row.get('error_code', ''),
                        'warning': row.get('warning', ''),
                        'warning_code': row.get('warning_code', ''),
                        
                        # Other fields
                        'tagged_users': row.get('tagged_users', ''),
                        'engagement_score': self._safe_float_convert(row.get('engagement_score_view', 0)),
                        'discovery_input': row.get('discovery_input', ''),
                    }
                    
                    # Set folder relationship if provided
                    if folder:
                        default_data['folder'] = folder
                    
                    # Try to find existing record with the same post_id and folder
                    existing_post = FacebookPost.objects.filter(
                        post_id=post_id,
                        folder=folder
                    ).first()
                    
                    if existing_post:
                        # Update the existing record
                        for key, value in default_data.items():
                            setattr(existing_post, key, value)
                        existing_post.save()
                        rows_updated += 1
                    else:
                        # Create a new record
                        FacebookPost.objects.create(**default_data)
                        rows_added += 1
                        
                except Exception as e:
                    errors.append(f"Error processing row {rows_processed}: {str(e)}")
                    rows_skipped += 1
            
            # Prepare response
            response_data = {
                'status': 'success',
                'message': f'CSV processed successfully. {rows_processed} rows processed, {rows_added} added, {rows_updated} updated, {rows_skipped} skipped.',
                'rows_processed': rows_processed,
                'rows_added': rows_added,
                'rows_updated': rows_updated,
                'rows_skipped': rows_skipped,
            }
            
            if errors:
                response_data['errors'] = errors[:10]  # Limit number of errors returned
                response_data['total_errors'] = len(errors)
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error processing CSV file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['GET'])
    def stats(self, request):
        """
        Get statistics for posts in a folder
        """
        try:
            folder_id = request.query_params.get('folder_id')
            if not folder_id:
                return Response(
                    {'error': 'folder_id parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                folder = Folder.objects.get(id=folder_id)
            except Folder.DoesNotExist:
                return Response(
                    {'error': f'Folder with id {folder_id} does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get all posts in the folder
            posts = FacebookPost.objects.filter(folder=folder)
            
            # Count total posts
            total_posts = posts.count()
            
            # Count unique posters - check if user_posted field exists
            available_fields = [f.name for f in FacebookPost._meta.get_fields()]
            
            unique_users = 0
            if 'user_posted' in available_fields:
                unique_users = posts.values('user_posted').distinct().count()
            elif 'page_name' in available_fields:
                unique_users = posts.values('page_name').distinct().count()
            
            # Calculate average likes - check if likes field exists
            avg_likes = 0
            if 'likes' in available_fields:
                try:
                    avg_likes = posts.values_list('likes', flat=True).aggregate(
                        avg_likes=models.Avg('likes')
                    )['avg_likes'] or 0
                except Exception as e:
                    print(f"Error calculating average likes: {str(e)}")
            
            # Count verified accounts - check if is_verified field exists
            verified_accounts = 0
            if 'is_verified' in available_fields:
                try:
                    if 'user_posted' in available_fields:
                        verified_accounts = posts.filter(is_verified=True).values('user_posted').distinct().count()
                    elif 'page_name' in available_fields:
                        verified_accounts = posts.filter(is_verified=True).values('page_name').distinct().count()
                except Exception as e:
                    print(f"Error counting verified accounts: {str(e)}")
            
            stats = {
                'totalPosts': total_posts,
                'uniqueUsers': unique_users,
                'avgLikes': round(avg_likes, 2) if isinstance(avg_likes, (int, float)) else 0,
                'verifiedAccounts': verified_accounts,
            }
            
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            # Log the error and return a friendly message
            print(f"Error in stats view: {str(e)}")
            return Response(
                {'error': 'An error occurred while retrieving statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['GET'])
    def download_csv(self, request):
        """
        Download posts as CSV
        """
        try:
            # Get query parameters
            folder_id = request.query_params.get('folder_id')
            content_type = request.query_params.get('content_type')
            
            # Build query
            query = {}
            if folder_id:
                query['folder_id'] = folder_id
            if content_type:
                query['content_type'] = content_type
            
            # Get posts
            posts = FacebookPost.objects.filter(**query).order_by('-date_posted')
            
            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="facebook_data_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            
            # Create CSV writer and write header
            writer = csv.writer(response)
            
            # Use different headers based on content type
            if content_type == 'reel':
                writer.writerow([
                    'url', 'post_id', 'user_url', 'user_username_raw', 'content', 'date_posted', 'hashtags',
                    'num_comments', 'num_shares', 'video_view_count', 'likes', 'page_name', 'profile_id',
                    'page_intro', 'page_category', 'page_logo', 'page_external_website', 'page_likes',
                    'page_followers', 'page_is_verified', 'thumbnail', 'external_link', 'page_url',
                    'header_image', 'avatar_image_url', 'profile_handle', 'shortcode', 'length', 'audio',
                    'num_of_posts', 'posts_to_not_include', 'until_date', 'from_date', 'start_date',
                    'end_date', 'timestamp', 'input', 'error', 'error_code', 'warning', 'warning_code'
                ])
            else:  # Post
                writer.writerow([
                    'url', 'post_id', 'user_url', 'user_username_raw', 'content', 'date_posted', 'hashtags',
                    'num_comments', 'num_shares', 'num_likes_type', 'page_name', 'profile_id',
                    'page_intro', 'page_category', 'page_logo', 'page_external_website', 'page_likes',
                    'page_followers', 'page_is_verified', 'original_post', 'attachments_data', 'other_posts_url',
                    'post_external_link', 'post_external_title', 'post_external_image', 'page_url',
                    'header_image', 'avatar_image_url', 'profile_handle', 'has_handshake', 'is_sponsored',
                    'sponsor_name', 'shortcode', 'video_view_count', 'likes', 'days_range', 'num_of_posts',
                    'post_image', 'posts_to_not_include', 'until_date', 'from_date', 'post_type',
                    'following', 'start_date', 'end_date', 'link_description_text', 'count_reactions_type',
                    'is_page', 'include_profile_data', 'page_phone', 'page_email', 'page_creation_time',
                    'page_reviews_score', 'page_reviewers_amount', 'page_price_range', 'about',
                    'active_ads_urls', 'delegate_page_id', 'timestamp', 'input', 'error', 'error_code',
                    'warning', 'warning_code'
                ])
            
            # Write the data rows
            for post in posts:
                # Convert JSON fields to strings if needed
                def safe_json_stringify(field_value):
                    """Safely convert any value to a JSON string or return empty string"""
                    if not field_value:
                        return ''
                    
                    if isinstance(field_value, str):
                        # If it looks like JSON but isn't valid, return as is
                        if (field_value.startswith('{') and field_value.endswith('}')) or \
                           (field_value.startswith('[') and field_value.endswith(']')):
                            try:
                                # Try to validate it by parsing and re-stringifying
                                parsed = json.loads(field_value)
                                return json.dumps(parsed)
                            except json.JSONDecodeError:
                                # Just return as is if it looks like JSON but isn't valid
                                return field_value
                        else:
                            # Regular string, return as is
                            return field_value
                    
                    # Try to convert to JSON
                    try:
                        return json.dumps(field_value)
                    except (TypeError, ValueError):
                        # If all else fails, convert to string
                        return str(field_value)
                
                num_likes_type_str = safe_json_stringify(post.num_likes_type)
                count_reactions_type_str = safe_json_stringify(post.count_reactions_type)
                attachments_data_str = safe_json_stringify(post.attachments_data)
                original_post_str = safe_json_stringify(post.original_post)
                active_ads_urls_str = safe_json_stringify(post.active_ads_urls)
                input_str = safe_json_stringify(post.input)
                
                # Format dates
                date_posted_str = post.date_posted.isoformat() if post.date_posted else ''
                page_creation_time_str = post.page_creation_time.isoformat() if post.page_creation_time else ''
                until_date_str = post.until_date.isoformat() if post.until_date else ''
                from_date_str = post.from_date.isoformat() if post.from_date else ''
                start_date_str = post.start_date.isoformat() if post.start_date else ''
                end_date_str = post.end_date.isoformat() if post.end_date else ''
                timestamp_str = post.timestamp.isoformat() if post.timestamp else ''
                
                # Write row based on content type
                if post.content_type == 'reel':
                    writer.writerow([
                        post.url, post.post_id, post.user_url, post.user_username_raw, post.content,
                        date_posted_str, post.hashtags, post.num_comments, post.num_shares,
                        post.video_view_count, post.likes, post.page_name, post.profile_id,
                        post.page_intro, post.page_category, post.page_logo, post.page_external_website,
                        post.page_likes, post.page_followers, post.page_is_verified, post.thumbnail,
                        post.external_link, post.page_url, post.header_image, post.avatar_image_url,
                        post.profile_handle, post.shortcode, post.length, post.audio, post.num_of_posts,
                        post.posts_to_not_include, until_date_str, from_date_str, start_date_str,
                        end_date_str, timestamp_str, input_str, post.error, post.error_code,
                        post.warning, post.warning_code
                    ])
                else:  # Post
                    writer.writerow([
                        post.url, post.post_id, post.user_url, post.user_username_raw, post.content,
                        date_posted_str, post.hashtags, post.num_comments, post.num_shares,
                        num_likes_type_str, post.page_name, post.profile_id, post.page_intro,
                        post.page_category, post.page_logo, post.page_external_website, post.page_likes,
                        post.page_followers, post.page_is_verified, original_post_str, attachments_data_str,
                        post.other_posts_url, post.post_external_link, post.post_external_title,
                        post.post_external_image, post.page_url, post.header_image, post.avatar_image_url,
                        post.profile_handle, post.has_handshake, post.is_sponsored, post.sponsor_name,
                        post.shortcode, post.video_view_count, post.likes, post.days_range,
                        post.num_of_posts, post.post_image, post.posts_to_not_include, until_date_str,
                        from_date_str, post.post_type, post.following, start_date_str, end_date_str,
                        post.link_description_text, count_reactions_type_str, post.is_page,
                        post.include_profile_data, post.page_phone, post.page_email, page_creation_time_str,
                        post.page_reviews_score, post.page_reviewers_amount, post.page_price_range,
                        post.about, active_ads_urls_str, post.delegate_page_id, timestamp_str, input_str,
                        post.error, post.error_code, post.warning, post.warning_code
                    ])
            
            return response
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST) 