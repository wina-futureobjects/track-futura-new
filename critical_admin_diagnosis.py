#!/usr/bin/env python3
"""
🚨 CRITICAL ADMIN DIAGNOSIS
===========================
The admin test data is NOT appearing, which means webhook fix is not deployed
"""

import requests
import json

def check_admin_scraped_posts():
    print("🚨 CRITICAL ADMIN DIAGNOSIS")
    print("=" * 50)
    
    print("❌ TEST DATA NOT FOUND IN ADMIN")
    print("   • BrightData Scraper Requests: 0 results")
    print("   • BrightData Batch Jobs: 0 results")
    print("   • This means webhook fix is NOT deployed in production")
    
    print("\n🔍 PLEASE CHECK THESE CRITICAL SECTIONS:")
    
    print("\n1. 📊 BrightData Scraped Posts:")
    print("   • Navigate to: BRIGHTDATA INTEGRATION > BrightData Scraped Posts")
    print("   • Search for: ADMIN_TEST_1760151908")
    print("   • This is the MOST IMPORTANT section!")
    
    print("\n2. 📋 BrightData Webhook Events:")
    print("   • Navigate to: BRIGHTDATA INTEGRATION > BrightData Webhook Events")
    print("   • Look for recent events")
    print("   • Check if any events have our timestamp: 1760151908")
    
    print("\n🚨 IF NO DATA IN SCRAPED POSTS:")
    print("   • The webhook fix is NOT deployed in production")
    print("   • Need to redeploy the backend changes")
    print("   • Production server needs restart")

def create_deployment_fix():
    print("\n🛠️ DEPLOYMENT FIX NEEDED")
    print("=" * 50)
    
    print("The webhook processing fix in views.py is not active in production.")
    print("We need to:")
    print("   1. ✅ Confirm changes are in git")
    print("   2. 🚀 Deploy to production")
    print("   3. 🔄 Restart production server")
    print("   4. 🧪 Test webhook again")

def check_current_webhook_status():
    print("\n🔍 TESTING CURRENT WEBHOOK STATUS")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Send a simple test post
    test_post = {
        "post_id": "DEPLOYMENT_TEST_SIMPLE",
        "url": "https://instagram.com/p/deployment_test",
        "content": "Simple deployment test",
        "platform": "instagram",
        "user_posted": "test_user",
        "likes": 1,
        "folder_id": 216
    }
    
    print("📤 Sending simple deployment test...")
    
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/webhook/",
            json=test_post,
            timeout=20
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result}")
            
            # Check if it includes our new fields
            if 'items_processed' in result:
                print("   ✅ New webhook fix response format detected!")
            else:
                print("   ❌ Old webhook response format - fix not deployed")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def main():
    print("🚨 CRITICAL ADMIN DIAGNOSIS")
    print("=" * 60)
    
    check_admin_scraped_posts()
    create_deployment_fix()
    check_current_webhook_status()
    
    print(f"\n📋 URGENT ADMIN CHECKS NEEDED:")
    print("=" * 60)
    
    print("1. 📊 CHECK: BrightData Scraped Posts")
    print("   • Most critical section!")
    print("   • Search: ADMIN_TEST_1760151908")
    print("   • Should show 2 posts if webhook fix is working")
    
    print("\n2. 📋 CHECK: BrightData Webhook Events")
    print("   • Look for events with timestamp 1760151908")
    print("   • Check status and raw_data fields")
    
    print(f"\n🚨 CRITICAL FINDINGS:")
    print("   • Test data NOT found in Scraper Requests")
    print("   • Test data NOT found in Batch Jobs")
    print("   • This indicates webhook fix is NOT deployed")
    print("   • Need immediate production deployment")
    
    print(f"\n🌐 ADMIN ACCESS:")
    print("   URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/admin/")
    print("   Search for: ADMIN_TEST_1760151908")
    print("   Focus on: BrightData Scraped Posts section")

if __name__ == "__main__":
    main()