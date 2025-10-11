#!/usr/bin/env python3
"""
🚨 ADMIN PANEL FIX VERIFICATION
===============================
Test after adding BrightDataScrapedPost to admin panel
"""

import requests
import json
import time

def test_after_admin_fix():
    print("🚨 ADMIN PANEL FIX VERIFICATION")
    print("=" * 50)
    
    print("🔧 ADMIN FIX DEPLOYED:")
    print("   • Added BrightDataScrapedPost to Django admin")
    print("   • Should now appear in admin panel")
    print("   • Git pushed to production")
    
    print(f"\n⏳ Waiting 30 seconds for deployment...")
    time.sleep(30)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    timestamp = int(time.time())
    
    # Send a clear test post
    test_post = {
        "post_id": f"ADMIN_FIX_TEST_{timestamp}",
        "url": f"https://instagram.com/p/admin_fix_test_{timestamp}",
        "content": f"🔧 ADMIN FIX TEST - BrightDataScrapedPost should now appear in admin panel! Timestamp: {timestamp}",
        "platform": "instagram",
        "user_posted": "admin_fix_test_user",
        "likes": 9999,
        "num_comments": 999,
        "shares": 99,
        "folder_id": 216,
        "media_type": "photo",
        "hashtags": ["adminfix", "test", "scraped"],
        "mentions": ["@trackfutura"]
    }
    
    print(f"\n📤 SENDING ADMIN FIX TEST POST...")
    print(f"   Post ID: {test_post['post_id']}")
    
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/webhook/",
            json=test_post,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SUCCESS: {result}")
            
            if result.get('items_processed') == 1:
                print(f"   🎯 WEBHOOK PROCESSED 1 ITEM")
            
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return timestamp

def admin_panel_verification_steps(timestamp):
    print(f"\n🔍 ADMIN PANEL VERIFICATION:")
    print("=" * 50)
    
    print("🌐 Admin Panel:")
    print("   URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/admin/")
    print("   Username: superadmin")
    print("   Password: admin123")
    
    print(f"\n📊 CHECK FOR NEW SECTION:")
    print("   • Navigate to: BRIGHTDATA INTEGRATION")
    print("   • Should now see: 'BrightData Scraped Posts' (NEW!)")
    print("   • Click on 'BrightData Scraped Posts'")
    
    print(f"\n🔍 SEARCH FOR TEST DATA:")
    print(f"   • Search for: ADMIN_FIX_TEST_{timestamp}")
    print("   • Should show 1 scraped post")
    print("   • Check folder_id = 216")
    print("   • Check platform = instagram")
    
    print(f"\n📋 ALSO CHECK WEBHOOK EVENTS:")
    print("   • Navigate to: BrightData Webhook Events")
    print(f"   • Search for: ADMIN_FIX_TEST_{timestamp}")
    print("   • Should show 1 webhook event")

def final_verification():
    print(f"\n🎯 FINAL VERIFICATION STEPS:")
    print("=" * 50)
    
    print("1. 🔄 REFRESH ADMIN PANEL")
    print("   • Hard refresh (Ctrl+F5)")
    print("   • Should see 'BrightData Scraped Posts' section")
    
    print("\n2. 🔍 CHECK SCRAPED POSTS")
    print("   • Click on 'BrightData Scraped Posts'")
    print("   • Search for our test data")
    print("   • Verify folder_id and platform")
    
    print("\n3. 🧪 TEST JOB-RESULTS API")
    print("   • If data appears in admin, test the API")
    print("   • Should finally show data in data-storage page")

def main():
    print("🚨 ADMIN PANEL FIX VERIFICATION")
    print("=" * 60)
    
    # Test webhook after admin fix
    timestamp = test_after_admin_fix()
    
    # Admin panel verification
    admin_panel_verification_steps(timestamp)
    
    # Final verification
    final_verification()
    
    print(f"\n🎊 CRITICAL MOMENT:")
    print("=" * 60)
    print("This admin panel fix should finally make BrightDataScrapedPost")
    print("visible in Django admin, confirming webhook data is being saved!")
    
    print(f"\n🔍 Search term: ADMIN_FIX_TEST_{timestamp}")
    print("Check BOTH 'BrightData Webhook Events' AND 'BrightData Scraped Posts'")

if __name__ == "__main__":
    main()