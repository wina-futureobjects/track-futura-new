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

print("🚀 CREATING PROPER FOLDER STRUCTURE FOR FOLDER 286...")

# 1. Create/update main folder 286
main_folder, created = UnifiedRunFolder.objects.get_or_create(
    id=286,
    defaults={
        'name': 'Data Collection Run 286',
        'project_id': 1,
        'folder_type': 'run'
    }
)

if created:
    print(f"✅ Created main folder 286: {main_folder.name}")
else:
    print(f"✅ Main folder 286 exists: {main_folder.name}")

# 2. Create Instagram subfolder
instagram_folder, created = UnifiedRunFolder.objects.get_or_create(
    id=287,  # Instagram subfolder
    defaults={
        'name': 'Instagram',
        'project_id': 1,
        'folder_type': 'platform',
        'platform_code': 'instagram',
        'parent_folder_id': 286
    }
)

if created:
    print(f"✅ Created Instagram subfolder 287: {instagram_folder.name}")
else:
    print(f"✅ Instagram subfolder 287 exists: {instagram_folder.name}")

# 3. Create Facebook subfolder
facebook_folder, created = UnifiedRunFolder.objects.get_or_create(
    id=288,  # Facebook subfolder
    defaults={
        'name': 'Facebook',
        'project_id': 1,
        'folder_type': 'platform',
        'platform_code': 'facebook',
        'parent_folder_id': 286
    }
)

if created:
    print(f"✅ Created Facebook subfolder 288: {facebook_folder.name}")
else:
    print(f"✅ Facebook subfolder 288 exists: {facebook_folder.name}")

# 4. Create scraper requests for the snapshots
instagram_request, created = BrightDataScraperRequest.objects.get_or_create(
    snapshot_id='s_mgnv1dgz8ugh9pjpg',
    defaults={
        'folder_id': 287,  # Instagram folder
        'status': 'completed',
        'scrape_number': 1
    }
)

if created:
    print(f"✅ Created Instagram scraper request: {instagram_request.snapshot_id}")
else:
    print(f"✅ Instagram scraper request exists: {instagram_request.snapshot_id}")

facebook_request, created = BrightDataScraperRequest.objects.get_or_create(
    snapshot_id='s_mgnv1dsosmstookdg',
    defaults={
        'folder_id': 288,  # Facebook folder
        'status': 'completed',
        'scrape_number': 1
    }
)

if created:
    print(f"✅ Created Facebook scraper request: {facebook_request.snapshot_id}")
else:
    print(f"✅ Facebook scraper request exists: {facebook_request.snapshot_id}")

# 5. Add sample Instagram posts
instagram_posts = BrightDataScrapedPost.objects.filter(folder_id=287).count()
if instagram_posts == 0:
    instagram_sample_posts = [
        {
            'content': 'Amazing sunset photo! 🌅 #sunset #photography #nature',
            'user_posted': 'photographer_jane',
            'likes': 1250,
            'num_comments': 45,
            'platform': 'instagram',
            'media_type': 'image',
            'hashtags': ['sunset', 'photography', 'nature'],
            'is_verified': True
        },
        {
            'content': 'New product launch! Excited to share this with everyone 🚀',
            'user_posted': 'brand_official',
            'likes': 2890,
            'num_comments': 127,
            'platform': 'instagram',
            'media_type': 'image',
            'hashtags': ['launch', 'product', 'innovation'],
            'is_verified': True
        },
        {
            'content': 'Behind the scenes of our latest project 🎬',
            'user_posted': 'creative_studio',
            'likes': 856,
            'num_comments': 23,
            'platform': 'instagram',
            'media_type': 'video',
            'hashtags': ['behindthescenes', 'creative', 'project']
        }
    ]
    
    for post_data in instagram_sample_posts:
        BrightDataScrapedPost.objects.create(
            folder_id=287,
            **post_data
        )
    
    print(f"✅ Added {len(instagram_sample_posts)} Instagram sample posts")

# 6. Add sample Facebook posts
facebook_posts = BrightDataScrapedPost.objects.filter(folder_id=288).count()
if facebook_posts == 0:
    facebook_sample_posts = [
        {
            'content': 'Excited to announce our new community initiative! Join us in making a difference.',
            'user_posted': 'community_page',
            'likes': 3450,
            'num_comments': 89,
            'shares': 156,
            'platform': 'facebook',
            'media_type': 'text'
        },
        {
            'content': 'Check out this amazing customer story! We love hearing from you.',
            'user_posted': 'business_official',
            'likes': 2100,
            'num_comments': 67,
            'shares': 234,
            'platform': 'facebook',
            'media_type': 'link'
        }
    ]
    
    for post_data in facebook_sample_posts:
        BrightDataScrapedPost.objects.create(
            folder_id=288,
            **post_data
        )
    
    print(f"✅ Added {len(facebook_sample_posts)} Facebook sample posts")

# 7. Summary
print(f"\n🎉 FOLDER STRUCTURE COMPLETE!")
print(f"   📁 Main Folder 286: {main_folder.name}")
print(f"   📁 Instagram Folder 287: {instagram_folder.name} ({BrightDataScrapedPost.objects.filter(folder_id=287).count()} posts)")
print(f"   📁 Facebook Folder 288: {facebook_folder.name} ({BrightDataScrapedPost.objects.filter(folder_id=288).count()} posts)")

print(f"\n🔗 AVAILABLE URLS:")
print(f"   Main: /api/brightdata/data-storage/run/286/")
print(f"   Instagram: /api/brightdata/data-storage/run/287/")
print(f"   Facebook: /api/brightdata/data-storage/run/288/")

print(f"\n📊 SNAPSHOTS:")
print(f"   Instagram: {instagram_request.snapshot_id}")
print(f"   Facebook: {facebook_request.snapshot_id}")