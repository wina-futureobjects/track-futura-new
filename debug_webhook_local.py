#!/usr/bin/env python3
"""
Local Webhook Debugging Script for Track-Futura
This script helps debug webhook data flow without deploying to production
"""

import requests
import json
import time
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment for direct database access
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.settings')

# Change to backend directory
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
if os.path.exists(backend_dir):
    os.chdir(backend_dir)
    sys.path.insert(0, backend_dir)

django.setup()

# Now import Django models
from brightdata_integration.models import ScraperRequest, BrightdataConfig
from facebook_data.models import FacebookPost, Folder as FacebookFolder
from instagram_data.models import InstagramPost, Folder as InstagramFolder
from linkedin_data.models import LinkedInPost, Folder as LinkedInFolder
from tiktok_data.models import TikTokPost, Folder as TikTokFolder

class WebhookDebugger:
    def __init__(self):
        self.base_url = 'http://localhost:8000'
        self.webhook_url = f'{self.base_url}/api/brightdata/webhook/'

    def create_test_folders(self):
        """Create test folders for each platform"""
        print("🗂️  Creating test folders...")

        folders = {}

        # Create Facebook folder
        fb_folder, created = FacebookFolder.objects.get_or_create(
            name='Debug_Facebook_Test',
            defaults={'description': 'Test folder for webhook debugging'}
        )
        folders['facebook'] = fb_folder
        print(f"✅ Facebook folder: {fb_folder.name} (ID: {fb_folder.id})")

        # Create Instagram folder
        ig_folder, created = InstagramFolder.objects.get_or_create(
            name='Debug_Instagram_Test',
            defaults={'description': 'Test folder for webhook debugging'}
        )
        folders['instagram'] = ig_folder
        print(f"✅ Instagram folder: {ig_folder.name} (ID: {ig_folder.id})")

        # Create LinkedIn folder
        li_folder, created = LinkedInFolder.objects.get_or_create(
            name='Debug_LinkedIn_Test',
            defaults={'description': 'Test folder for webhook debugging'}
        )
        folders['linkedin'] = li_folder
        print(f"✅ LinkedIn folder: {li_folder.name} (ID: {li_folder.id})")

        # Create TikTok folder
        tt_folder, created = TikTokFolder.objects.get_or_create(
            name='Debug_TikTok_Test',
            defaults={'description': 'Test folder for webhook debugging'}
        )
        folders['tiktok'] = tt_folder
        print(f"✅ TikTok folder: {tt_folder.name} (ID: {tt_folder.id})")

        return folders

    def create_test_scraper_requests(self, folders):
        """Create test scraper requests with folder associations"""
        print("\n📋 Creating test scraper requests...")

        requests_data = {}

        for platform, folder in folders.items():
            # Create a mock scraper request
            scraper_request = ScraperRequest.objects.create(
                platform=platform,
                target_url=f'https://example.com/{platform}',
                request_id=f'debug_{platform}_{int(time.time())}',
                folder_id=folder.id,
                status='processing'
            )
            requests_data[platform] = scraper_request
            print(f"✅ {platform}: Request ID {scraper_request.request_id} → Folder ID {folder.id}")

        return requests_data

    def generate_sample_data(self, platform, request_id):
        """Generate realistic sample data for each platform"""

        if platform == 'facebook':
            return [
                {
                    "url": "https://www.facebook.com/debug/posts/123456789",
                    "post_id": f"debug_fb_{int(time.time())}",
                    "user_url": "https://www.facebook.com/testuser",
                    "user_username_raw": "Test User",
                    "content": "This is a test Facebook post for webhook debugging",
                    "date_posted": datetime.now().isoformat(),
                    "num_comments": 15,
                    "num_shares": 5,
                    "likes": 25,
                    "page_name": "Debug Test Page",
                    "profile_id": "123456789",
                    "page_intro": "Test page for debugging",
                    "page_category": "Software Company",
                    "page_is_verified": True,
                    "post_type": "Post"
                }
            ]

        elif platform == 'instagram':
            return [
                {
                    "url": "https://www.instagram.com/p/debug123/",
                    "post_id": f"debug_ig_{int(time.time())}",
                    "user_posted": "test_user_ig",
                    "description": "This is a test Instagram post for webhook debugging #debug #test",
                    "date_posted": datetime.now().isoformat(),
                    "num_comments": 8,
                    "likes": 42,
                    "shortcode": "debug123",
                    "content_type": "post",
                    "hashtags": ["debug", "test", "webhook"]
                }
            ]

        elif platform == 'linkedin':
            return [
                {
                    "url": "https://www.linkedin.com/feed/update/debug123/",
                    "post_id": f"debug_li_{int(time.time())}",
                    "content": "This is a test LinkedIn post for webhook debugging",
                    "date": datetime.now().isoformat(),
                    "likes": 18,
                    "comments": 6,
                    "shares": 3,
                    "author": "Test LinkedIn User"
                }
            ]

        elif platform == 'tiktok':
            return [
                {
                    "url": "https://www.tiktok.com/@testuser/video/debug123",
                    "post_id": f"debug_tt_{int(time.time())}",
                    "user_posted": "test_tiktok_user",
                    "description": "This is a test TikTok video for webhook debugging",
                    "date_posted": datetime.now().isoformat(),
                    "num_comments": 12,
                    "likes": 156,
                    "content_type": "video"
                }
            ]

        return []

    def send_webhook_data(self, platform, data, request_id):
        """Send webhook data to the local server"""
        print(f"\n📡 Sending webhook data for {platform}...")

        headers = {
            'Content-Type': 'application/json',
            'X-Platform': platform,
            'X-Snapshot-Id': request_id,
            'User-Agent': 'BrightData-Webhook/1.0'
        }

        try:
            print(f"   URL: {self.webhook_url}")
            print(f"   Headers: {headers}")
            print(f"   Data: {json.dumps(data, indent=2)}")

            response = requests.post(
                self.webhook_url,
                json=data,
                headers=headers,
                timeout=30
            )

            print(f"   Response Status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.text

        except Exception as e:
            print(f"   Error: {str(e)}")
            return False, str(e)

    def verify_data_in_folders(self, folders):
        """Check if data was actually saved to the folders"""
        print(f"\n🔍 Verifying data in folders...")

        results = {}

        for platform, folder in folders.items():
            if platform == 'facebook':
                posts = FacebookPost.objects.filter(folder=folder)
            elif platform == 'instagram':
                posts = InstagramPost.objects.filter(folder=folder)
            elif platform == 'linkedin':
                posts = LinkedInPost.objects.filter(folder=folder)
            elif platform == 'tiktok':
                posts = TikTokPost.objects.filter(folder=folder)
            else:
                posts = []

            count = posts.count()
            results[platform] = {
                'folder_id': folder.id,
                'folder_name': folder.name,
                'post_count': count,
                'posts': list(posts.values('post_id', 'content', 'date_posted')[:5])  # First 5 posts
            }

            status = "✅" if count > 0 else "❌"
            print(f"   {status} {platform}: {count} posts in folder '{folder.name}' (ID: {folder.id})")

            if count > 0:
                for post in posts[:3]:  # Show first 3 posts
                    print(f"      - Post ID: {post.post_id}")
                    content = getattr(post, 'content', '') or getattr(post, 'description', '')
                    if content:
                        print(f"        Content: {content[:50]}...")

        return results

    def cleanup_test_data(self):
        """Clean up test data"""
        print(f"\n🧹 Cleaning up test data...")

        # Delete test posts
        FacebookPost.objects.filter(post_id__startswith='debug_fb_').delete()
        InstagramPost.objects.filter(post_id__startswith='debug_ig_').delete()
        LinkedInPost.objects.filter(post_id__startswith='debug_li_').delete()
        TikTokPost.objects.filter(post_id__startswith='debug_tt_').delete()

        # Delete test scraper requests
        ScraperRequest.objects.filter(request_id__startswith='debug_').delete()

        # Delete test folders
        FacebookFolder.objects.filter(name__startswith='Debug_').delete()
        InstagramFolder.objects.filter(name__startswith='Debug_').delete()
        LinkedInFolder.objects.filter(name__startswith='Debug_').delete()
        TikTokFolder.objects.filter(name__startswith='Debug_').delete()

        print("✅ Test data cleaned up")

def main():
    """Run comprehensive webhook debugging"""
    print("🚀 Starting Webhook Debugging Session")
    print("=" * 60)

    debugger = WebhookDebugger()

    try:
        # Step 1: Create test folders
        folders = debugger.create_test_folders()

        # Step 2: Create scraper requests
        scraper_requests = debugger.create_test_scraper_requests(folders)

        # Step 3: Test each platform
        results = {}

        for platform in ['facebook', 'instagram', 'linkedin', 'tiktok']:
            print(f"\n🧪 Testing {platform.upper()} webhook processing...")

            # Generate sample data
            request_id = scraper_requests[platform].request_id
            sample_data = debugger.generate_sample_data(platform, request_id)

            # Send webhook data
            success, response = debugger.send_webhook_data(platform, sample_data, request_id)

            results[platform] = {
                'success': success,
                'response': response,
                'request_id': request_id,
                'folder_id': folders[platform].id
            }

            # Wait a moment for processing
            time.sleep(1)

        # Step 4: Verify data was saved
        verification_results = debugger.verify_data_in_folders(folders)

        # Step 5: Summary
        print(f"\n📊 DEBUGGING SUMMARY")
        print("=" * 60)

        total_tests = len(results)
        successful_webhooks = sum(1 for r in results.values() if r['success'])
        successful_saves = sum(1 for r in verification_results.values() if r['post_count'] > 0)

        print(f"Webhook Calls: {successful_webhooks}/{total_tests} successful")
        print(f"Data Saved: {successful_saves}/{total_tests} platforms saved data")

        for platform, result in results.items():
            webhook_status = "✅" if result['success'] else "❌"
            save_status = "✅" if verification_results[platform]['post_count'] > 0 else "❌"

            print(f"\n{platform.upper()}:")
            print(f"  Webhook: {webhook_status} {result.get('response', 'No response')}")
            print(f"  Data Save: {save_status} {verification_results[platform]['post_count']} posts")
            print(f"  Folder ID: {result['folder_id']}")
            print(f"  Request ID: {result['request_id']}")

        if successful_saves == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! Webhook system is working correctly.")
        else:
            print(f"\n⚠️  ISSUES DETECTED:")
            for platform, verification in verification_results.items():
                if verification['post_count'] == 0:
                    print(f"   - {platform}: No data saved to folder")

        # Ask if user wants to clean up
        cleanup = input(f"\n🧹 Clean up test data? (y/N): ").lower().strip()
        if cleanup in ['y', 'yes']:
            debugger.cleanup_test_data()
        else:
            print("Test data left in database for manual inspection")

    except Exception as e:
        print(f"❌ Error during debugging: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
