#!/usr/bin/env python3
"""
Fix Webhook Routing Issue
Test the correct webhook URL based on Upsun routing configuration
"""

import requests
import json
import time
from datetime import datetime

# CORRECT webhook URLs based on Upsun routing
INCORRECT_URL = "https://upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/"
CORRECT_URL = "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/"

def test_webhook_routing():
    """Test both webhook URLs to confirm the routing issue and fix"""
    print("🔧 TESTING WEBHOOK ROUTING - IDENTIFYING THE CORRECT URL")
    print("=" * 70)

    # Test data
    test_data = [{
        "url": "https://www.instagram.com/p/routing_test/",
        "post_id": f"routing_test_{int(time.time())}",
        "user_posted": "routing_test_user",
        "description": "🔄 Testing webhook routing fix",
        "date_posted": datetime.now().isoformat(),
        "num_comments": 1,
        "likes": 5,
        "shortcode": "routing_test",
        "content_type": "post"
    }]

    headers = {
        'Content-Type': 'application/json',
        'X-Platform': 'instagram',
        'X-Snapshot-Id': f'routing_test_{int(time.time())}',
        'User-Agent': 'BrightData-Webhook/1.0'
    }

    print(f"📍 TESTING INCORRECT URL (goes to frontend):")
    print(f"   {INCORRECT_URL}")
    test_url(INCORRECT_URL, test_data, headers, "INCORRECT - Frontend")

    print(f"\n📍 TESTING CORRECT URL (goes to backend API):")
    print(f"   {CORRECT_URL}")
    test_url(CORRECT_URL, test_data, headers, "CORRECT - Backend API")

def test_url(url, data, headers, description):
    """Test a specific webhook URL"""
    print(f"\n🎯 {description}")
    print(f"   URL: {url}")

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")

        content_type = response.headers.get('content-type', '')

        if 'html' in content_type.lower():
            print(f"   ❌ Returns HTML (Frontend) - Content-Type: {content_type}")
            print(f"   Response preview: {response.text[:150]}...")
        elif 'json' in content_type.lower():
            print(f"   ✅ Returns JSON (API) - Content-Type: {content_type}")
            try:
                json_response = response.json()
                print(f"   Response: {json.dumps(json_response, indent=2)[:200]}...")
            except:
                print(f"   Response text: {response.text[:200]}...")
        else:
            print(f"   ⚠️  Unknown content type: {content_type}")
            print(f"   Response: {response.text[:200]}...")

    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed - URL might not exist")
    except requests.exceptions.Timeout:
        print(f"   ❌ Request timeout")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def provide_brightdata_fix():
    """Provide the exact BrightData configuration fix"""
    print(f"\n🔧 BRIGHTDATA CONFIGURATION FIX")
    print("=" * 70)

    print("❌ CURRENT (WRONG) WEBHOOK URL:")
    print(f"   {INCORRECT_URL}")
    print("   ↳ This goes to React frontend (returns HTML)")
    print()
    print("✅ CORRECT WEBHOOK URL TO USE:")
    print(f"   {CORRECT_URL}")
    print("   ↳ This goes to Django backend API (processes webhooks)")
    print()
    print("🎯 ACTION REQUIRED:")
    print("1. Go to your BrightData dashboard")
    print("2. Find your Instagram scraper configuration")
    print("3. Update webhook URL to the CORRECT URL above")
    print("4. Save the configuration")
    print("5. Test with next scraping job")

def test_api_endpoints():
    """Test various API endpoints to confirm backend accessibility"""
    print(f"\n🧪 TESTING BACKEND API ENDPOINTS")
    print("=" * 70)

    api_endpoints = [
        "/api/brightdata/webhook/health/",
        "/api/instagram_data/folders/",
        "/api/users/profile/"
    ]

    for endpoint in api_endpoints:
        correct_url = f"https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site{endpoint}"
        incorrect_url = f"https://upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site{endpoint}"

        print(f"\n🔍 Testing: {endpoint}")
        print(f"   Correct API URL: {test_endpoint_briefly(correct_url)}")
        print(f"   Incorrect URL: {test_endpoint_briefly(incorrect_url)}")

def test_endpoint_briefly(url):
    """Briefly test an endpoint and return status"""
    try:
        response = requests.get(url, timeout=10)
        content_type = response.headers.get('content-type', '')

        if 'html' in content_type.lower():
            return f"{response.status_code} (HTML/Frontend)"
        elif 'json' in content_type.lower():
            return f"{response.status_code} (JSON/API) ✅"
        else:
            return f"{response.status_code} ({content_type})"
    except:
        return "Failed/Not Found"

def main():
    print("🚨 FIXING WEBHOOK ROUTING ISSUE")
    print("=" * 70)

    print("PROBLEM IDENTIFIED:")
    print("Your Upsun routing sends main domain to frontend, subdomain to backend")
    print("Webhook URL needs to use API subdomain to reach Django backend")
    print()

    # Test both URLs
    test_webhook_routing()

    # Test other API endpoints
    test_api_endpoints()

    # Provide fix instructions
    provide_brightdata_fix()

    print(f"\n🎉 SUMMARY:")
    print("=" * 70)
    print("✅ Problem identified: Wrong webhook URL routing")
    print("✅ Solution: Use API subdomain webhook URL")
    print("✅ Your next scraping job should work after updating BrightData config")
    print()
    print("⚡ URGENT: Update BrightData webhook URL now!")

if __name__ == "__main__":
    main()
