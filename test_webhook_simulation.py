#!/usr/bin/env python3
"""
Simple Webhook Simulation for Testing
Simulates BrightData sending Instagram data to your webhook
"""

import requests
import json
import time

def test_instagram_webhook():
    """Test Instagram webhook with sample data"""

    # Your local webhook URL
    webhook_url = 'http://localhost:8000/api/brightdata/webhook/'

    # Sample Instagram data (matches what BrightData would send)
    sample_data = [
        {
            "url": "https://www.instagram.com/p/test123/",
            "post_id": f"test_ig_{int(time.time())}",
            "user_posted": "test_user",
            "description": "This is a test Instagram post for debugging webhook data flow",
            "date_posted": "2024-01-15T10:30:00Z",
            "num_comments": 5,
            "likes": 25,
            "shortcode": "test123",
            "content_type": "post",
            "hashtags": ["test", "debug"]
        }
    ]

    # Headers that BrightData would send
    headers = {
        'Content-Type': 'application/json',
        'X-Platform': 'instagram',
        'X-Snapshot-Id': 'your_request_id_here',  # Replace with actual request ID
        'User-Agent': 'BrightData-Webhook/1.0'
    }

    print("🧪 Testing Instagram Webhook")
    print("=" * 40)
    print(f"URL: {webhook_url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Data: {json.dumps(sample_data, indent=2)}")
    print()

    try:
        response = requests.post(
            webhook_url,
            json=sample_data,
            headers=headers,
            timeout=30
        )

        print(f"✅ Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")

        if response.status_code == 200:
            print("✅ Webhook call successful!")
            try:
                response_json = response.json()
                print(f"Response JSON: {json.dumps(response_json, indent=2)}")
            except:
                print("Response is not JSON")
        else:
            print(f"❌ Webhook call failed with status {response.status_code}")

    except Exception as e:
        print(f"❌ Error calling webhook: {str(e)}")

def check_webhook_endpoint():
    """Check if webhook endpoint is accessible"""
    print("\n🔍 Checking webhook endpoint...")

    try:
        response = requests.get('http://localhost:8000/api/brightdata/')
        print(f"API endpoint status: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach API endpoint: {str(e)}")
        print("Make sure your Django server is running: cd backend && python manage.py runserver")

if __name__ == "__main__":
    check_webhook_endpoint()

    # Ask for request ID
    request_id = input("\n📋 Enter your Instagram scraper request ID (or press Enter to use 'test'): ").strip()
    if not request_id:
        request_id = 'test'

    # Update headers with request ID
    print(f"\nUsing request ID: {request_id}")

    test_instagram_webhook()

    print(f"\n💡 To see if data was saved, run:")
    print(f"   python check_instagram_debug.py")
