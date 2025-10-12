#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder
from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest

print("🚀 CREATING FOLDER 286 AND SAMPLE DATA...")

try:
    # Create folder 286
    folder, created = UnifiedRunFolder.objects.get_or_create(
        id=286,
        defaults={
            'name': 'Emergency Folder 286',
            'project_id': 1,
            'folder_type': 'job'
        }
    )
    
    if created:
        print(f"✅ Created folder 286: {folder.name}")
    else:
        print(f"✅ Folder 286 already exists: {folder.name}")
    
    # Create scraper request 286
    scraper_request, created = BrightDataScraperRequest.objects.get_or_create(
        id=286,
        defaults={
            'snapshot_id': 'emergency_286',
            'folder_id': 286,
            'status': 'completed',
            'scrape_number': 1
        }
    )
    
    if created:
        print(f"✅ Created scraper request 286")
    else:
        print(f"✅ Scraper request 286 already exists")
    
    # Add some sample posts to folder 286 if empty
    existing_posts = BrightDataScrapedPost.objects.filter(folder_id=286).count()
    if existing_posts == 0:
        # Create a few sample posts
        sample_posts = [
            {
                'content': 'Sample post 1 for folder 286 testing',
                'user_posted': 'test_user_1',
                'likes': 100,
                'platform': 'instagram'
            },
            {
                'content': 'Sample post 2 for folder 286 testing',
                'user_posted': 'test_user_2', 
                'likes': 200,
                'platform': 'instagram'
            },
            {
                'content': 'Sample post 3 for folder 286 testing',
                'user_posted': 'test_user_3',
                'likes': 300,
                'platform': 'instagram'
            }
        ]
        
        for post_data in sample_posts:
            post = BrightDataScrapedPost.objects.create(
                folder_id=286,
                **post_data
            )
        
        print(f"✅ Created 3 sample posts in folder 286")
    else:
        print(f"✅ Folder 286 already has {existing_posts} posts")
    
    print(f"\n🎉 SUCCESS! Folder 286 is ready!")
    print(f"   URL: /api/brightdata/data-storage/run/286/")
    print(f"   Folder: {folder.name}")
    print(f"   Posts: {BrightDataScrapedPost.objects.filter(folder_id=286).count()}")

except Exception as e:
    print(f"❌ Error creating folder 286: {e}")
    import traceback
    traceback.print_exc()