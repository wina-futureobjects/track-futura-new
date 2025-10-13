#!/usr/bin/env python3
"""
Fix for "No sources found in folder 1" Error
Creates webhook endpoint support for folders with subfolders
"""

import requests
import json

def create_webhook_fix():
    print('🔧 CREATING WEBHOOK AGGREGATION FIX')
    print('=' * 50)
    
    # This is the backend fix that needs to be applied
    backend_fix_code = '''
# ADD TO: backend/brightdata_integration/views.py

@api_view(['GET'])
def webhook_results_by_folder_id(request, folder_id):
    """
    Get webhook-delivered results for a folder by ID, including subfolder aggregation
    Handles both direct folder data and aggregated subfolder data
    """
    try:
        # First check if we have direct webhook data for this folder
        folder_posts = BrightDataScrapedPost.objects.filter(
            job_folder_id=folder_id,
            webhook_delivered=True
        ).order_by('-created_at')
        
        if folder_posts.exists():
            # Direct folder data available
            posts_data = []
            for post in folder_posts:
                post_data = {
                    'id': post.id,
                    'post_id': post.post_id,
                    'url': post.url,
                    'user_posted': post.user_posted,
                    'content': post.description or post.content,
                    'likes': post.likes or 0,
                    'num_comments': post.num_comments or 0,
                    'date_posted': post.date_posted.isoformat() if post.date_posted else '',
                    'webhook_delivered': post.webhook_delivered,
                    'created_at': post.created_at.isoformat()
                }
                posts_data.append(post_data)
            
            return Response({
                'success': True,
                'total_results': len(posts_data),
                'data': posts_data,
                'source': 'direct_folder_webhook'
            })
        
        # No direct data, try to get folder info and aggregate subfolders
        try:
            import requests
            folder_response = requests.get(f'http://localhost:8000/api/track-accounts/report-folders/{folder_id}/')
            if folder_response.status_code == 200:
                folder_data = folder_response.json()
                subfolders = folder_data.get('subfolders', [])
                
                if subfolders:
                    # Aggregate posts from all subfolders
                    all_posts = []
                    for subfolder in subfolders:
                        subfolder_id = subfolder.get('id')
                        platform = subfolder.get('platform', 'instagram')
                        
                        # Try to get posts from platform-specific endpoints
                        try:
                            posts_endpoint = f'http://localhost:8000/api/{platform}-data/folders/{subfolder_id}/posts/'
                            posts_response = requests.get(posts_endpoint)
                            if posts_response.status_code == 200:
                                posts_data = posts_response.json()
                                posts = posts_data.get('results', posts_data)
                                
                                # Transform posts to common format
                                for i, post in enumerate(posts):
                                    transformed_post = {
                                        'id': post.get('id', i + len(all_posts) + 1),
                                        'post_id': post.get('post_id') or post.get('shortcode') or f'post_{i}',
                                        'url': post.get('url') or post.get('postUrl', ''),
                                        'user_posted': post.get('user_posted') or post.get('ownerUsername') or post.get('user', 'Unknown'),
                                        'content': post.get('description') or post.get('caption') or post.get('text') or post.get('content', ''),
                                        'likes': int(post.get('likes') or post.get('likesCount') or 0),
                                        'num_comments': int(post.get('num_comments') or post.get('commentsCount') or post.get('comments') or 0),
                                        'date_posted': post.get('date_posted') or post.get('timestamp') or post.get('date', ''),
                                        'platform': platform,
                                        'subfolder_id': subfolder_id,
                                        'created_at': post.get('created_at') or post.get('timestamp', '')
                                    }
                                    all_posts.append(transformed_post)
                        except Exception as e:
                            print(f'Error fetching posts from {platform} subfolder {subfolder_id}: {e}')
                    
                    if all_posts:
                        return Response({
                            'success': True,
                            'total_results': len(all_posts),
                            'data': all_posts,
                            'source': 'aggregated_subfolders',
                            'folder_name': folder_data.get('name'),
                            'subfolders_processed': len(subfolders)
                        })
                    else:
                        return Response({
                            'success': False,
                            'message': f'Folder {folder_id} has subfolders but no accessible post data',
                            'total_results': 0,
                            'data': [],
                            'subfolders_found': len(subfolders)
                        })
                else:
                    return Response({
                        'success': False,
                        'message': f'Folder {folder_id} exists but has no subfolders or direct data',
                        'total_results': 0,
                        'data': []
                    })
            else:
                return Response({
                    'success': False,
                    'message': f'Folder {folder_id} not found',
                    'total_results': 0,
                    'data': []
                })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error accessing folder {folder_id}: {str(e)}',
                'total_results': 0,
                'data': []
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Database error: {str(e)}',
            'total_results': 0,
            'data': []
        })

# ADD TO: backend/brightdata_integration/urls.py
path('webhook-results/job/<int:folder_id>/', views.webhook_results_by_folder_id, name='webhook_results_by_folder_id'),
'''
    
    print('📋 BACKEND FIX CODE:')
    print(backend_fix_code)
    
    print('\n🎯 IMPLEMENTATION STEPS:')
    print('1. Add the webhook_results_by_folder_id function to backend/brightdata_integration/views.py')
    print('2. Add the URL pattern to backend/brightdata_integration/urls.py')
    print('3. Deploy the changes to production')
    print('4. Test the endpoint: /api/brightdata/webhook-results/job/1/')
    
    print('\n✅ EXPECTED RESULT:')
    print('- Folder 1 will aggregate data from subfolders 5 (Facebook) and 2 (Instagram)')
    print('- Frontend will receive combined webhook data for display')
    print('- Error "No sources found in folder 1" will be resolved')

if __name__ == '__main__':
    create_webhook_fix()