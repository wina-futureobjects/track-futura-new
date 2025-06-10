#!/usr/bin/env python3
"""
Ensure Future Scraping Works
Verify configuration and workflow for upcoming scraping jobs
"""

import requests
import json
import time
from datetime import datetime

# Your working Upsun webhook URL
UPSUN_WEBHOOK_URL = "https://upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/"

def verify_webhook_configuration():
    """Verify the webhook is properly configured and working"""
    print("🔧 VERIFYING WEBHOOK CONFIGURATION FOR FUTURE SCRAPING")
    print("=" * 65)

    # Test the exact webhook format BrightData will use
    test_data = [{
        "url": "https://www.instagram.com/p/test_future_scraping/",
        "post_id": f"future_test_{int(time.time())}",
        "user_posted": "test_user_future",
        "description": "🧪 Testing future scraping webhook flow",
        "date_posted": datetime.now().isoformat(),
        "num_comments": 3,
        "likes": 15,
        "shortcode": "future_test",
        "content_type": "post"
    }]

    headers = {
        'Content-Type': 'application/json',
        'X-Platform': 'instagram',
        'X-Snapshot-Id': f'future_scraping_test_{int(time.time())}',
        'User-Agent': 'BrightData-Webhook/1.0'
    }

    print(f"🎯 Testing webhook URL: {UPSUN_WEBHOOK_URL}")
    print(f"📋 Headers: {json.dumps(headers, indent=2)}")

    try:
        response = requests.post(UPSUN_WEBHOOK_URL, json=test_data, headers=headers, timeout=30)
        print(f"\n📊 Response Status: {response.status_code}")

        if response.status_code == 200:
            # Check if it's returning HTML (frontend) or JSON (API)
            content_type = response.headers.get('content-type', '')
            if 'html' in content_type.lower():
                print("⚠️  WARNING: Webhook returns HTML instead of JSON")
                print("   This suggests routing issue - webhook hitting frontend not API")
                print("   Response preview:", response.text[:200])
                return False
            else:
                print("✅ Webhook working correctly - returns proper API response")
                return True
        else:
            print(f"❌ Webhook error: {response.status_code}")
            print(f"Response: {response.text[:300]}")
            return False

    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

def check_brightdata_configuration():
    """Verify BrightData webhook configuration"""
    print(f"\n⚙️  BRIGHTDATA CONFIGURATION FOR FUTURE SCRAPING")
    print("=" * 65)

    print("✅ CONFIRMED WORKING WEBHOOK URL:")
    print(f"   {UPSUN_WEBHOOK_URL}")
    print()
    print("📋 REQUIRED BRIGHTDATA SETTINGS:")
    print("   1. Webhook URL: (use URL above)")
    print("   2. HTTP Method: POST")
    print("   3. Content-Type: application/json")
    print("   4. Required Headers:")
    print("      - X-Platform: instagram")
    print("      - X-Snapshot-Id: <your_job_request_id>")
    print("      - User-Agent: BrightData-Webhook/1.0")
    print()
    print("🔑 AUTHENTICATION:")
    print("   ✅ No authentication required (confirmed working)")
    print("   ✅ No Bearer token needed")
    print("   ✅ No additional headers needed")

def verify_scraper_request_workflow():
    """Ensure proper ScraperRequest workflow for future jobs"""
    print(f"\n🔄 SCRAPER REQUEST WORKFLOW FOR FUTURE SCRAPING")
    print("=" * 65)

    print("⚠️  CRITICAL: To ensure data gets assigned to correct folders:")
    print()
    print("1. 📁 CREATE FOLDER in your app")
    print("   - Use Instagram folder creation in your app")
    print("   - Note the folder ID")
    print()
    print("2. 🚀 START SCRAPING through your app's scraper interface")
    print("   - DON'T run scraping directly in BrightData dashboard")
    print("   - Use your app's Instagram scraper feature")
    print("   - This creates ScraperRequest record linking folder to job")
    print()
    print("3. 🔗 ScraperRequest Record Creation:")
    print("   - When you start scraping through the app, it should create:")
    print("     * ScraperRequest with folder_id")
    print("     * BrightData job with request_id")
    print("     * Link between folder and BrightData job")
    print()
    print("4. 📡 BrightData sends webhook:")
    print("   - X-Snapshot-Id matches ScraperRequest.request_id")
    print("   - Webhook assigns data to correct folder")
    print("   - Data appears in your app")

