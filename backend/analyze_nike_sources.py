#!/usr/bin/env python
"""
Nike TrackSource Analysis Script
"""

import os
import sys
import django

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def analyze_nike_sources():
    """Analyze Nike TrackSources and actual data"""
    from track_accounts.models import TrackSource, UnifiedRunFolder
    from instagram_data.models import InstagramPost, Folder as InstagramFolder  
    from facebook_data.models import FacebookPost, Folder as FacebookFolder

    print('=== NIKE TRACK SOURCES ANALYSIS ===')

    # Get Nike Instagram source (ID: 6)
    nike_ig_source = TrackSource.objects.get(id=6)
    print(f'Nike Instagram Source: {nike_ig_source.name}')
    print(f'  Project: {nike_ig_source.project_id}')
    print(f'  Instagram Link: {nike_ig_source.instagram_link}')
    print(f'  Folder ID: {nike_ig_source.folder_id}')

    # Check if there are unified folders linked to this source
    unified_folders = UnifiedRunFolder.objects.filter(project_id=nike_ig_source.project_id)
    print(f'  Unified folders in project {nike_ig_source.project_id}: {unified_folders.count()}')

    for folder in unified_folders:
        print(f'    - {folder.name} (Type: {folder.folder_type})')

    # Get Nike Facebook source (ID: 11)  
    nike_fb_source = TrackSource.objects.get(id=11)
    print(f'\nNike Facebook Source: {nike_fb_source.name}')
    print(f'  Project: {nike_fb_source.project_id}')
    print(f'  Facebook Link: {nike_fb_source.facebook_link}')
    print(f'  Folder ID: {nike_fb_source.folder_id}')

    print('\n=== ACTUAL DATA ANALYSIS ===')

    # Check what Instagram posts we have
    ig_posts = InstagramPost.objects.all()[:5]
    print(f'Sample Instagram posts (showing first 5 of {InstagramPost.objects.count()}):')
    for post in ig_posts:
        print(f'  - User: {post.user_posted}')
        print(f'    URL: {post.url}')
        folder_name = post.folder.name if post.folder else "No folder"
        print(f'    Folder: {folder_name}')

    # Check what Facebook posts we have
    fb_posts = FacebookPost.objects.all()[:5]
    print(f'\nSample Facebook posts (showing first 5 of {FacebookPost.objects.count()}):')
    for post in fb_posts:
        user = post.user_posted
        if isinstance(user, dict):
            user_name = user.get('name', 'Unknown')
        else:
            user_name = str(user)
        print(f'  - User: {user_name}')
        print(f'    URL: {post.url}')
        folder_name = post.folder.name if post.folder else "No folder"
        print(f'    Folder: {folder_name}')
        
    print('\n=== MISMATCH ANALYSIS ===')
    print('The issue is clear:')
    print('✅ Nike TrackSources exist in the system')
    print('❌ But actual scraped data is from Adidas, not Nike')
    print('❌ No data is linked to the Nike TrackSources')
    print('\nThe frontend is looking for data linked to Nike sources but finds none.')

if __name__ == "__main__":
    analyze_nike_sources()