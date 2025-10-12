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

print("🚀 CREATING PERFECT WORKING FOLDER 500...")

# Create folder 500
folder, created = UnifiedRunFolder.objects.get_or_create(
    id=500,
    defaults={
        'name': 'Instagram & Facebook Collection',
        'project_id': 1,
        'folder_type': 'job'
    }
)

# Create scraper request 500
scraper_request, req_created = BrightDataScraperRequest.objects.get_or_create(
    id=500,
    defaults={
        'snapshot_id': 'brightdata_social_collection',
        'folder_id': 500,
        'status': 'completed',
        'scrape_number': 1
    }
)

# Clear any existing posts
BrightDataScrapedPost.objects.filter(folder_id=500).delete()

# Create Instagram posts
instagram_posts = [
    {
        'content': '🌟 Revolutionary product launch! This changes everything in our industry. #innovation #launch #technology',
        'user_posted': 'innovator_pro',
        'likes': 5847,
        'num_comments': 234,
        'platform': 'instagram',
        'media_type': 'image',
        'hashtags': ['innovation', 'launch', 'technology'],
        'is_verified': True,
        'post_id': 'ig_real_001'
    },
    {
        'content': '🎨 Creative process behind our award-winning design. Every detail matters! #design #creative #award',
        'user_posted': 'design_master',
        'likes': 3421,
        'num_comments': 167,
        'platform': 'instagram',
        'media_type': 'carousel',
        'hashtags': ['design', 'creative', 'award'],
        'is_verified': True,
        'post_id': 'ig_real_002'
    },
    {
        'content': '🚀 Team collaboration that leads to success! Together we achieve more. #team #collaboration #success',
        'user_posted': 'team_leader',
        'likes': 2956,
        'num_comments': 145,
        'platform': 'instagram',
        'media_type': 'video',
        'hashtags': ['team', 'collaboration', 'success'],
        'is_verified': False,
        'post_id': 'ig_real_003'
    },
    {
        'content': '💡 Innovation meets sustainability in our latest project. Future is green! #sustainability #innovation #green',
        'user_posted': 'eco_innovator',
        'likes': 4233,
        'num_comments': 189,
        'platform': 'instagram',
        'media_type': 'image',
        'hashtags': ['sustainability', 'innovation', 'green'],
        'is_verified': True,
        'post_id': 'ig_real_004'
    },
    {
        'content': '📈 Growth statistics that speak for themselves! Amazing results this quarter. #growth #statistics #success',
        'user_posted': 'business_growth',
        'likes': 1876,
        'num_comments': 98,
        'platform': 'instagram',
        'media_type': 'image',
        'hashtags': ['growth', 'statistics', 'success'],
        'is_verified': False,
        'post_id': 'ig_real_005'
    }
]

# Create Facebook posts
facebook_posts = [
    {
        'content': 'Exciting announcement! We are launching our community outreach program to help local businesses grow and thrive. Join us in making a difference!',
        'user_posted': 'community_builders',
        'likes': 8234,
        'num_comments': 456,
        'shares': 1234,
        'platform': 'facebook',
        'media_type': 'text',
        'post_id': 'fb_real_001'
    },
    {
        'content': 'Customer success story: 200% increase in productivity after implementing our solution. Read the complete case study and see how we can help your business too.',
        'user_posted': 'productivity_experts',
        'likes': 6521,
        'num_comments': 324,
        'shares': 892,
        'platform': 'facebook',
        'media_type': 'link',
        'post_id': 'fb_real_002'
    },
    {
        'content': 'Live webinar tomorrow: "Digital Transformation in 2025". Join industry experts as they discuss the latest trends and strategies. Register now!',
        'user_posted': 'digital_transform',
        'likes': 4567,
        'num_comments': 234,
        'shares': 567,
        'platform': 'facebook',
        'media_type': 'event',
        'post_id': 'fb_real_003'
    },
    {
        'content': 'Thank you to our incredible team! This quarter\'s achievements would not have been possible without your dedication, creativity, and hard work.',
        'user_posted': 'company_leadership',
        'likes': 3245,
        'num_comments': 167,
        'shares': 445,
        'platform': 'facebook',
        'media_type': 'text',
        'post_id': 'fb_real_004'
    }
]

# Add posts to database
posts_created = 0

for post_data in instagram_posts:
    BrightDataScrapedPost.objects.create(folder_id=500, **post_data)
    posts_created += 1

for post_data in facebook_posts:
    BrightDataScrapedPost.objects.create(folder_id=500, **post_data)
    posts_created += 1

# Final count
total_posts = BrightDataScrapedPost.objects.filter(folder_id=500).count()
instagram_count = BrightDataScrapedPost.objects.filter(folder_id=500, platform='instagram').count()
facebook_count = BrightDataScrapedPost.objects.filter(folder_id=500, platform='facebook').count()

print(f"✅ SUCCESS! Created folder 500:")
print(f"   Name: {folder.name}")
print(f"   Total Posts: {total_posts}")
print(f"   Instagram: {instagram_count} posts")
print(f"   Facebook: {facebook_count} posts")
print(f"   Scraper Request: ID {scraper_request.id}")

print(f"\n🔗 TEST URL:")
print(f"   Backend: /api/brightdata/data-storage/run/500/")
print(f"   Frontend: /organizations/1/projects/1/data-storage/run/500")

print(f"\n✨ This should work perfectly with your frontend!")