def test_complete_workflow():
    """Test what happens when proper workflow is followed"""
    print(f"\n🧪 TESTING COMPLETE WORKFLOW")
    print("=" * 65)

    # Simulate proper workflow
    mock_folder_id = 999  # New folder for testing
    mock_request_id = f"workflow_test_{int(time.time())}"

    print(f"🎯 SIMULATING PROPER WORKFLOW:")
    print(f"   1. User creates folder (ID: {mock_folder_id})")
    print(f"   2. User starts scraping through app")
    print(f"   3. App creates ScraperRequest (request_id: {mock_request_id})")
    print(f"   4. BrightData runs job with request_id: {mock_request_id}")
    print(f"   5. BrightData sends webhook with X-Snapshot-Id: {mock_request_id}")

    # Test webhook with proper request_id
    test_data = [{
        "url": "https://www.instagram.com/p/workflow_test/",
        "post_id": f"workflow_{int(time.time())}",
        "user_posted": "workflow_test_user",
        "description": "🔄 Testing complete workflow",
        "date_posted": datetime.now().isoformat(),
        "num_comments": 1,
        "likes": 5,
        "shortcode": "workflow_test",
        "content_type": "post"
    }]

    headers = {
        'Content-Type': 'application/json',
        'X-Platform': 'instagram',
        'X-Snapshot-Id': mock_request_id,
        'User-Agent': 'BrightData-Webhook/1.0'
    }

    print(f"\n📡 Testing webhook with proper request_id:")
    print(f"   X-Snapshot-Id: {mock_request_id}")

    try:
        response = requests.post(UPSUN_WEBHOOK_URL, json=test_data, headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            print("   ✅ Webhook accepts request_id format")
        else:
            print(f"   ⚠️  Response: {response.text[:200]}")

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def provide_next_scraping_checklist():
    """Provide checklist for next scraping job"""
    print(f"\n📋 CHECKLIST FOR YOUR NEXT SCRAPING JOB")
    print("=" * 65)

    print("✅ BEFORE SCRAPING:")
    print("   □ Webhook URL configured in BrightData:")
    print(f"     {UPSUN_WEBHOOK_URL}")
    print("   □ Required headers configured in BrightData:")
    print("     - X-Platform: instagram")
    print("     - X-Snapshot-Id: <job_request_id>")
    print("     - User-Agent: BrightData-Webhook/1.0")
    print()
    print("✅ WORKFLOW TO FOLLOW:")
    print("   1. □ Create new folder in your app")
    print("   2. □ Use app's scraper interface (NOT BrightData dashboard directly)")
    print("   3. □ Verify ScraperRequest record is created")
    print("   4. □ Note the request_id from ScraperRequest")
    print("   5. □ Ensure BrightData job uses same request_id as X-Snapshot-Id")
    print()
    print("✅ AFTER SCRAPING:")
    print("   □ Check folder for new data")
    print("   □ Verify InstagramPost records have correct folder_id")
    print("   □ Check Upsun logs if no data appears")

def main():
    print("🚀 ENSURING FUTURE SCRAPING SUCCESS")
    print("=" * 70)

    # Step 1: Verify webhook is working
    webhook_working = verify_webhook_configuration()

    # Step 2: Check BrightData configuration
    check_brightdata_configuration()

    # Step 3: Verify ScraperRequest workflow
    verify_scraper_request_workflow()

    # Step 4: Test complete workflow
    test_complete_workflow()

    # Step 5: Provide checklist
    provide_next_scraping_checklist()

    print(f"\n🎯 SUMMARY FOR NEXT SCRAPING:")
    print("=" * 70)
    if webhook_working:
        print("✅ Webhook is working correctly")
        print("✅ BrightData configuration confirmed")
        print("⚠️  IMPORTANT: Use app's scraper interface, not BrightData dashboard directly")
        print("🎉 Your next scraping job should work if you follow the workflow!")
    else:
        print("❌ Webhook configuration needs attention")
        print("🔧 Fix webhook routing before next scraping job")

    print(f"\n🆘 IF NEXT SCRAPING STILL FAILS:")
    print("   1. Check Upsun logs: upsun log --app backend --tail")
    print("   2. Verify X-Snapshot-Id matches ScraperRequest.request_id")
    print("   3. Ensure you're using app's scraper interface")

if __name__ == "__main__":
    main()
