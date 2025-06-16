#!/usr/bin/env python3
"""
Debug script for Upsun production webhook issues with exact BrightData JSON structure
"""

import json
import os
import sys

# Add Django project to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

def analyze_brightdata_json():
    """Analyze the provided BrightData JSON structure"""

    print("🔍 ANALYZING BRIGHTDATA JSON STRUCTURE")
    print("=" * 60)

    # Load the actual JSON file
    try:
        with open('bd_20250616_040447_0.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ JSON file not found")
        return
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return

    print(f"📊 Total entries in JSON: {len(data)}")

    # Analyze entry types
    warning_entries = []
    valid_posts = []

    for i, entry in enumerate(data):
        if 'warning' in entry or 'warning_code' in entry:
            warning_entries.append(entry)
            print(f"⚠️  Warning entry {i+1}: {entry.get('warning', 'Unknown warning')}")
        else:
            # Check if it's a valid post
            if 'url' in entry and 'user_posted' in entry:
                valid_posts.append(entry)
                print(f"✅ Valid post {i+1}: {entry.get('url', 'No URL')}")
            else:
                print(f"❓ Unknown entry type {i+1}: {list(entry.keys())}")

    print(f"\n📈 ANALYSIS SUMMARY:")
    print(f"   • Warning entries: {len(warning_entries)}")
    print(f"   • Valid posts: {len(valid_posts)}")
    print(f"   • Total entries: {len(data)}")

    # Check structure of first valid post
    if valid_posts:
        print(f"\n🔍 FIRST VALID POST STRUCTURE:")
        first_post = valid_posts[0]
        print(f"   • URL: {first_post.get('url')}")
        print(f"   • User: {first_post.get('user_posted')}")
        print(f"   • Description: {first_post.get('description', '')[:100]}...")
        print(f"   • Date: {first_post.get('date_posted')}")
        print(f"   • Has input field: {'input' in first_post}")
        print(f"   • Has discovery_input: {'discovery_input' in first_post}")
        print(f"   • Content type: {first_post.get('content_type')}")

    return {
        'total_entries': len(data),
        'warning_entries': len(warning_entries),
        'valid_posts': len(valid_posts),
        'data': data,
        'warnings': warning_entries,
        'posts': valid_posts
    }

def test_webhook_processing():
    """Test the webhook processing with the actual data"""

    analysis = analyze_brightdata_json()
    if not analysis:
        return False

    print(f"\n🧪 TESTING WEBHOOK PROCESSING")
    print("=" * 60)

    # Import required modules
    from instagram_data.models import Folder, InstagramPost
    from brightdata_integration.models import ScraperRequest, BrightdataConfig
    from brightdata_integration.views import _process_webhook_data

    # Create test folder
    test_folder, created = Folder.objects.get_or_create(
        name="Production Debug Test",
        defaults={"description": "Debug test folder for production issues"}
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
        target_url='https://www.instagram.com/sgcarmart',
        folder_id=test_folder.id,
        status='processing'
    )
    print(f"📋 Created scraper request: ID {scraper_request.id}")

    # Count initial posts
    initial_count = InstagramPost.objects.filter(folder=test_folder).count()
    print(f"📊 Initial post count: {initial_count}")

    # Test processing with full data (including warnings)
    print(f"\n🔄 TESTING WITH FULL DATA (including warnings)")
    try:
        result = _process_webhook_data(analysis['data'], 'instagram', scraper_request)
        print(f"📋 Processing result: {result}")
    except Exception as e:
        print(f"❌ Error processing full data: {str(e)}")
        import traceback
        traceback.print_exc()

    # Test processing with only valid posts
    print(f"\n🔄 TESTING WITH VALID POSTS ONLY")
    try:
        result = _process_webhook_data(analysis['posts'], 'instagram', scraper_request)
        print(f"📋 Processing result: {result}")
    except Exception as e:
        print(f"❌ Error processing valid posts: {str(e)}")
        import traceback
        traceback.print_exc()

    # Check final post count
    final_count = InstagramPost.objects.filter(folder=test_folder).count()
    posts_created = final_count - initial_count
    print(f"\n📈 FINAL RESULTS:")
    print(f"   • Initial posts: {initial_count}")
    print(f"   • Final posts: {final_count}")
    print(f"   • Posts created: {posts_created}")

    return posts_created > 0

if __name__ == "__main__":
    test_webhook_processing()
