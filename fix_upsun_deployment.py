#!/usr/bin/env python3
"""
Fix Upsun Deployment Issues
Based on debugging results, this script addresses the specific problems found
"""

import requests
import json
import time
from datetime import datetime

# Correct Upsun webhook URL from testing
UPSUN_WEBHOOK_URL = "https://upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/"

def test_direct_webhook_fix():
    """Test webhook with corrected headers and authentication"""
    print("🔧 TESTING WEBHOOK WITH AUTHENTICATION FIX")
    print("=" * 60)

    # Test with proper authentication header
    sample_data = [
        {
            "url": "https://www.instagram.com/p/test_fix_46/",
            "post_id": f"fix_test_{int(time.time())}",
            "user_posted": "test_folder_46",
            "description": "🛠️ FIXING: Testing webhook fix for folder 46 assignment",
            "date_posted": datetime.now().isoformat(),
            "num_comments": 1,
            "likes": 5,
            "shortcode": "test_fix_46",
            "content_type": "post"
        }
    ]

    # Test different authentication approaches
    auth_tests = [
        {
            "name": "No Authentication",
            "headers": {
                'Content-Type': 'application/json',
                'X-Platform': 'instagram',
                'X-Snapshot-Id': f'folder_46_test_{int(time.time())}',
                'User-Agent': 'BrightData-Webhook/1.0'
            }
        },
        {
            "name": "Bearer Token",
            "headers": {
                'Content-Type': 'application/json',
                'X-Platform': 'instagram',
                'X-Snapshot-Id': f'folder_46_test_{int(time.time())}',
                'Authorization': 'Bearer your-webhook-token-here',
                'User-Agent': 'BrightData-Webhook/1.0'
            }
        },
        {
            "name": "X-Webhook-Token",
            "headers": {
                'Content-Type': 'application/json',
                'X-Platform': 'instagram',
                'X-Snapshot-Id': f'folder_46_test_{int(time.time())}',
                'X-Webhook-Token': 'your-webhook-token-here',
                'User-Agent': 'BrightData-Webhook/1.0'
            }
        }
    ]

    for auth_test in auth_tests:
        print(f"\n🔑 Testing: {auth_test['name']}")
        print(f"   Headers: {json.dumps(auth_test['headers'], indent=2)}")

        try:
            response = requests.post(
                UPSUN_WEBHOOK_URL,
                json=sample_data,
                headers=auth_test['headers'],
                timeout=30
            )

            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:300]}...")

            if response.status_code == 200:
                print(f"   ✅ SUCCESS! This authentication works")
                return auth_test['headers']
            elif response.status_code == 500:
                print(f"   ❌ Server error - Django issue on Upsun")
            elif response.status_code == 401:
                print(f"   ❌ Authentication failed")
            elif response.status_code == 403:
                print(f"   ❌ Forbidden")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

    return None

def check_upsun_environment_vars():
    """Check what environment variables might be missing on Upsun"""
    print(f"\n🌍 UPSUN ENVIRONMENT VARIABLES CHECK")
    print("=" * 60)

    print("These environment variables MUST be set on Upsun:")
    print()
    print("1. 🔑 BRIGHTDATA_WEBHOOK_TOKEN")
    print("   - Set this in Upsun dashboard: Variables section")
    print("   - Use the same token you configure in BrightData")
    print("   - Command: upsun variable:set BRIGHTDATA_WEBHOOK_TOKEN your_token_here")
    print()
    print("2. 🗄️  DATABASE_URL")
    print("   - Should be auto-configured by Upsun")
    print("   - If using external database, set manually")
    print()
    print("3. 🔐 DJANGO_SECRET_KEY")
    print("   - Critical for Django security")
    print("   - Command: upsun variable:set DJANGO_SECRET_KEY your_secret_key")
    print()
    print("4. 🚀 DEBUG")
    print("   - Should be False in production")
    print("   - Command: upsun variable:set DEBUG false")
    print()
    print("5. 🌐 ALLOWED_HOSTS")
    print("   - Should include your Upsun domain")
    print("   - Command: upsun variable:set ALLOWED_HOSTS 'upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site'")

