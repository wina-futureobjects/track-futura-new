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
from .models import InstagramPost, Folder
from .serializers import InstagramPostSerializer, FolderSerializer
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
    API endpoint for managing Instagram data folders
    """
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [AllowAny]  # For testing, use proper permissions in production

class InstagramPostViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Instagram Posts
    """
    serializer_class = InstagramPostSerializer
    permission_classes = [AllowAny]  # Allow any user to access these endpoints for testing
    
    def get_queryset(self):
        """
        Filter posts by folder if folder_id is provided
        """
        queryset = InstagramPost.objects.all()
        
        # Filter by folder if specified
        folder_id = self.request.query_params.get('folder_id')
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        
        # Filter by content type if specified
        content_type = self.request.query_params.get('content_type')
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        # Add search functionality
        search_query = self.request.query_params.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user_posted__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(hashtags__icontains=search_query) |
                Q(content_type__icontains=search_query) |
                Q(post_id__icontains=search_query)
            )
        
        return queryset

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
        
        # Special handling for ISO format dates (like 2025-04-14T08:27:06.000Z)
        if 'T' in clean_date and (clean_date.endswith('Z') or '+' in clean_date):
            try:
                # Use Python's built-in ISO parser for efficiency
                from datetime import datetime
                return datetime.fromisoformat(clean_date.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                # If that fails, continue with the regular parsing methods
                print(f"ISO format detection failed for: {clean_date}")
                pass
            
        # Detect and fix common Instagram date formats
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
                # Use dateparser if available with specific settings for Instagram
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
                    '%Y-%m-%dT%H:%M:%S.%fZ', # 2025-04-14T08:27:06.000Z
                    '%Y-%m-%dT%H:%M:%SZ',    # 2025-04-14T08:27:06Z
                    '%Y-%m-%dT%H:%M:%S.%f',  # 2025-04-14T08:27:06.000
                    '%Y-%m-%dT%H:%M:%S',     # 2025-04-14T08:27:06
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
            print(f"Date parsing error: {str(e)} for value: '{clean_date}'")
            return None

    @action(detail=False, methods=['POST'])
    def upload_csv(self, request):
        """
        Upload CSV file and parse the data
        """
        try:
            csv_file = request.FILES.get('file')
            if not csv_file:
                return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not csv_file.name.endswith('.csv'):
                return Response({'error': 'File must be a CSV'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get folder_id from request data
            folder_id = request.data.get('folder_id')
            folder = None
            if folder_id:
                folder = get_object_or_404(Folder, id=folder_id)
            
            # Get content_type from request data (post or reel)
            content_type = request.data.get('content_type', 'post')
            
            # Read the CSV file
            decoded_file = csv_file.read().decode('utf-8', errors='replace')  # Handle encoding issues
            io_string = io.StringIO(decoded_file)
            
            # Get CSV header and determine format
            first_line = io_string.readline().strip()
            header = first_line.split(',')
            print(f"CSV Header: {header}")
            
            # Reset file pointer to beginning
            io_string.seek(0)
            reader = csv.DictReader(io_string)
            
            # Lists to track created and updated objects
            created_objects = []
            updated_objects = []
            rejected_rows = []
            
            total_rows = 0
            
            # Process each row
            for row in reader:
                total_rows += 1
                
                # Debug log every 10 rows
                if total_rows % 10 == 0:
                    print(f"Processing row {total_rows}...")
                
                # Check for empty row
                if not row:
                    rejected_rows.append({
                        'reason': 'Empty row',
                        'row_number': total_rows + 1,
                    })
                    continue
                
                # Extract post_id from different possible sources
                post_id = None
                
                # Try different fields that might contain the post ID
                for field in ['post_id', 'shortcode', 'content_id']:
                    if field in row and row.get(field):
                        post_id = row.get(field)
                        break
                
                # If no post_id found but URL exists, extract from URL
                if not post_id and row.get('url'):
                    url = row.get('url', '')
                    # Extract post ID from Instagram URL (e.g., https://www.instagram.com/p/ABC123/)
                    import re
                    match = re.search(r'/p/([^/]+)/', url)
                    if match:
                        post_id = match.group(1)
                
                if not post_id:
                    rejected_rows.append({
                        'reason': 'Missing post_id',
                        'row_number': total_rows + 1,
                        'data': str(row)[:100] + '...' if len(str(row)) > 100 else str(row)
                    })
                    continue
                
                try:
                    # Parse date fields - handle empty strings 
                    date_posted_raw = row.get('date_posted', None)
                    parsed_date = self._parse_date(date_posted_raw)
                    
                    # If date parsing failed but timestamp is available, try to use that
                    if parsed_date is None and row.get('timestamp'):
                        parsed_date = self._parse_date(row.get('timestamp'))
                    
                    # Prepare the default data dictionary
                    default_data = {
                        'url': row.get('url', ''),
                        'user_posted': row.get('user_posted', ''),
                        'description': row.get('description', ''),
                        'hashtags': row.get('hashtags', ''),
                        'num_comments': self._safe_int_convert(row.get('num_comments')),
                        'date_posted': parsed_date,  # Use the parsed date
                        'likes': self._safe_int_convert(row.get('likes')),
                        'photos': row.get('photos', ''),
                        'videos': row.get('videos', ''),
                        'location': row.get('location', ''),
                        'latest_comments': row.get('latest_comments', ''),
                        'discovery_input': row.get('discovery_input', ''),
                        'thumbnail': row.get('thumbnail', ''),
                        'content_type': content_type,  # Set from the request parameter
                        'platform_type': 'IG Post' if content_type == 'post' else 'IG Reel',  # Set platform type based on content_type
                        'engagement_score': self._safe_float_convert(row.get('engagement_score_view')),
                        'tagged_users': row.get('tagged_users', ''),
                        'followers': self._safe_int_convert(row.get('followers')),
                        'posts_count': self._safe_int_convert(row.get('posts_count')),
                        'profile_image_link': row.get('profile_image_link', ''),
                        'is_verified': self._safe_bool_convert(row.get('is_verified')),
                        'is_paid_partnership': self._safe_bool_convert(row.get('is_paid_partnership')),
                        'folder': folder,
                    }
                    
                    # Check if post already exists in this specific folder
                    if folder:
                        existing_post = InstagramPost.objects.filter(post_id=post_id, folder=folder).first()
                    else:
                        existing_post = InstagramPost.objects.filter(post_id=post_id, folder__isnull=True).first()
                    
                    if existing_post:
                        # Update existing post in this folder
                        for key, value in default_data.items():
                            if key != 'folder':  # Preserve the folder
                                setattr(existing_post, key, value)
                        existing_post.save()
                        updated_objects.append(existing_post)
                    else:
                        # Create a new post
                        default_data['post_id'] = post_id
                        new_post = InstagramPost.objects.create(**default_data)
                        created_objects.append(new_post)
                except Exception as e:
                    rejected_rows.append({
                        'reason': str(e),
                        'row_number': total_rows + 1,  # +1 for header
                        'post_id': post_id,
                        'date': row.get('date_posted', 'unknown')
                    })
            
            total_count = len(created_objects) + len(updated_objects)
            content_type_label = "reels" if content_type == "reel" else "posts"
            message = f"Successfully processed {total_count} Instagram {content_type_label}: {len(created_objects)} created, {len(updated_objects)} updated"
            
            if rejected_rows:
                message += f". {len(rejected_rows)} rows were rejected."
            
            # Log summary
            print(f"CSV Import Summary: {message}")
            print(f"Total rows: {total_rows}, Created: {len(created_objects)}, Updated: {len(updated_objects)}, Rejected: {len(rejected_rows)}")
            
            # Add more descriptive information about the import
            return Response({
                'message': message,
                'total_rows_in_csv': total_rows,
                'count': total_count,
                'created': len(created_objects),
                'updated': len(updated_objects),
                'rejected': len(rejected_rows),
                'rejected_details': rejected_rows[:10] if rejected_rows else [],  # Only return first 10 rejected rows
                'content_type': content_type
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            print(f"CSV upload error: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['GET'])
    def download_csv(self, request):
        """
        Download Instagram posts as CSV
        """
        try:
            # Filter by folder if specified
            folder_id = request.query_params.get('folder_id')
            content_type = request.query_params.get('content_type')
            
            posts = InstagramPost.objects.all()
            
            if folder_id:
                posts = posts.filter(folder_id=folder_id)
            
            if content_type:
                posts = posts.filter(content_type=content_type)
                filename = f"instagram_{content_type}s.csv"
            else:
                filename = "instagram_data.csv"
            
            # Create the HttpResponse object with the appropriate CSV header
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            # Create the CSV writer
            writer = csv.writer(response)
            
            # Write the header row
            writer.writerow([
                'url', 'user_posted', 'description', 'hashtags', 'num_comments',
                'date_posted', 'likes', 'photos', 'videos', 'location',
                'latest_comments', 'post_id', 'discovery_input', 'thumbnail',
                'content_type', 'platform_type', 'engagement_score', 'tagged_users', 'followers',
                'posts_count', 'profile_image_link', 'is_verified', 'is_paid_partnership'
            ])
            
            # Write the data rows
            for post in posts:
                writer.writerow([
                    post.url, post.user_posted, post.description, post.hashtags, post.num_comments,
                    post.date_posted, post.likes, post.photos, post.videos, post.location,
                    post.latest_comments, post.post_id, post.discovery_input, post.thumbnail,
                    post.content_type, post.platform_type, post.engagement_score, post.tagged_users, post.followers,
                    post.posts_count, post.profile_image_link, post.is_verified, post.is_paid_partnership
                ])
            
            return response
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def move_to_folder(self, request):
        """
        Move posts to a specific folder
        """
        try:
            post_ids = request.data.get('post_ids', [])
            folder_id = request.data.get('folder_id')
            
            if not post_ids:
                return Response({'error': 'No posts specified'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the target folder (or None for uncategorized)
            folder = None
            if folder_id:
                folder = get_object_or_404(Folder, id=folder_id)
            
            # Move the posts
            posts = InstagramPost.objects.filter(id__in=post_ids)
            count = posts.count()
            
            for post in posts:
                post.folder = folder
                post.save()
            
            folder_name = folder.name if folder else "uncategorized"
            return Response({
                'message': f'Successfully moved {count} posts to {folder_name}',
                'count': count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
