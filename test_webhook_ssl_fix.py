#!/usr/bin/env python3
"""
Test webhook with SSL verification disabled to work around connection issues
"""

import requests
import json
import time
from datetime import datetime
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_webhook_no_ssl_verify():
    """Send sample Instagram data to webhook with SSL verification disabled"""

    print("🧪 TESTING WEBHOOK (SSL VERIFICATION DISABLED)")
    print("=" * 60)

    # Live webhook URL
    webhook_url = "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/"

    # Generate unique identifiers
    timestamp = int(time.time())

    # Sample Instagram post data
    sample_data = [
        {
            "url": "https://www.instagram.com/p/test_webhook_ssl_fix/",
            "post_id": f"test_webhook_ssl_fix_{timestamp}",
            "user_posted": "webhook_test_ssl_fix",
            "description": "🔧 SSL FIX WEBHOOK TEST: Testing webhook with SSL verification disabled to work around connection issues. This should reach the database if the webhook is working.",
            "date_posted": "2025-01-15T15:30:00.000Z",
            "num_comments": 8,
            "likes": 156,
            "shortcode": "test_webhook_ssl_fix",
            "content_type": "post",
            "hashtags": ["sslfix", "webhooktest", "trackfutura"],
            "followers": 3200,
            "posts_count": 89,
            "is_verified": False,
            "photos": ["https://example.com/ssl_fix_photo.jpg"],
            "user_posted_id": "ssl_fix_user_123",
            "engagement_score": 0.18
        }
    ]

    # Headers
    headers = {
        'Content-Type': 'application/json',
        'X-Platform': 'instagram',
        'X-Snapshot-Id': f'ssl_fix_webhook_{timestamp}',
        'User-Agent': 'BrightData-Webhook-SSL-Fix/1.0'
    }

    print(f"🌐 Webhook URL: {webhook_url}")
    print(f"📊 Snapshot ID: {headers['X-Snapshot-Id']}")
    print(f"🔑 Post ID: test_webhook_ssl_fix_{timestamp}")
    print(f"👤 User: webhook_test_ssl_fix")
    print()

    try:
        print("📡 Sending POST request (SSL verification disabled)...")

        # Send request with SSL verification disabled
        response = requests.post(
            webhook_url,
            json=sample_data,
            headers=headers,
            timeout=30,
            verify=False  # Disable SSL verification
        )

        print(f"✅ Response Status: {response.status_code}")
        print(f"📝 Response Body: {response.text}")

        if response.status_code == 200:
            print("\n🎉 SUCCESS: Webhook processed successfully!")
            print("\n📋 VERIFICATION STEPS:")
            print("   1. Go to Django Admin: https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/admin/")
            print("   2. Navigate to: Instagram data > Instagram posts")
            print(f"   3. Look for post with:")
            print(f"      • Post ID: test_webhook_ssl_fix_{timestamp}")
            print(f"      • User: webhook_test_ssl_fix")
            print(f"      • Description containing: 'SSL FIX WEBHOOK TEST'")
            print(f"      • Likes: 156")
            print(f"      • Comments: 8")
            print(f"   4. If you see this post, the webhook is working correctly!")

        elif response.status_code == 405:
            print("\n⚠️  Method not allowed - webhook endpoint found but might not accept POST")

        elif response.status_code == 403:
            print("\n🔒 Forbidden - webhook endpoint found but access denied")

        elif response.status_code == 404:
            print("\n❌ Not Found - webhook endpoint doesn't exist at this URL")

        else:
            print(f"\n❌ ERROR: Webhook failed with status {response.status_code}")

    except requests.exceptions.Timeout:
        print("⏱️ ERROR: Request timed out")

    except requests.exceptions.ConnectionError as e:
        print(f"🔌 CONNECTION ERROR: {str(e)}")
        print("   This might indicate:")
        print("   • Server is down")
        print("   • Network connectivity issues")
        print("   • DNS resolution problems")

    except Exception as e:
        print(f"💥 UNEXPECTED ERROR: {str(e)}")

def test_api_root_first():
    """Test the API root endpoint that we know works"""

    print("🧪 TESTING API ROOT ENDPOINT")
    print("=" * 40)

    try:
        response = requests.get(
            "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/",
            timeout=15,
            verify=False
        )

        print(f"✅ API Root Status: {response.status_code}")
        print(f"📝 Response: {response.text}")

        if response.status_code == 200:
            print("🎉 API server is responding!")
            return True
        else:
            print("⚠️  API server responded but with unexpected status")
            return False

    except Exception as e:
        print(f"❌ API Root test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # First test if API server is responding
    api_working = test_api_root_first()

    if api_working:
        print("\n" + "="*60)
        test_webhook_no_ssl_verify()
    else:
        print("\n❌ Skipping webhook test because API server is not responding")
