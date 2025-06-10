#!/usr/bin/env python3
"""
Simple webhook test for local development
"""

import json
import requests
import time

def test_local_webhook():
    """Test webhook on local development server"""
    print("🧪 TESTING LOCAL WEBHOOK")
    print("=" * 50)

    # Test data (same structure as BrightData)
    webhook_data = [
        {
            "url": "https://www.instagram.com/p/DKkbTWvJC37",
            "user_posted": "skybarauburnal",
            "description": "Local webhook test",
            "hashtags": None,
            "num_comments": 1,
            "date_posted": "2025-01-07T18:19:52.000Z",
            "likes": 445,
            "photos": ["https://example.com/photo1.jpg"],
            "shortcode": "DKkbTWvJC37",
            "content_type": "Carousel",
            "instagram_pk": "3649161675416022523",
            "user_posted_id": "1938739694",
            "followers": 23959,
            "is_verified": False
        }
    ]

    snapshot_id = f"local_test_{int(time.time())}"

    try:
        print(f"📤 Sending webhook to: http://localhost:8000/api/brightdata/webhook/")
        print(f"   Snapshot ID: {snapshot_id}")

        response = requests.post(
            "http://localhost:8000/api/brightdata/webhook/",
            json=webhook_data,
            headers={
                "Content-Type": "application/json",
                "X-Brightdata-Snapshot-Id": snapshot_id
            },
            params={"snapshot_id": snapshot_id},
            timeout=10
        )

        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")

        if response.status_code == 200:
            print("   ✅ Local webhook working!")
            return True
        else:
            print(f"   ❌ Local webhook failed with status {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection Error: {str(e)}")
        print("   💡 Make sure Django server is running: python manage.py runserver")
        return False

def test_local_notify():
    """Test notify endpoint locally"""
    print("\n🔔 TESTING LOCAL NOTIFY ENDPOINT")
    print("=" * 50)

    test_data = {
        "snapshot_id": f"notify_test_{int(time.time())}",
        "status": "finished",
        "message": "Local notify test"
    }

    try:
        print(f"📤 Sending notify to: http://localhost:8000/api/brightdata/notify/")

        response = requests.post(
            "http://localhost:8000/api/brightdata/notify/",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")

        if response.status_code == 200:
            print("   ✅ Local notify working!")
            return True
        else:
            print(f"   ❌ Local notify failed with status {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection Error: {str(e)}")
        return False

def test_local_notifications_api():
    """Test notifications API locally"""
    print("\n📋 TESTING LOCAL NOTIFICATIONS API")
    print("=" * 50)

    try:
        print(f"📤 Getting notifications from: http://localhost:8000/api/brightdata/notifications/")

        response = requests.get(
            "http://localhost:8000/api/brightdata/notifications/",
            timeout=10
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   Found {data.get('count', 0)} notifications")
            print("   ✅ Local notifications API working!")
            return True
        else:
            print(f"   ❌ Local notifications API failed with status {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 LOCAL WEBHOOK TEST")
    print("=" * 50)
    print("This will test the webhook functionality on your local Django server.")
    print("Make sure to run 'python manage.py runserver' in another terminal first.")
    print()

    webhook_ok = test_local_webhook()
    notify_ok = test_local_notify()
    api_ok = test_local_notifications_api()

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"   Webhook: {'✅ PASS' if webhook_ok else '❌ FAIL'}")
    print(f"   Notify: {'✅ PASS' if notify_ok else '❌ FAIL'}")
    print(f"   API: {'✅ PASS' if api_ok else '❌ FAIL'}")

    if all([webhook_ok, notify_ok, api_ok]):
        print("\n🎉 ALL TESTS PASSED!")
        print("Your local webhook system is working correctly.")
        print("The issue is likely that changes need to be deployed to Upsun.")
    else:
        print("\n⚠️  SOME TESTS FAILED!")
        print("Fix local issues before deploying to Upsun.")

if __name__ == "__main__":
    main()
