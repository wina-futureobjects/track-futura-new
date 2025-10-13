from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from track_accounts.models import UnifiedRunFolder
from brightdata_integration.models import BrightDataScrapedPost
import json
import csv
import io
from datetime import datetime
import uuid

@csrf_exempt
@require_http_methods(["POST"])
def upload_data_file(request):
    """
    Upload JSON or CSV file and create a new folder with the data
    """
    try:
        # Get form data
        folder_name = request.POST.get('folder_name', 'Uploaded Data')
        platform = request.POST.get('platform', 'instagram')
        file = request.FILES.get('data_file')
        
        if not file:
            return JsonResponse({
                'success': False,
                'error': 'No file uploaded'
            }, status=400)
        
        # Validate file type
        if not file.name.endswith(('.json', '.csv')):
            return JsonResponse({
                'success': False,
                'error': 'Only JSON and CSV files are supported'
            }, status=400)
        
        # Create new folder
        folder = UnifiedRunFolder.objects.create(
            name=folder_name,
            project_id=1,  # Default project
            folder_type='run',
            platform=platform
        )
        
        # Process the file
        file_content = file.read().decode('utf-8')
        posts_created = 0
        
        if file.name.endswith('.json'):
            # Process JSON file
            try:
                data = json.loads(file_content)
                
                # Handle different JSON structures
                if isinstance(data, list):
                    posts_data = data
                elif isinstance(data, dict) and 'data' in data:
                    posts_data = data['data']
                elif isinstance(data, dict) and 'results' in data:
                    posts_data = data['results']
                else:
                    posts_data = [data]  # Single post object
                
                # Create posts
                for i, post_data in enumerate(posts_data):
                    BrightDataScrapedPost.objects.create(
                        folder_id=folder.id,
                        post_id=post_data.get('post_id', post_data.get('shortcode', post_data.get('id', f'post_{i}'))),
                        platform=platform,
                        raw_data=post_data,
                        user_posted=post_data.get('user_posted', post_data.get('user_username', post_data.get('username', 'Unknown'))),
                        content=post_data.get('content', post_data.get('caption', post_data.get('description', ''))),
                        likes=int(post_data.get('likes', post_data.get('likes_count', post_data.get('likesCount', 0))) or 0),
                        comments=int(post_data.get('comments', post_data.get('comments_count', post_data.get('commentsCount', 0))) or 0),
                        url=post_data.get('url', post_data.get('post_url', post_data.get('link', ''))),
                        date_posted=post_data.get('date_posted', post_data.get('timestamp', datetime.now().isoformat())),
                    )
                    posts_created += 1
                    
            except json.JSONDecodeError as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid JSON format: {str(e)}'
                }, status=400)
        
        elif file.name.endswith('.csv'):
            # Process CSV file
            try:
                csv_reader = csv.DictReader(io.StringIO(file_content))
                
                for i, row in enumerate(csv_reader):
                    BrightDataScrapedPost.objects.create(
                        folder_id=folder.id,
                        post_id=row.get('post_id', row.get('id', f'post_{i}')),
                        platform=platform,
                        raw_data=dict(row),
                        user_posted=row.get('user_posted', row.get('username', 'Unknown')),
                        content=row.get('content', row.get('caption', row.get('description', ''))),
                        likes=int(row.get('likes', row.get('likes_count', 0)) or 0),
                        comments=int(row.get('comments', row.get('comments_count', 0)) or 0),
                        url=row.get('url', row.get('post_url', '')),
                        date_posted=row.get('date_posted', row.get('timestamp', datetime.now().isoformat())),
                    )
                    posts_created += 1
                    
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Error processing CSV: {str(e)}'
                }, status=400)
        
        return JsonResponse({
            'success': True,
            'folder_id': folder.id,
            'folder_name': folder.name,
            'posts_created': posts_created,
            'message': f'Successfully created folder "{folder.name}" with {posts_created} posts',
            'redirect_url': f'/organizations/1/projects/1/data-storage/run/{folder.id}/'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def list_uploaded_folders(request):
    """
    List all folders with uploaded data
    """
    try:
        folders = UnifiedRunFolder.objects.filter(
            project_id=1
        ).order_by('-created_at')
        
        folder_data = []
        for folder in folders:
            post_count = BrightDataScrapedPost.objects.filter(folder_id=folder.id).count()
            folder_data.append({
                'id': folder.id,
                'name': folder.name,
                'platform': getattr(folder, 'platform', 'unknown'),
                'post_count': post_count,
                'created_at': folder.created_at.isoformat() if folder.created_at else None,
                'folder_type': folder.folder_type
            })
        
        return JsonResponse({
            'success': True,
            'folders': folder_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error listing folders: {str(e)}'
        }, status=500)