def create_manual_scraper_request():
    """Create the missing ScraperRequest for folder 46"""
    print(f"\n🔧 MANUAL SCRAPER REQUEST CREATION")
    print("=" * 60)

    print("Since your webhook is failing, create ScraperRequest manually:")
    print()
    print("1. 🖥️  SSH into your Upsun environment:")
    print("   upsun ssh")
    print()
    print("2. 🐍 Access Django shell:")
    print("   cd /app && python manage.py shell")
    print()
    print("3. 📝 Run this Python code:")
    print("""
from brightdata_integration.models import ScraperRequest, BrightdataConfig
from instagram_data.models import Folder

# Get your folder 46
folder = Folder.objects.get(id=46)
print(f"Folder: {folder.name}")

# Get BrightData config (you need the config_id)
config = BrightdataConfig.objects.first()
if not config:
    print("❌ No BrightData config found! Create one first.")
else:
    # Create ScraperRequest with your actual BrightData job ID
    scraper_request = ScraperRequest.objects.create(
        config=config,
        folder=folder,
        request_id="YOUR_ACTUAL_BRIGHTDATA_JOB_ID",  # Replace with real job ID
        platform="instagram",
        status="completed"
    )
    print(f"✅ Created ScraperRequest: {scraper_request.id}")
    print(f"   Request ID: {scraper_request.request_id}")
    print(f"   Folder: {scraper_request.folder.name}")
""")
    print()
    print("4. 🎯 Replace 'YOUR_ACTUAL_BRIGHTDATA_JOB_ID' with your real BrightData job ID")
    print("   - Find this in your BrightData dashboard")
    print("   - Look for the job that scraped data for folder 46")

def provide_curl_test():
    """Provide curl command to test webhook directly"""
    print(f"\n🌐 DIRECT WEBHOOK TEST WITH CURL")
    print("=" * 60)

    test_data = {
        "url": "https://www.instagram.com/p/curl_test_46/",
        "post_id": f"curl_test_{int(time.time())}",
        "user_posted": "curl_test_user",
        "description": "🧪 CURL TEST: Direct webhook test for folder 46",
        "date_posted": datetime.now().isoformat(),
        "num_comments": 0,
        "likes": 1,
        "shortcode": "curl_test_46",
        "content_type": "post"
    }

    curl_command = f'''curl -X POST "{UPSUN_WEBHOOK_URL}" \\
  -H "Content-Type: application/json" \\
  -H "X-Platform: instagram" \\
  -H "X-Snapshot-Id: folder_46_test_{int(time.time())}" \\
  -H "User-Agent: BrightData-Webhook/1.0" \\
  -d '{json.dumps([test_data], indent=2)}\''''

    print("Run this curl command to test webhook directly:")
    print()
    print(curl_command)
    print()
    print("Expected responses:")
    print("✅ 200 OK: Webhook working correctly")
    print("❌ 500 Error: Django configuration issue")
    print("❌ 401/403: Authentication problem")
    print("❌ 404: Wrong URL or routing issue")

def main():
    print("🛠️  UPSUN DEPLOYMENT FIX")
    print("=" * 70)

    print("Based on debugging, here are the issues and fixes:")
    print()

    # Test webhook with authentication
    working_headers = test_direct_webhook_fix()

    # Check environment variables
    check_upsun_environment_vars()

    # Manual ScraperRequest creation
    create_manual_scraper_request()

    # Curl test
    provide_curl_test()

    print(f"\n🎯 IMMEDIATE ACTION ITEMS:")
    print("=" * 70)
    print("1. ⚡ URGENT: Check Upsun logs right now:")
    print("   upsun log --app backend --tail")
    print()
    print("2. 🔑 Set missing environment variables on Upsun")
    print("3. 🧪 Test webhook with curl command above")
    print("4. 📝 Create manual ScraperRequest for folder 46")
    print("5. 🔍 Verify BrightData webhook URL configuration")
    print()
    print("⚠️  The webhook URL returns 500 errors - this is a Django config issue!")
    print("   Check Django logs on Upsun for the exact error details.")

if __name__ == "__main__":
    main()
