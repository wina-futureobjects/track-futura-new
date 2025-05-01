from django.shortcuts import render, get_object_or_404
import csv
import io
import json
import datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from django.db.models import Q
from .models import TrackAccount, TrackAccountFolder, ReportFolder, ReportEntry
from .serializers import (
    TrackAccountSerializer, TrackAccountFolderSerializer,
    ReportFolderSerializer, ReportEntrySerializer, ReportFolderDetailSerializer
)

class TrackAccountFolderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Track Account folders
    """
    queryset = TrackAccountFolder.objects.all()
    serializer_class = TrackAccountFolderSerializer
    permission_classes = [AllowAny]  # For testing, use proper permissions in production

class TrackAccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Track Accounts
    """
    serializer_class = TrackAccountSerializer
    permission_classes = [AllowAny]  # Allow any user to access these endpoints for testing
    
    def get_queryset(self):
        """
        Filter accounts by folder if folder_id is provided
        """
        queryset = TrackAccount.objects.all()
        
        # Filter by folder if specified
        folder_id = self.request.query_params.get('folder_id')
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        
        # Add search functionality
        search_query = self.request.query_params.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(iac_no__icontains=search_query) |
                Q(facebook_id__icontains=search_query) |
                Q(instagram_id__icontains=search_query) |
                Q(linkedin_id__icontains=search_query) |
                Q(tiktok_id__icontains=search_query) |
                Q(risk_classification__icontains=search_query)
            )
        
        return queryset

    @action(detail=False, methods=['POST'])
    def upload_csv(self, request):
        """
        Upload CSV file and parse the track account data
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
                folder = get_object_or_404(TrackAccountFolder, id=folder_id)
            
            # Read the CSV file
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            # Lists to track created and updated objects
            created_objects = []
            updated_objects = []
            
            # Process each row
            for row in reader:
                # Check if the row has the required data
                if not row.get('Name') or not row.get('IAC_NO'):
                    continue
                
                # Prepare the data dictionary
                default_data = {
                    'name': row.get('Name', ''),
                    'iac_no': row.get('IAC_NO', ''),
                    # Social media usernames
                    'facebook_username': row.get('FB', ''),
                    'instagram_username': row.get('IG', ''),
                    'linkedin_username': row.get('LK', ''),
                    'tiktok_username': row.get('TK', ''),
                    # Social media URLs
                    'facebook_id': row.get('FACEBOOK_ID', ''),
                    'instagram_id': row.get('INSTAGRAM_ID', ''),
                    'linkedin_id': row.get('LINKEDIN_ID', ''),
                    'tiktok_id': row.get('TIKTOK_ID', ''),
                    'other_social_media': row.get('Other Social Media platforms', ''),
                    'risk_classification': row.get('Risk Classification (Others)', ''),
                    'close_monitoring': row.get('Close Monitoring', '').lower() == 'yes',
                    'posting_frequency': row.get('Posting Frequency (High/ Medium/ Low)', ''),
                    'folder': folder,
                }
                
                # Check if account already exists
                try:
                    existing_account = TrackAccount.objects.get(iac_no=default_data['iac_no'])
                    # Update existing account
                    for key, value in default_data.items():
                        setattr(existing_account, key, value)
                    existing_account.save()
                    updated_objects.append(existing_account)
                except TrackAccount.DoesNotExist:
                    # Create a new account
                    new_account = TrackAccount.objects.create(**default_data)
                    created_objects.append(new_account)
            
            total_count = len(created_objects) + len(updated_objects)
            message = f"Successfully processed {total_count} accounts: {len(created_objects)} created, {len(updated_objects)} updated"
            
            return Response({
                'message': message,
                'count': total_count,
                'created': len(created_objects),
                'updated': len(updated_objects)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['GET'])
    def download_csv(self, request):
        """
        Download Track Accounts as CSV
        """
        try:
            # Filter by folder if specified
            folder_id = request.query_params.get('folder_id')
            accounts = TrackAccount.objects.all()
            if folder_id:
                accounts = accounts.filter(folder_id=folder_id)
            
            # Create the HttpResponse object with the appropriate CSV header
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="track_accounts.csv"'
            
            # Create the CSV writer
            writer = csv.writer(response)
            
            # Write the header row
            writer.writerow([
                'FB', 'IG', 'LK', 'TK', '',
                'Number of rows', 'Name', 'IAC_NO', 'FACEBOOK_ID', 'INSTAGRAM_ID', 'LINKEDIN_ID', 
                'TIKTOK_ID', 'Other Social Media platforms', 'Risk Classification (Others)',
                'Close Monitoring', 'Posting Frequency (High/ Medium/ Low)'
            ])
            
            # Write the data rows
            for account in accounts:
                writer.writerow([
                    account.facebook_username,
                    account.instagram_username,
                    account.linkedin_username,
                    account.tiktok_username,
                    '',  # Empty column
                    '',  # Number of rows (leave empty)
                    account.name,
                    account.iac_no,
                    account.facebook_id,
                    account.instagram_id,
                    account.linkedin_id,
                    account.tiktok_id,
                    account.other_social_media,
                    account.risk_classification,
                    'Yes' if account.close_monitoring else 'No',
                    account.posting_frequency
                ])
            
            return response
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def move_to_folder(self, request):
        """
        Move accounts to a specific folder
        """
        try:
            account_ids = request.data.get('account_ids', [])
            folder_id = request.data.get('folder_id')
            
            if not account_ids:
                return Response({'error': 'No accounts specified'}, status=status.HTTP_400_BAD_REQUEST)
            
            folder = None
            if folder_id:
                folder = get_object_or_404(TrackAccountFolder, id=folder_id)
            
            accounts = TrackAccount.objects.filter(id__in=account_ids)
            count = accounts.count()
            
            if count == 0:
                return Response({'error': 'No accounts found with provided IDs'}, status=status.HTTP_404_NOT_FOUND)
            
            # Update the folder for all matching accounts
            accounts.update(folder=folder)
            
            return Response({
                'message': f"Successfully moved {count} accounts to {folder.name if folder else 'no folder'}",
                'count': count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ReportFolderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing generated reports
    """
    queryset = ReportFolder.objects.all()
    serializer_class = ReportFolderSerializer
    permission_classes = [AllowAny]  # For testing, use proper permissions in production
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ReportFolderDetailSerializer
        return self.serializer_class
    
    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle validation errors better
        """
        try:
            # Validate required fields
            if not request.data.get('name'):
                return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not request.data.get('start_date'):
                return Response({'error': 'Start date is required'}, status=status.HTTP_400_BAD_REQUEST)
                
            if not request.data.get('end_date'):
                return Response({'error': 'End date is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create serializer with data
            serializer = self.get_serializer(data=request.data)
            
            # If serializer validation fails, return detailed errors
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Save the instance
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            print(f"Error creating report folder: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['POST'])
    def generate_report(self, request, pk=None):
        """
        Generate a new report and save it to the database
        Supports all platform types: Instagram, Facebook, LinkedIn, TikTok
        """
        try:
            # Get request data
            folder_ids_by_platform = request.data.get('platform_folders', {})
            instagram_folder_ids = folder_ids_by_platform.get('instagram', [])
            facebook_folder_ids = folder_ids_by_platform.get('facebook', [])
            linkedin_folder_ids = folder_ids_by_platform.get('linkedin', [])
            tiktok_folder_ids = folder_ids_by_platform.get('tiktok', [])
            
            # For backward compatibility
            if not folder_ids_by_platform and request.data.get('folder_ids'):
                instagram_folder_ids = request.data.get('folder_ids', [])
            
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            report_name = request.data.get('name', f"Multi-Platform Report {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
            report_description = request.data.get('description', 'Generated multi-platform report')
            
            all_folder_ids = instagram_folder_ids + facebook_folder_ids + linkedin_folder_ids + tiktok_folder_ids
            if not all_folder_ids:
                return Response({'error': 'No folders specified'}, status=status.HTTP_400_BAD_REQUEST)
                
            # Create the report folder
            report = ReportFolder.objects.create(
                name=report_name,
                description=report_description,
                start_date=start_date if start_date else datetime.datetime.now().isoformat(),
                end_date=end_date if end_date else datetime.datetime.now().isoformat(),
                source_folders=json.dumps({
                    'instagram': instagram_folder_ids,
                    'facebook': facebook_folder_ids,
                    'linkedin': linkedin_folder_ids,
                    'tiktok': tiktok_folder_ids
                })
            )
            
            total_posts = 0
            matched_posts = 0
            
            # Process Instagram posts
            if instagram_folder_ids:
                from instagram_data.models import InstagramPost
                instagram_posts = InstagramPost.objects.filter(folder_id__in=instagram_folder_ids)
                total_posts += instagram_posts.count()
                
                for post in instagram_posts:
                    # Extract username from post data
                    username = self._extract_username_from_discovery_input(post.discovery_input)
                    
                    # Find matching account
                    account = self._find_matching_account(username)
                    
                    # Create report entry
                    entry = ReportEntry(
                        report=report,
                        username=username or post.user_posted,
                        post_url=post.url,
                        posting_date=post.date_posted,
                        platform_type=post.platform_type or ('IG Post' if post.content_type == 'post' else 'IG Reel'),
                        keywords=post.hashtags,
                        content=post.description,
                        post_id=f"instagram_{post.id}",
                        sn=''
                    )
                    
                    if account:
                        matched_posts += 1
                        entry.name = account.name
                        entry.iac_no = account.iac_no
                        entry.entity = ''
                        entry.close_monitoring = 'Yes' if account.close_monitoring else 'No'
                        entry.track_account_id = account.id
                    else:
                        entry.name = None
                        entry.iac_no = None
                        entry.entity = None
                        entry.close_monitoring = 'No'
                        entry.track_account_id = None
                    
                    entry.save()
            
            # Process Facebook posts
            if facebook_folder_ids:
                from facebook_data.models import FacebookPost
                facebook_posts = FacebookPost.objects.filter(folder_id__in=facebook_folder_ids)
                total_posts += facebook_posts.count()
                
                print(f"Processing {facebook_posts.count()} Facebook posts")
                for post in facebook_posts:
                    # Use user_url for matching with facebook_id in track accounts
                    account = None
                    if post.user_url and post.user_url.strip():
                        print(f"Attempting to match Facebook post by user_url: {post.user_url}")
                        account = self._find_matching_facebook_account(post.user_url)
                    else:
                        print(f"Facebook post has no user_url, post_id: {post.post_id}")
                    
                    # Fall back to username matching if no match found via URL
                    if not account:
                        username = post.user_posted or post.page_name or post.user_username_raw
                        if username:
                            print(f"Falling back to username matching for: {username}")
                            account = self._find_matching_account(username)
                    
                    # Create report entry
                    entry = ReportEntry(
                        report=report,
                        username=post.user_posted or post.page_name or post.user_username_raw,
                        post_url=post.url,
                        posting_date=post.date_posted,
                        platform_type=post.platform_type or ('FB Post' if post.content_type == 'post' else 'FB Reel'),
                        keywords=post.hashtags,
                        content=post.description or post.content,
                        post_id=f"facebook_{post.id}",
                        sn=''
                    )
                    
                    if account:
                        matched_posts += 1
                        print(f"Successfully matched Facebook post to account: {account.name}")
                        entry.name = account.name
                        entry.iac_no = account.iac_no
                        entry.entity = ''
                        entry.close_monitoring = 'Yes' if account.close_monitoring else 'No'
                        entry.track_account_id = account.id
                    else:
                        print(f"No match found for Facebook post: {post.url}")
                        entry.name = None
                        entry.iac_no = None
                        entry.entity = None
                        entry.close_monitoring = 'No'
                        entry.track_account_id = None
                    
                    entry.save()
            
            # Process LinkedIn posts
            if linkedin_folder_ids:
                from linkedin_data.models import LinkedInPost
                linkedin_posts = LinkedInPost.objects.filter(folder_id__in=linkedin_folder_ids)
                total_posts += linkedin_posts.count()
                
                for post in linkedin_posts:
                    # Extract username from LinkedIn data
                    username = post.user_posted or post.profile_name
                    
                    # Find matching account
                    account = self._find_matching_account(username)
                    
                    # Create report entry
                    entry = ReportEntry(
                        report=report,
                        username=username,
                        post_url=post.url,
                        posting_date=post.date_posted,
                        platform_type='LinkedIn Post',
                        keywords=post.hashtags,
                        content=post.description,
                        post_id=f"linkedin_{post.id}",
                        sn=''
                    )
                    
                    if account:
                        matched_posts += 1
                        entry.name = account.name
                        entry.iac_no = account.iac_no
                        entry.entity = ''
                        entry.close_monitoring = 'Yes' if account.close_monitoring else 'No'
                        entry.track_account_id = account.id
                    else:
                        entry.name = None
                        entry.iac_no = None
                        entry.entity = None
                        entry.close_monitoring = 'No'
                        entry.track_account_id = None
                    
                    entry.save()
            
            # Process TikTok posts
            if tiktok_folder_ids:
                from tiktok_data.models import TikTokPost
                tiktok_posts = TikTokPost.objects.filter(folder_id__in=tiktok_folder_ids)
                total_posts += tiktok_posts.count()
                
                for post in tiktok_posts:
                    # Extract username from TikTok data
                    username = post.user_posted
                    
                    # Find matching account
                    account = self._find_matching_account(username)
                    
                    # Create report entry
                    entry = ReportEntry(
                        report=report,
                        username=username,
                        post_url=post.url,
                        posting_date=post.date_posted,
                        platform_type='TikTok Video',
                        keywords=post.hashtags,
                        content=post.description,
                        post_id=f"tiktok_{post.id}",
                        sn=''
                    )
                    
                    if account:
                        matched_posts += 1
                        entry.name = account.name
                        entry.iac_no = account.iac_no
                        entry.entity = ''
                        entry.close_monitoring = 'Yes' if account.close_monitoring else 'No'
                        entry.track_account_id = account.id
                    else:
                        entry.name = None
                        entry.iac_no = None
                        entry.entity = None
                        entry.close_monitoring = 'No'
                        entry.track_account_id = None
                    
                    entry.save()
            
            # Update report statistics
            report.total_posts = total_posts
            report.matched_posts = matched_posts
            report.save()
            
            return Response({
                'id': report.id,
                'name': report.name,
                'total_posts': total_posts,
                'matched_posts': matched_posts,
                'platforms': {
                    'instagram': len(instagram_folder_ids) > 0,
                    'facebook': len(facebook_folder_ids) > 0,
                    'linkedin': len(linkedin_folder_ids) > 0,
                    'tiktok': len(tiktok_folder_ids) > 0
                },
                'match_percentage': round((matched_posts / total_posts) * 100) if total_posts > 0 else 0
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            print(f"Error generating report: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['POST'])
    def add_instagram_data(self, request, pk=None):
        """
        Add Instagram data to an existing report folder
        """
        try:
            report = self.get_object()
            
            # Get request data
            instagram_folder_ids = request.data.get('folder_ids', [])
            start_date = request.data.get('start_date')  # We'll still accept these params
            end_date = request.data.get('end_date')      # but not use them for filtering
            append_entries = request.data.get('append_entries', True)
            
            print(f"Adding Instagram data from folders: {instagram_folder_ids}")
            print(f"Date filtering disabled - including all posts")
            
            if not instagram_folder_ids:
                return Response({'error': 'No folders specified'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update source folders
            existing_folders = report.get_source_folders()
            all_folders = existing_folders + [folder_id for folder_id in instagram_folder_ids if folder_id not in existing_folders]
            report.set_source_folders(all_folders)
            report.save()
            
            # If append_entries is False, clear existing entries
            if not append_entries:
                report.entries.all().delete()
                report.matched_posts = 0
                report.total_posts = 0
            
            # Fetch Instagram posts from the specified folders - NO DATE FILTERING
            from instagram_data.models import InstagramPost
            
            # Fetch all posts from the selected folders without date filtering
            posts = InstagramPost.objects.filter(
                folder_id__in=instagram_folder_ids
            )
            
            total_available_posts = posts.count()
            print(f"Total posts available in selected folders: {total_available_posts}")
            
            # Get list of existing post IDs in the report
            existing_post_ids = set(report.entries.values_list('post_id', flat=True))
            print(f"Existing post IDs in report: {len(existing_post_ids)}")
            
            matched_new_posts = 0
            processed_posts = 0
            skipped_posts = 0
            
            # Process each post
            for post in posts:
                # Check if post is already in the report to avoid duplicates
                if str(post.id) in existing_post_ids:
                    skipped_posts += 1
                    continue
                
                processed_posts += 1
                    
                # Extract username from post data
                username = self._extract_username_from_discovery_input(post.discovery_input)
                
                # Find matching account
                account = self._find_matching_account(username)
                
                # Create report entry (regardless of whether there's a match)
                entry = ReportEntry(
                    report=report,
                    username=username,
                    post_url=post.url,
                    posting_date=post.date_posted,
                    platform_type=post.platform_type or ('IG Post' if post.content_type == 'post' else 'IG Reel'),
                    keywords=post.hashtags,
                    content=post.description,
                    post_id=str(post.id),  # Ensure post_id is stored as string for consistency
                    sn=''  # Set S/N to empty string
                )
                
                # If account is matched, add account data
                if account:
                    matched_new_posts += 1
                    entry.name = account.name
                    entry.iac_no = account.iac_no
                    entry.entity = ''  # This could be added later
                    entry.close_monitoring = 'Yes' if account.close_monitoring else 'No'
                    entry.track_account_id = account.id
                else:
                    # For non-matches, leave these fields empty or set to default values
                    entry.name = None
                    entry.iac_no = None
                    entry.entity = None
                    entry.close_monitoring = 'No'
                    entry.track_account_id = None
                
                entry.save()
            
            print(f"Processed {processed_posts} new posts, skipped {skipped_posts} duplicates")
            
            # Update report statistics
            report.total_posts += processed_posts
            report.matched_posts += matched_new_posts
            report.save()
            
            return Response({
                'id': report.id,
                'name': report.name,
                'total_posts': report.total_posts,
                'matched_posts': report.matched_posts,
                'new_posts_added': processed_posts,
                'posts_skipped': skipped_posts,
                'match_percentage': round((report.matched_posts / report.total_posts) * 100) if report.total_posts > 0 else 0
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            print(f"Error adding Instagram data: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['GET'])
    def download_csv(self, request, pk=None):
        """
        Download report as CSV
        """
        try:
            report = self.get_object()
            
            # Create the HttpResponse object with CSV header
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{report.name}.csv"'
            
            # Create the CSV writer
            writer = csv.writer(response)
            
            # Write the header row
            writer.writerow([
                'S/N', 'Name', 'IAC No.', 'Entity', 'Under Close Monitoring? (Yes / No)',
                'Posting Date', 'Platform Type', 'Post URL', 'Username', 
                'Personal/Business', 'Keywords', 'Content'
            ])
            
            # Write data rows
            for index, entry in enumerate(report.entries.all()):
                writer.writerow([
                    index + 1,
                    entry.name or '',
                    entry.iac_no or '',
                    entry.entity or '',
                    entry.close_monitoring or 'No',
                    entry.posting_date.strftime('%Y-%m-%d %H:%M:%S') if entry.posting_date else '',
                    entry.platform_type or 'Instagram Post',
                    entry.post_url or '',
                    entry.username or '',
                    entry.account_type or '',
                    entry.keywords or '',
                    entry.content or ''
                ])
            
            return response
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def _extract_username_from_discovery_input(self, discovery_input):
        """Extract Instagram username from discovery input"""
        if not discovery_input:
            return ''
            
        # Print for debugging
        print(f"Extracting username from: {discovery_input[:100]}...")
        
        username = ''
        
        # STRATEGY 1: Parse as JSON and extract from URL
        try:
            data = json.loads(discovery_input)
            
            # If we have a URL field, extract username from it
            if data.get('url'):
                url = data['url']
                print(f"Found URL in JSON: {url}")
                
                import re
                # Handle different Instagram URL formats
                url_pattern = r'(?:https?:\/\/)?(?:www\.)?instagram\.com\/([^\/\?]+)'
                matches = re.search(url_pattern, url)
                if matches:
                    username = matches.group(1).strip()
                    print(f"Extracted username from URL: '{username}'")
                    return username
                    
            # If we have a username field directly
            if data.get('username') or data.get('user_name'):
                username = data.get('username') or data.get('user_name')
                print(f"Found username in JSON: '{username}'")
                return username
        except Exception as e:
            print(f"JSON parsing error: {str(e)}")
        
        # STRATEGY 2: Direct URL extraction if not JSON but contains instagram.com
        if isinstance(discovery_input, str) and 'instagram.com' in discovery_input:
            try:
                import re
                url_pattern = r'(?:https?:\/\/)?(?:www\.)?instagram\.com\/([^\/\?]+)'
                matches = re.search(url_pattern, discovery_input)
                if matches:
                    username = matches.group(1).strip()
                    print(f"Extracted username from string URL: '{username}'")
                    return username
            except Exception as e:
                print(f"URL extraction error: {str(e)}")
        
        # STRATEGY 3: Look for common username patterns in the string
        if isinstance(discovery_input, str) and ('@' in discovery_input or 'username' in discovery_input.lower()):
            try:
                import re
                # Pattern for @username or "username: something"
                patterns = [
                    r'@([a-zA-Z0-9_\.]+)',                 # @username
                    r'username\s*:\s*([a-zA-Z0-9_\.]+)',   # username: something
                    r'user\s*:\s*([a-zA-Z0-9_\.]+)',       # user: something
                ]
                
                for pattern in patterns:
                    matches = re.search(pattern, discovery_input, re.IGNORECASE)
                    if matches:
                        username = matches.group(1).strip()
                        print(f"Extracted username using pattern {pattern}: '{username}'")
                        return username
            except Exception as e:
                print(f"Pattern matching error: {str(e)}")
        
        # If we get here, we couldn't extract a username
        print(f"Could not extract username from discovery input")
        return username
    
    def _find_matching_account(self, username):
        """Find matching TrackAccount by Instagram username"""
        if not username:
            return None
        
        # Normalize the username input
        normalized_username = username.lower().strip() if username else ''
        if not normalized_username:
            return None
            
        # Debug
        print(f"Looking for match for Instagram username: '{normalized_username}'")
        
        # MATCHING STRATEGY 1: Direct exact match with instagram_username
        try:
            # Direct match with instagram_username field
            account = TrackAccount.objects.filter(instagram_username__iexact=normalized_username).first()
            if account:
                print(f"Found direct match with instagram_username: {account.name} (ID: {account.id})")
                return account
        except Exception as e:
            print(f"Error during direct username match: {str(e)}")
        
        # MATCHING STRATEGY 2: Extract username from instagram_id URL and compare
        try:
            # Query accounts with instagram_id that's not null/empty
            accounts = TrackAccount.objects.exclude(instagram_id__isnull=True).exclude(instagram_id='')
            
            for account in accounts:
                try:
                    # Extract username from instagram_id URL
                    import re
                    url_pattern = r'(?:https?:\/\/)?(?:www\.)?instagram\.com\/([^\/\?]+)'
                    matches = re.search(url_pattern, account.instagram_id)
                    if matches:
                        extracted_username = matches.group(1).lower().strip()
                        if extracted_username == normalized_username:
                            print(f"Found URL match with instagram_id: {account.name} (ID: {account.id})")
                            return account
                except Exception as e:
                    print(f"Error processing account {account.id}: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error during URL extraction match: {str(e)}")
            
        # MATCHING STRATEGY 3: More flexible/partial matching
        try:
            # Check if any account contains this username as part of their instagram fields
            accounts = TrackAccount.objects.filter(
                Q(instagram_username__icontains=normalized_username) | 
                Q(instagram_id__icontains=normalized_username)
            )
            
            if accounts.exists():
                best_match = accounts.first()
                print(f"Found partial match: {best_match.name} (ID: {best_match.id})")
                return best_match
        except Exception as e:
            print(f"Error during partial match: {str(e)}")
        
        # No matches found
        print(f"No matching account found for username: '{normalized_username}'")
        return None

    def _find_matching_facebook_account(self, user_url):
        """Find matching TrackAccount by Facebook user_url"""
        if not user_url:
            return None
        
        # Normalize the user_url input
        normalized_user_url = user_url.lower().strip() if user_url else ''
        if not normalized_user_url:
            return None
            
        # Debug
        print(f"Looking for match for Facebook user_url: '{normalized_user_url}'")
        
        # MATCHING STRATEGY 1: Direct exact match with facebook_id
        try:
            # Direct match with facebook_id field
            account = TrackAccount.objects.filter(facebook_id__iexact=normalized_user_url).first()
            if account:
                print(f"Found direct match with facebook_id: {account.name} (ID: {account.id})")
                return account
        except Exception as e:
            print(f"Error during direct user_url match: {str(e)}")
        
        # Extract identifiers from the post user_url
        import re
        post_profile_path = None
        post_numeric_id = None
        
        # Extract from https://www.facebook.com/people/name/123456789/ or https://www.facebook.com/username/
        path_match = re.search(r'facebook\.com\/(?:people\/)?([^\/\?]+)', normalized_user_url)
        if path_match:
            post_profile_path = path_match.group(1).lower().strip()
        
        # Extract numeric ID if present
        id_match = re.search(r'\/(\d+)\/?(?:\?|$)', normalized_user_url)
        if id_match:
            post_numeric_id = id_match.group(1)
        
        # MATCHING STRATEGY 2: Match extracted paths and IDs against track accounts
        try:
            # Query accounts with facebook_id that's not null/empty
            accounts = TrackAccount.objects.exclude(facebook_id__isnull=True).exclude(facebook_id='')
            
            for account in accounts:
                try:
                    account_fb_id = account.facebook_id.lower().strip()
                    
                    # Direct substring check for full URL
                    if normalized_user_url in account_fb_id or account_fb_id in normalized_user_url:
                        print(f"Found substring match with facebook_id: {account.name} (ID: {account.id})")
                        return account
                    
                    # Extract profile path from account facebook_id
                    acc_path_match = re.search(r'facebook\.com\/(?:people\/)?([^\/\?]+)', account_fb_id)
                    if acc_path_match:
                        acc_profile_path = acc_path_match.group(1).lower().strip()
                        
                        # Compare profile paths if both are available
                        if post_profile_path and acc_profile_path and post_profile_path == acc_profile_path:
                            print(f"Found profile path match with facebook_id: {account.name} (ID: {account.id})")
                            return account
                    
                    # Extract numeric ID from account facebook_id
                    acc_id_match = re.search(r'\/(\d+)\/?(?:\?|$)', account_fb_id)
                    if acc_id_match:
                        acc_numeric_id = acc_id_match.group(1)
                        
                        # Compare numeric IDs if both are available
                        if post_numeric_id and acc_numeric_id and post_numeric_id == acc_numeric_id:
                            print(f"Found numeric ID match with facebook_id: {account.name} (ID: {account.id})")
                            return account
                    
                except Exception as e:
                    print(f"Error processing account {account.id}: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error during URL extraction match: {str(e)}")
            
        # MATCHING STRATEGY 3: More flexible/partial matching
        try:
            # Only try this if we have a profile path to match
            if post_profile_path:
                accounts = TrackAccount.objects.filter(
                    Q(facebook_id__icontains=post_profile_path) |
                    Q(facebook_username__iexact=post_profile_path)
                )
                
                if accounts.exists():
                    best_match = accounts.first()
                    print(f"Found partial match: {best_match.name} (ID: {best_match.id})")
                    return best_match
        except Exception as e:
            print(f"Error during partial match: {str(e)}")
        
        # No matches found
        print(f"No matching account found for user_url: '{normalized_user_url}'")
        return None
