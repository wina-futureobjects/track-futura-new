#!/usr/bin/env python3
"""
Debug Upsun Production Webhook Issues
This script helps debug webhook problems on the live Upsun deployment
"""

import requests
import json
import time
import os
from datetime import datetime

def get_upsun_webhook_url():
    """Get the correct Upsun webhook URL"""
    # Your Upsun domain from the previous logs
    upsun_domain = "upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site"

    # Test both possible webhook URLs
    webhook_urls = [
        f"https://{upsun_domain}/api/brightdata/webhook/",
        f"https://api.{upsun_domain}/api/brightdata/webhook/"
    ]

    return webhook_urls

def test_upsun_webhook_accessibility():
    """Test if Upsun webhook endpoints are accessible"""
    print("🔍 TESTING UPSUN WEBHOOK ACCESSIBILITY")
    print("=" * 60)

    webhook_urls = get_upsun_webhook_url()

    for url in webhook_urls:
        print(f"\n🔗 Testing: {url}")

        # Test health endpoint
        health_url = url.replace('/webhook/', '/webhook/health/')

        try:
            response = requests.get(health_url, timeout=10)
            print(f"   Health check: {response.status_code}")

            if response.status_code == 200:
                print(f"   ✅ Webhook endpoint accessible")
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)}")
                except:
                    print(f"   Response text: {response.text[:200]}...")
            elif response.status_code == 404:
                print(f"   ❌ Webhook endpoint not found (404)")
            elif response.status_code == 403:
                print(f"   ❌ Webhook endpoint forbidden (403)")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

        except requests.exceptions.ConnectionError:
            print(f"   ❌ Cannot connect to {url}")
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout connecting to {url}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def test_upsun_webhook_post():
    """Test POST request to Upsun webhook"""
    print(f"\n📡 TESTING UPSUN WEBHOOK POST")
    print("=" * 60)

    webhook_urls = get_upsun_webhook_url()

    # Sample Instagram data
    sample_data = [
        {
            "url": "https://www.instagram.com/p/upsun_test/",
            "post_id": f"upsun_test_{int(time.time())}",
            "user_posted": "test_upsun",
            "description": "🚀 UPSUN TEST: Testing webhook on production deployment",
            "date_posted": datetime.now().isoformat(),
            "num_comments": 2,
            "likes": 10,
            "shortcode": "upsun_test",
            "content_type": "post"
        }
    ]

    headers = {
        'Content-Type': 'application/json',
        'X-Platform': 'instagram',
        'X-Snapshot-Id': f'upsun_test_{int(time.time())}',
        'User-Agent': 'BrightData-Webhook/1.0'
    }

    for url in webhook_urls:
        print(f"\n🎯 Testing POST to: {url}")
        print(f"   Headers: {json.dumps(headers, indent=2)}")
        print(f"   Data: {json.dumps(sample_data[0], indent=2)}")

        try:
            response = requests.post(url, json=sample_data, headers=headers, timeout=30)
            print(f"\n   Response Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            print(f"   Response Body: {response.text}")

            if response.status_code == 200:
                print(f"   ✅ Webhook POST successful!")
            elif response.status_code == 401:
                print(f"   ❌ Authentication failed - check BRIGHTDATA_WEBHOOK_TOKEN")
            elif response.status_code == 403:
                print(f"   ❌ Forbidden - check CORS or authentication")
            elif response.status_code == 404:
                print(f"   ❌ Webhook endpoint not found")
            elif response.status_code == 500:
                print(f"   ❌ Server error - check Upsun logs")
            else:
                print(f"   ⚠️  Unexpected response")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def check_brightdata_webhook_config():
    """Check what webhook URL should be configured in BrightData"""
    print(f"\n⚙️  BRIGHTDATA WEBHOOK CONFIGURATION")
    print("=" * 60)

    webhook_urls = get_upsun_webhook_url()

    print("Configure ONE of these URLs in your BrightData webhook settings:")
    for i, url in enumerate(webhook_urls, 1):
        print(f"\n   Option {i}: {url}")
        print(f"   Use this if your Upsun domain structure is: {'api subdomain' if 'api.' in url else 'main domain'}")

    print(f"\n📋 Required BrightData Webhook Headers:")
    print(f"   Content-Type: application/json")
    print(f"   X-Platform: instagram")
    print(f"   X-Snapshot-Id: <your_request_id>")
    print(f"   Authorization: Bearer <your_webhook_token>")

    print(f"\n🔑 Webhook Authentication:")
    print(f"   Make sure BRIGHTDATA_WEBHOOK_TOKEN is set in Upsun environment")
    print(f"   This token must match what you configure in BrightData")

def test_upsun_database_connection():
    """Test if we can connect to Upsun database via API"""
    print(f"\n💾 TESTING UPSUN DATABASE ACCESS")
    print("=" * 60)

    webhook_urls = get_upsun_webhook_url()

    for url in webhook_urls:
        # Try to access a simple API endpoint
        api_url = url.replace('/api/brightdata/webhook/', '/api/instagram_data/folders/')

        print(f"\n🔗 Testing database access: {api_url}")

        try:
            response = requests.get(api_url, timeout=10)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Database accessible")
                    print(f"   Found {len(data.get('results', []))} folders")

                    # Look for folder 46
                    folders = data.get('results', [])
                    folder_46 = next((f for f in folders if f.get('id') == 46), None)
                    if folder_46:
                        print(f"   📁 Folder 46 found: {folder_46.get('name')}")
                    else:
                        print(f"   ⚠️  Folder 46 not found in API response")

                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"   ❌ Cannot access database API: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def check_upsun_logs_access():
    """Provide instructions for checking Upsun logs"""
    print(f"\n📝 UPSUN LOGS DEBUGGING")
    print("=" * 60)

    print("To check what's happening on Upsun when webhooks are sent:")
    print()
    print("1. 🖥️  Via Upsun CLI:")
    print("   upsun log --app backend --tail")
    print("   (Run this while testing webhooks to see real-time logs)")
    print()
    print("2. 🌐 Via Upsun Web Console:")
    print("   - Go to your Upsun project dashboard")
    print("   - Navigate to 'Logs' section")
    print("   - Filter by 'backend' application")
    print("   - Look for webhook-related errors")
    print()
    print("3. 🔍 What to look for in logs:")
    print("   - 'brightdata_webhook' function calls")
    print("   - Authentication errors")
    print("   - Database connection errors")
    print("   - JSON parsing errors")
    print("   - ScraperRequest creation errors")
    print()
    print("4. 🚨 Common Upsun issues:")
    print("   - Environment variables not set")
    print("   - Database migration issues")
    print("   - Memory/CPU limits")
    print("   - Network connectivity issues")

def main():
    print("🚀 UPSUN PRODUCTION WEBHOOK DEBUGGING")
    print("=" * 70)

    # Step 1: Test webhook accessibility
    test_upsun_webhook_accessibility()

    # Step 2: Test webhook POST
    test_upsun_webhook_post()

    # Step 3: Check database access
    test_upsun_database_connection()

    # Step 4: Check BrightData configuration
    check_brightdata_webhook_config()

    # Step 5: Logs access instructions
    check_upsun_logs_access()

    print(f"\n🎯 NEXT STEPS:")
    print("=" * 70)
    print("1. Check Upsun logs while running a scraper")
    print("2. Verify BrightData webhook URL configuration")
    print("3. Confirm BRIGHTDATA_WEBHOOK_TOKEN is set in Upsun")
    print("4. Test webhook with curl from external source")
    print("5. Check if ScraperRequest records are being created on Upsun")

if __name__ == "__main__":
    main()
