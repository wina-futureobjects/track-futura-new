#!/usr/bin/env python3
"""
Test new endpoints locally before deployment
"""

import os
import sys
import django

# Setup Django
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from track_accounts.models import UnifiedRunFolder

def test_data_setup():
    """Test if we have the right data structure for new endpoints"""
    print("🧪 TESTING DATA SETUP FOR NEW ENDPOINTS")
    print("=" * 50)
    
    # Check folders
    print("\n📁 CHECKING UNIFIED RUN FOLDERS:")
    folders = UnifiedRunFolder.objects.all()[:10]
    for folder in folders:
        print(f"   ID {folder.id}: '{folder.name}' (type: {folder.folder_type})")
    
    # Check scraper requests
    print(f"\n🔍 CHECKING SCRAPER REQUESTS:")
    requests = BrightDataScraperRequest.objects.all()[:10]
    for req in requests:
        print(f"   ID {req.id}: folder_id={req.folder_id}, scrape_number={req.scrape_number}, platform={req.platform}")
    
    # Check scraped posts
    print(f"\n📋 CHECKING SCRAPED POSTS:")
    posts = BrightDataScrapedPost.objects.all()[:5]
    for post in posts:
        print(f"   ID {post.id}: folder_id={post.folder_id}, platform={post.platform}, user={post.user_posted}")
    
    # Find a good folder name for testing
    print(f"\n🎯 FOLDERS WITH SCRAPED DATA:")
    folders_with_data = BrightDataScrapedPost.objects.values('folder_id').distinct()
    
    for folder_data in folders_with_data[:5]:
        folder_id = folder_data['folder_id']
        try:
            folder = UnifiedRunFolder.objects.get(id=folder_id)
            post_count = BrightDataScrapedPost.objects.filter(folder_id=folder_id).count()
            scraper_requests = BrightDataScraperRequest.objects.filter(folder_id=folder_id).count()
            print(f"   Folder '{folder.name}' (ID {folder_id}): {post_count} posts, {scraper_requests} scraper requests")
        except UnifiedRunFolder.DoesNotExist:
            print(f"   Folder ID {folder_id}: No UnifiedRunFolder found, {BrightDataScrapedPost.objects.filter(folder_id=folder_id).count()} posts")

def create_test_folder_if_needed():
    """Create a test folder with proper data structure"""
    print(f"\n🔧 ENSURING TEST FOLDER EXISTS:")
    
    # Create or get Nike folder
    nike_folder, created = UnifiedRunFolder.objects.get_or_create(
        name='nike',
        defaults={
            'folder_type': 'job',
            'description': 'Nike test folder for new endpoints'
        }
    )
    
    if created:
        print(f"   ✅ Created Nike folder (ID: {nike_folder.id})")
    else:
        print(f"   ✅ Nike folder exists (ID: {nike_folder.id})")
    
    # Check if Nike folder has scraper requests
    scraper_requests = BrightDataScraperRequest.objects.filter(folder_id=nike_folder.id)
    if not scraper_requests.exists():
        # Create a test scraper request
        test_request = BrightDataScraperRequest.objects.create(
            folder_id=nike_folder.id,
            scrape_number=1,
            platform='instagram',
            target_url='nike',
            status='completed'
        )
        print(f"   ✅ Created test scraper request (ID: {test_request.id})")
    else:
        print(f"   ✅ Nike folder has {scraper_requests.count()} scraper requests")
    
    # Check if Nike folder has scraped posts
    scraped_posts = BrightDataScrapedPost.objects.filter(folder_id=nike_folder.id)
    if scraped_posts.count() == 0:
        print(f"   ⚠️ Nike folder has no scraped posts - new endpoints will return empty data")
    else:
        print(f"   ✅ Nike folder has {scraped_posts.count()} scraped posts")
    
    return nike_folder

if __name__ == "__main__":
    test_data_setup()
    nike_folder = create_test_folder_if_needed()
    
    print(f"\n🎯 READY FOR ENDPOINT TESTING!")
    print(f"Test with folder name: '{nike_folder.name}' (ID: {nike_folder.id})")
    print(f"Expected URL: /api/brightdata/data-storage/nike/1/")