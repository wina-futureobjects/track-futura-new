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
            
            # Read the CSV file
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            # Lists to track created and updated objects
            created_objects = []
            updated_objects = []
            
            # Process each row
            for row in reader:
                # Parse date fields
                date_posted = row.get('date_posted', None)
                if date_posted:
                    try:
                        date_posted = datetime.datetime.fromisoformat(date_posted)
                    except ValueError:
                        date_posted = None
                
                # Prepare the default data dictionary
                default_data = {
                    'url': row.get('url', ''),
                    'user_posted': row.get('user_posted', ''),
                    'description': row.get('description', ''),
                    'hashtags': row.get('hashtags', ''),
                    'num_comments': int(row.get('num_comments', 0) or 0),
                    'date_posted': date_posted,
                    'likes': int(row.get('likes', 0) or 0),
                    'photos': row.get('photos', ''),
                    'videos': row.get('videos', ''),
                    'location': row.get('location', ''),
                    'latest_comments': row.get('latest_comments', ''),
                    'discovery_input': row.get('discovery_input', ''),
                    'thumbnail': row.get('thumbnail', ''),
                    'content_type': row.get('content_type', ''),
                    'engagement_score': float(row.get('engagement_score_view', 0) or 0),
                    'tagged_users': row.get('tagged_users', ''),
                    'followers': int(row.get('followers', 0) or 0),
                    'posts_count': int(row.get('posts_count', 0) or 0),
                    'profile_image_link': row.get('profile_image_link', ''),
                    'is_verified': row.get('is_verified', '').lower() == 'true',
                    'is_paid_partnership': row.get('is_paid_partnership', '').lower() == 'true',
                    'folder': folder,
                }
                
                post_id = row.get('post_id', '')
                
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
            
            total_count = len(created_objects) + len(updated_objects)
            message = f"Successfully processed {total_count} posts: {len(created_objects)} created, {len(updated_objects)} updated"
            
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
        Download Instagram posts as CSV
        """
        try:
            # Filter by folder if specified
            folder_id = request.query_params.get('folder_id')
            posts = InstagramPost.objects.all()
            if folder_id:
                posts = posts.filter(folder_id=folder_id)
            
            # Create the HttpResponse object with the appropriate CSV header
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="instagram_data.csv"'
            
            # Create the CSV writer
            writer = csv.writer(response)
            
            # Write the header row
            writer.writerow([
                'url', 'user_posted', 'description', 'hashtags', 'num_comments',
                'date_posted', 'likes', 'photos', 'videos', 'location',
                'latest_comments', 'post_id', 'discovery_input', 'thumbnail',
                'content_type', 'engagement_score', 'tagged_users', 'followers',
                'posts_count', 'profile_image_link', 'is_verified', 'is_paid_partnership'
            ])
            
            # Write the data rows
            for post in posts:
                writer.writerow([
                    post.url, post.user_posted, post.description, post.hashtags, post.num_comments,
                    post.date_posted, post.likes, post.photos, post.videos, post.location,
                    post.latest_comments, post.post_id, post.discovery_input, post.thumbnail,
                    post.content_type, post.engagement_score, post.tagged_users, post.followers,
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
