#!/usr/bin/env python3
"""
🔧 DEBUG WEBHOOK TEST
=====================
Test webhook with debug logging deployed
"""

import requests
import json
import time

def debug_webhook_test():
    print("🔧 DEBUG WEBHOOK TEST")
    print("=" * 50)
    
    print("⏳ Waiting 60 seconds for deployment...")
    time.sleep(60)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    timestamp = int(time.time())
    
    # Simple debug test post
    debug_test_post = {
        "post_id": f"DEBUG_TEST_{timestamp}",
        "url": f"https://instagram.com/p/debug_{timestamp}",
        "content": f"🔧 Debug test with logging. Timestamp: {timestamp}",
        "platform": "instagram",
        "user_posted": "debug_user",
        "likes": 1000,
        "num_comments": 100,
        "shares": 10,
        "folder_id": 216,
        "media_type": "photo"
    }
    
    print(f"📤 Sending debug test post...")
    print(f"   Post ID: {debug_test_post['post_id']}")
    print(f"   Folder ID: {debug_test_post['folder_id']}")
    
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/webhook/",
            json=debug_test_post,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SUCCESS: {result}")
            
            if result.get('items_processed') == 1:
                print(f"   🎯 WEBHOOK PROCESSED 1 ITEM")
                print(f"   🔍 Now check production logs for debug output")
            
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return timestamp

def admin_panel_check(timestamp):
    print(f"\n🔍 ADMIN PANEL CHECK:")
    print("=" * 50)
    
    print(f"Search in admin panel for: DEBUG_TEST_{timestamp}")
    print("This will confirm if the debug logging shows the issue")

def main():
    print("🔧 DEBUG WEBHOOK TEST")
    print("=" * 60)
    
    timestamp = debug_webhook_test()
    admin_panel_check(timestamp)
    
    print(f"\n🎯 NEXT STEPS:")
    print("=" * 60)
    print("1. Check admin panel for the debug test post")
    print("2. Check production logs for debug output")
    print("3. The logs will show exactly where the issue is")
    
    print(f"\n🔍 EXPECTED DEBUG OUTPUT:")
    print("   • _create_brightdata_scraped_post called")
    print("   • item_data keys and values")
    print("   • folder_id extraction process")
    print("   • post_data creation details")
    print("   • Database save success/failure")

if __name__ == "__main__":
    main()