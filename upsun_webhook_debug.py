#!/usr/bin/env python3
"""
Upsun Webhook Debug Tool
Test webhook endpoints on production environment
"""

import json
import requests
import time
from urllib.parse import urljoin

# Upsun Production URLs
UPSUN_API_BASE = "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site"
UPSUN_FRONTEND_BASE = "https://upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site"

def test_webhook_endpoint():
    """Test if webhook endpoint is accessible"""
    print("🔍 TESTING WEBHOOK ENDPOINT ACCESSIBILITY")
    print("=" * 60)

    endpoints_to_test = [
        f"{UPSUN_API_BASE}/api/brightdata/webhook/",
        f"{UPSUN_API_BASE}/webhook/brightdata/",
        f"{UPSUN_API_BASE}/brightdata/webhook/",
        f"{UPSUN_FRONTEND_BASE}/api/brightdata/webhook/",
        f"{UPSUN_FRONTEND_BASE}/webhook/brightdata/",
    ]

    for endpoint in endpoints_to_test:
        try:
            print(f"\n🌐 Testing: {endpoint}")
            response = requests.get(endpoint, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error: {str(e)}")

def test_notify_endpoint():
    """Test notify endpoint"""
    print("\n🔔 TESTING NOTIFY ENDPOINT")
    print("=" * 60)

    endpoints_to_test = [
        f"{UPSUN_API_BASE}/api/brightdata/notify/",
        f"{UPSUN_API_BASE}/brightdata/notify/",
        f"{UPSUN_FRONTEND_BASE}/api/brightdata/notify/",
    ]

    test_data = {
        "snapshot_id": f"test_notify_{int(time.time())}",
        "status": "finished",
        "message": "Test notification from debug script"
    }

    for endpoint in endpoints_to_test:
        try:
            print(f"\n🌐 Testing POST to: {endpoint}")
            response = requests.post(
                endpoint,
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error: {str(e)}")

def test_notifications_api():
    """Test notifications viewing API"""
    print("\n📋 TESTING NOTIFICATIONS API")
    print("=" * 60)

    endpoints_to_test = [
        f"{UPSUN_API_BASE}/api/brightdata/notifications/",
        f"{UPSUN_API_BASE}/api/brightdata/webhook-metrics/",
        f"{UPSUN_FRONTEND_BASE}/api/brightdata/notifications/",
    ]

    for endpoint in endpoints_to_test:
        try:
            print(f"\n🌐 Testing GET: {endpoint}")
            response = requests.get(endpoint, timeout=10)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   Found {len(data)} items")
                    elif isinstance(data, dict):
                        print(f"   Response keys: {list(data.keys())}")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"   Response: {response.text[:200]}...")

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error: {str(e)}")

def simulate_brightdata_webhook():
    """Simulate a BrightData webhook call"""
    print("\n🤖 SIMULATING BRIGHTDATA WEBHOOK")
    print("=" * 60)

    # Use real Instagram data structure from previous testing
    webhook_data = [
        {
            "url": "https://www.instagram.com/p/DKkbTWvJC37",
            "user_posted": "skybarauburnal",
            "description": "FRIDAY NIGHT - 7PM test webhook debug",
            "hashtags": None,
            "num_comments": 1,
            "date_posted": "2025-01-07T18:19:52.000Z",
            "likes": 445,
            "photos": [
                "https://example.com/photo1.jpg"
            ],
            "shortcode": "DKkbTWvJC37",
            "content_type": "Carousel",
            "instagram_pk": "3649161675416022523",
            "user_posted_id": "1938739694",
            "followers": 23959,
            "is_verified": False
        }
    ]

    endpoints_to_test = [
        f"{UPSUN_API_BASE}/api/brightdata/webhook/",
        f"{UPSUN_API_BASE}/webhook/brightdata/",
    ]

    snapshot_id = f"debug_webhook_{int(time.time())}"

    for endpoint in endpoints_to_test:
        try:
            print(f"\n🌐 Sending webhook to: {endpoint}")
            print(f"   Snapshot ID: {snapshot_id}")

            response = requests.post(
                endpoint,
                json=webhook_data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "BrightData-Webhook/1.0",
                    "X-Brightdata-Snapshot-Id": snapshot_id
                },
                params={"snapshot_id": snapshot_id},
                timeout=15
            )

            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:300]}...")

            if response.status_code == 200:
                print("   ✅ Webhook processed successfully!")
            else:
                print(f"   ❌ Webhook failed with status {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection Error: {str(e)}")

def check_cors_and_csrf():
    """Check CORS and CSRF settings"""
    print("\n🔒 CHECKING CORS AND CSRF SETTINGS")
    print("=" * 60)

    # Test preflight request
    try:
        print("\n🌐 Testing CORS preflight (OPTIONS request)")
        response = requests.options(
            f"{UPSUN_API_BASE}/api/brightdata/webhook/",
            headers={
                "Origin": "https://brightdata.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
            timeout=10
        )

        print(f"   Status: {response.status_code}")
        cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
        if cors_headers:
            print("   CORS Headers:")
            for k, v in cors_headers.items():
                print(f"     {k}: {v}")
        else:
            print("   No CORS headers found")

    except requests.exceptions.RequestException as e:
        print(f"   ❌ CORS Test Error: {str(e)}")

def main():
    """Main debugging function"""
    print("🚀 UPSUN WEBHOOK DEBUG TOOL")
    print("=" * 60)
    print(f"API Base URL: {UPSUN_API_BASE}")
    print(f"Frontend Base URL: {UPSUN_FRONTEND_BASE}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Run all tests
        test_webhook_endpoint()
        test_notify_endpoint()
        test_notifications_api()
        check_cors_and_csrf()
        simulate_brightdata_webhook()

        print("\n" + "=" * 60)
        print("🏁 DEBUGGING COMPLETE")
        print("\n💡 NEXT STEPS:")
        print("1. Check which endpoints are accessible (200 status)")
        print("2. Use working endpoint for BrightData webhook configuration")
        print("3. Monitor notifications page to see incoming data")
        print(f"4. Visit: {UPSUN_FRONTEND_BASE}/brightdata-notifications")

    except KeyboardInterrupt:
        print("\n\n⚠️  Debug interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
