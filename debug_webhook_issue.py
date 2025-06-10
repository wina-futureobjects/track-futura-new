#!/usr/bin/env python3
"""
Debug script to identify why Instagram posts aren't being created during webhook processing
"""

import os
import sys
import json

# Add Django project to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from instagram_data.models import Folder, InstagramPost
from brightdata_integration.models import ScraperRequest, BrightdataNotification, BrightdataConfig
from brightdata_integration.views import _process_webhook_data, _map_post_fields

def debug_webhook_processing():
    """Debug the webhook processing step by step"""

    print("🔍 DEBUGGING WEBHOOK PROCESSING")
    print("=" * 50)

    # Sample data from user's example
    sample_post = {
        "url": "https://www.instagram.com/p/DKkbTWvJC37",
        "user_posted": "skybarauburnal",
        "description": "FRIDAY NIGHT - 7PM\n\nFRONT • BACK • BEER GARDEN",
        "hashtags": None,
        "num_comments": 1,
        "date_posted": "2025-06-06T18:19:52.000Z",
        "likes": 445,
        "photos": ["https://example.com/photo.jpg"],
        "videos": None,
        "post_id": "3649161675416022523",
        "shortcode": "DKkbTWvJC37",
        "content_type": "Carousel",
        "pk": "3649161675416022523",
        "content_id": "DKkbTWvJC37",
        "followers": 23959,
        "posts_count": 1922,
        "is_verified": False,
        "user_posted_id": "1938739694"
    }

    # Create test folder
    test_folder, created = Folder.objects.get_or_create(
        name="Debug Test Folder",
        defaults={"description": "Debug test folder"}
    )
    print(f"📁 Test folder: {test_folder.name} (ID: {test_folder.id})")

    # Create config and scraper request
    config, created = BrightdataConfig.objects.get_or_create(
        platform='instagram_posts',
        defaults={'name': 'Debug Config', 'dataset_id': 'debug', 'is_active': True}
    )

    scraper_request = ScraperRequest.objects.create(
        config=config,
        platform='instagram_posts',
        content_type='post',
        target_url='https://www.instagram.com/skybarauburnal/',
        folder_id=test_folder.id,
        status='processing'
    )
    print(f"📋 Created scraper request: ID {scraper_request.id}")

    # Test field mapping
    print(f"\n🗂️  TESTING FIELD MAPPING")
    mapped_fields = _map_post_fields(sample_post, 'instagram')
    print(f"Mapped fields:")
    for key, value in mapped_fields.items():
        print(f"  • {key}: {value}")

    # Test webhook data processing
    print(f"\n🌐 TESTING WEBHOOK DATA PROCESSING")
    initial_count = InstagramPost.objects.filter(folder=test_folder).count()
    print(f"Initial post count: {initial_count}")

    # Manually call the processing function
    try:
        result = _process_webhook_data([sample_post], 'instagram', scraper_request)
        print(f"Processing result: {result}")
    except Exception as e:
        print(f"❌ Error in processing: {str(e)}")
        import traceback
        traceback.print_exc()

    # Check if post was created
    final_count = InstagramPost.objects.filter(folder=test_folder).count()
    print(f"Final post count: {final_count}")
    print(f"Posts created: {final_count - initial_count}")

    if final_count > initial_count:
        latest_post = InstagramPost.objects.filter(folder=test_folder).last()
        print(f"\n✅ Post created successfully:")
        print(f"  • URL: {latest_post.url}")
        print(f"  • User: {latest_post.user_posted}")
        print(f"  • Likes: {latest_post.likes}")
        print(f"  • Folder: {latest_post.folder.name}")
    else:
        print(f"\n❌ No posts were created")

        # Check if there are any posts at all
        all_posts = InstagramPost.objects.all()
        print(f"Total posts in database: {all_posts.count()}")

        if all_posts.count() > 0:
            recent_post = all_posts.last()
            print(f"Most recent post: {recent_post.url} in folder {recent_post.folder}")

def check_database_state():
    """Check the current state of the database"""
    print(f"\n📊 DATABASE STATE CHECK")
    print("=" * 30)

    folders = Folder.objects.all()
    print(f"Total folders: {folders.count()}")
    for folder in folders:
        posts_count = InstagramPost.objects.filter(folder=folder).count()
        print(f"  • {folder.name}: {posts_count} posts")

    scraper_requests = ScraperRequest.objects.all()
    print(f"\nTotal scraper requests: {scraper_requests.count()}")
    for req in scraper_requests.order_by('-id')[:5]:
        print(f"  • ID {req.id}: {req.platform} -> folder {req.folder_id} (status: {req.status})")

def main():
    """Run the debug process"""
    try:
        check_database_state()
        debug_webhook_processing()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
