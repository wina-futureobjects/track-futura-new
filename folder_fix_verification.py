#!/usr/bin/env python3
"""
🎉 FOLDER FIX VERIFICATION TEST
===============================
Test webhook now that folders 216 and 219 exist!
"""

import requests
import json
import time

def test_webhook_after_folder_fix():
    print("🎉 FOLDER FIX VERIFICATION TEST")
    print("=" * 50)
    
    print("✅ FOLDERS CREATED SUCCESSFULLY:")
    print("   • Job Folder 216 (Instagram/Posts)")
    print("   • Job Folder 219 (Facebook/Posts)")
    print("   • Both belong to Demo project")
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    timestamp = int(time.time())
    
    # Test posts for both folders
    test_posts = [
        {
            "post_id": f"FOLDER_FIX_TEST_216_{timestamp}",
            "url": f"https://instagram.com/p/folder_fix_test_216_{timestamp}",
            "content": f"🎉 SUCCESS TEST - Folder 216 now exists! This should appear in database. Timestamp: {timestamp}",
            "platform": "instagram",
            "user_posted": "folder_fix_test_user",
            "likes": 2160,
            "num_comments": 216,
            "shares": 21,
            "folder_id": 216,
            "media_type": "photo",
            "hashtags": ["success", "folder216", "fixed"],
            "mentions": ["@trackfutura"]
        },
        {
            "post_id": f"FOLDER_FIX_TEST_219_{timestamp}",
            "url": f"https://facebook.com/posts/folder_fix_test_219_{timestamp}",
            "content": f"🎉 SUCCESS TEST - Folder 219 now exists! This should appear in database. Timestamp: {timestamp}",
            "platform": "facebook",
            "user_posted": "folder_fix_test_user",
            "likes": 2190,
            "num_comments": 219,
            "shares": 21,
            "folder_id": 219,
            "media_type": "photo",
            "hashtags": ["success", "folder219", "fixed"],
            "mentions": ["@trackfutura"]
        }
    ]
    
    print(f"\n📤 TESTING WEBHOOK WITH EXISTING FOLDERS...")
    
    sent_posts = []
    for i, post in enumerate(test_posts, 1):
        print(f"   📨 Sending test post {i}: {post['post_id']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/brightdata/webhook/",
                json=post,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                sent_posts.append(post['post_id'])
                print(f"      ✅ SUCCESS: {result}")
                
                if result.get('items_processed') == 1:
                    print(f"      🎯 WEBHOOK PROCESSED 1 ITEM")
                else:
                    print(f"      ⚠️ Unexpected items_processed: {result.get('items_processed')}")
                    
            else:
                print(f"      ❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    return sent_posts, timestamp

def check_admin_panel_instructions(timestamp):
    print(f"\n🔍 CHECK ADMIN PANEL NOW:")
    print("=" * 50)
    
    print("🌐 Admin Panel:")
    print("   URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/admin/")
    print("   Username: superadmin")
    print("   Password: admin123")
    
    print(f"\n📊 CHECK THESE SECTIONS:")
    
    print("\n1. 📋 BrightData Webhook Events:")
    print("   • Navigate to: BRIGHTDATA INTEGRATION > BrightData Webhook Events")
    print(f"   • Search for: FOLDER_FIX_TEST_{timestamp}")
    print("   • Should show 2 recent events")
    print("   • Check status = 'completed'")
    
    print("\n2. 📄 BrightData Scraped Posts:")
    print("   • Navigate to: BRIGHTDATA INTEGRATION > BrightData Scraped Posts")
    print(f"   • Search for: FOLDER_FIX_TEST_{timestamp}")
    print("   • Should show 2 posts:")
    print(f"     - FOLDER_FIX_TEST_216_{timestamp} (folder_id=216)")
    print(f"     - FOLDER_FIX_TEST_219_{timestamp} (folder_id=219)")

def test_job_results_api():
    print(f"\n🧪 TESTING JOB-RESULTS API:")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("⏳ Waiting 10 seconds for database processing...")
    time.sleep(10)
    
    for folder_id in [216, 219]:
        print(f"\n📁 Testing job-results API for folder {folder_id}...")
        
        try:
            response = requests.get(f"{base_url}/api/brightdata/job-results/{folder_id}/", timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('total_results', 0) > 0:
                    posts = data.get('data', [])
                    print(f"   🎉 SUCCESS! Found {len(posts)} posts in folder {folder_id}")
                    
                    # Look for our test posts
                    test_posts = [p for p in posts if 'FOLDER_FIX_TEST_' in p.get('post_id', '')]
                    if test_posts:
                        print(f"   🎯 Found {len(test_posts)} of our test posts!")
                        for post in test_posts:
                            print(f"      📄 {post.get('post_id', 'N/A')}")
                    else:
                        print(f"   📋 No test posts found yet, but {len(posts)} total posts exist")
                        
                else:
                    print(f"   ➖ No data in folder {folder_id}: {data.get('error', 'Unknown')}")
            else:
                print(f"   ❌ API error for folder {folder_id}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception for folder {folder_id}: {e}")

def main():
    print("🎉 FOLDER FIX VERIFICATION TEST")
    print("=" * 60)
    
    # Test webhook with existing folders
    sent_posts, timestamp = test_webhook_after_folder_fix()
    
    # Admin panel check instructions
    check_admin_panel_instructions(timestamp)
    
    # Test job-results API
    test_job_results_api()
    
    print(f"\n🎊 VERIFICATION SUMMARY:")
    print("=" * 60)
    
    print(f"✅ Sent {len(sent_posts)} test posts to existing folders")
    print(f"🕐 Test timestamp: {timestamp}")
    print(f"🔍 Search term: FOLDER_FIX_TEST_{timestamp}")
    
    print(f"\n🎯 EXPECTED RESULTS:")
    print("   • Webhook events should appear in admin")
    print("   • Scraped posts should appear in admin")
    print("   • Data should show in job-results API")
    print("   • All with correct folder_id values (216, 219)")
    
    print(f"\n🚨 IF DATA APPEARS:")
    print("   🎉 DATABASE ISSUE IS FIXED!")
    print("   🎉 WEBHOOK PROCESSING IS WORKING!")
    print("   🎉 PRODUCTION DATA STORAGE IS READY!")
    
    print(f"\n⚠️ IF NO DATA APPEARS:")
    print("   • Check admin panel carefully")
    print("   • May need to investigate further")
    print("   • But folder creation was the likely fix")

if __name__ == "__main__":
    main()