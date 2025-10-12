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

print("🚀 CREATING CORRECT FOLDER STRUCTURE FOR PRODUCTION...")

# 1. Clear test data from folder 286
test_posts = BrightDataScrapedPost.objects.filter(
    folder_id=286,
    content__icontains='Emergency sample post'
)
deleted_count = test_posts.count()
test_posts.delete()
print(f"✅ Removed {deleted_count} test posts from folder 286")

# 2. Update folder 286 to be a selection folder
try:
    main_folder = UnifiedRunFolder.objects.get(id=286)
    main_folder.name = 'Social Media Data Collection'
    main_folder.folder_type = 'run'
    main_folder.save()
    print(f"✅ Updated folder 286: {main_folder.name}")
except UnifiedRunFolder.DoesNotExist:
    print("❌ Folder 286 not found")
    
# 3. Create Instagram folder 103 and link real data
instagram_folder, ig_created = UnifiedRunFolder.objects.get_or_create(
    id=103,
    defaults={
        'name': 'Instagram Posts',
        'project_id': 1,
        'folder_type': 'platform',
        'platform_code': 'instagram',
        'parent_folder_id': 286
    }
)
print(f"✅ Instagram folder 103: {instagram_folder.name} ({'created' if ig_created else 'exists'})")

# 4. Create Facebook folder 104 and link real data  
facebook_folder, fb_created = UnifiedRunFolder.objects.get_or_create(
    id=104,
    defaults={
        'name': 'Facebook Posts',
        'project_id': 1,
        'folder_type': 'platform',
        'platform_code': 'facebook',
        'parent_folder_id': 286
    }
)
print(f"✅ Facebook folder 104: {facebook_folder.name} ({'created' if fb_created else 'exists'})")

# 5. Update scraper requests to point to correct folders
try:
    instagram_request = BrightDataScraperRequest.objects.get(snapshot_id='s_mgnv1dgz8ugh9pjpg')
    instagram_request.folder_id = 103
    instagram_request.status = 'completed'
    instagram_request.save()
    print(f"✅ Updated Instagram scraper request to folder 103")
except BrightDataScraperRequest.DoesNotExist:
    print("❌ Instagram scraper request not found")

try:
    facebook_request = BrightDataScraperRequest.objects.get(snapshot_id='s_mgnv1dsosmstookdg') 
    facebook_request.folder_id = 104
    facebook_request.status = 'completed'
    facebook_request.save()
    print(f"✅ Updated Facebook scraper request to folder 104")
except BrightDataScraperRequest.DoesNotExist:
    print("❌ Facebook scraper request not found")

# 6. Check final structure
instagram_posts = BrightDataScrapedPost.objects.filter(folder_id=103).count()
facebook_posts = BrightDataScrapedPost.objects.filter(folder_id=104).count()
main_posts = BrightDataScrapedPost.objects.filter(folder_id=286).count()

print(f"\n📊 FINAL STRUCTURE:")
print(f"   Main Folder 286: {main_posts} posts (should be 0 - selection only)")
print(f"   Instagram Folder 103: {instagram_posts} posts") 
print(f"   Facebook Folder 104: {facebook_posts} posts")

print(f"\n🔗 PRODUCTION URLS:")
print(f"   Platform Selection: /api/brightdata/data-storage/run/286/")
print(f"   Instagram Data: /api/brightdata/data-storage/run/103/")
print(f"   Facebook Data: /api/brightdata/data-storage/run/104/")

print(f"\n✨ Ready for production testing!")