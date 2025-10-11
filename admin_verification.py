#!/usr/bin/env python3
"""
🎯 DIRECT ADMIN VERIFICATION
============================
Create data that will definitely show up in Django admin panel
"""

import requests
import json
import time
import random

def create_admin_visible_data():
    print("📊 CREATING ADMIN-VISIBLE DATA")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Create data with very specific, trackable identifiers
    timestamp = int(time.time())
    
    admin_test_posts = [
        {
            "post_id": f"ADMIN_TEST_216_{timestamp}_1",
            "url": f"https://instagram.com/p/ADMIN_TEST_216_{timestamp}_1",
            "content": f"🚨 ADMIN TEST POST 1 FOR FOLDER 216 - Timestamp {timestamp}. This should appear in Django admin! #admin #test #folder216",
            "platform": "instagram",
            "user_posted": "admin_test_user_216",
            "likes": 9999,
            "num_comments": 999,
            "shares": 99,
            "folder_id": 216,
            "media_type": "photo",
            "is_verified": True,
            "hashtags": ["admin", "test", "folder216"],
            "mentions": ["@trackfutura", "@admin"],
            "location": "Admin Test Center 216"
        },
        {
            "post_id": f"ADMIN_TEST_219_{timestamp}_1",
            "url": f"https://facebook.com/posts/ADMIN_TEST_219_{timestamp}_1",
            "content": f"🚨 ADMIN TEST POST 1 FOR FOLDER 219 - Timestamp {timestamp}. This should appear in Django admin! #admin #test #folder219",
            "platform": "facebook",
            "user_posted": "admin_test_user_219",
            "likes": 8888,
            "num_comments": 888,
            "shares": 88,
            "folder_id": 219,
            "media_type": "photo",
            "is_verified": True,
            "hashtags": ["admin", "test", "folder219"],
            "mentions": ["@trackfutura", "@admin"],
            "location": "Admin Test Center 219"
        },
        {
            "post_id": f"ADMIN_TEST_216_{timestamp}_2",
            "url": f"https://instagram.com/p/ADMIN_TEST_216_{timestamp}_2",
            "content": f"🔥 ADMIN TEST POST 2 FOR FOLDER 216 - Second test post to confirm folder linking works! Timestamp {timestamp} #adminconfirm",
            "platform": "instagram",
            "user_posted": "admin_confirm_user_216",
            "likes": 7777,
            "num_comments": 777,
            "shares": 77,
            "folder_id": 216,
            "media_type": "video",
            "is_verified": True,
            "hashtags": ["adminconfirm", "test", "folder216"],
            "mentions": ["@trackfutura"],
            "location": "Confirmation Test 216"
        }
    ]
    
    print(f"📤 Sending {len(admin_test_posts)} admin test posts...")
    
    sent_posts = []
    for i, post in enumerate(admin_test_posts, 1):
        print(f"   📨 Sending admin test post {i}: {post['post_id']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/brightdata/webhook/",
                json=post,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                sent_posts.append(post['post_id'])
                print(f"      ✅ Success: {result.get('status', 'success')}")
            else:
                print(f"      ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print(f"\n📈 Successfully sent {len(sent_posts)}/{len(admin_test_posts)} admin test posts")
    return sent_posts, timestamp

def check_webhook_events():
    print("\n🔍 CHECKING WEBHOOK EVENTS")
    print("=" * 50)
    
    print("💡 What to check in Django Admin:")
    print("   1. Go to: BrightData Integration > BrightData Webhook Events")
    print("   2. Look for recent events with our timestamp")
    print("   3. Check if status = 'completed'")
    print("   4. Verify platform and raw_data fields")

def check_scraped_posts():
    print("\n📊 CHECKING SCRAPED POSTS")
    print("=" * 50)
    
    print("💡 What to check in Django Admin:")
    print("   1. Go to: BrightData Integration > BrightData Scraped Posts")
    print("   2. Look for posts with our ADMIN_TEST_ post_ids")
    print("   3. Verify folder_id = 216 or 219 (NOT 1)")
    print("   4. Check created_at timestamps")

def manual_admin_verification_steps():
    print("\n📋 MANUAL ADMIN VERIFICATION STEPS")
    print("=" * 50)
    
    print("🔧 STEP-BY-STEP ADMIN CHECK:")
    print("   1. Login to Django Admin:")
    print("      URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/admin/")
    print("      Username: superadmin")
    print("      Password: admin123")
    
    print("\n   2. Check BrightData Scraped Posts:")
    print("      • Navigate to: BRIGHTDATA INTEGRATION > BrightData Scraped Posts")
    print("      • Look for posts with 'ADMIN_TEST_' in post_id")
    print("      • Verify folder_id shows 216 or 219")
    print("      • Check created_at for recent timestamps")
    
    print("\n   3. Check BrightData Webhook Events:")
    print("      • Navigate to: BRIGHTDATA INTEGRATION > BrightData Webhook Events")
    print("      • Look for recent events")
    print("      • Check status = 'completed'")
    print("      • Verify raw_data contains our test posts")
    
    print("\n   4. Check BrightData Scraper Requests:")
    print("      • Navigate to: BRIGHTDATA INTEGRATION > BrightData Scraper Requests")
    print("      • Look for requests with folder_id 216, 219")
    print("      • Check if any new ones were created")

def test_direct_api_verification():
    print("\n🧪 DIRECT API VERIFICATION")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Wait for processing
    print("⏳ Waiting 15 seconds for webhook processing...")
    time.sleep(15)
    
    # Test both folders
    for folder_id in [216, 219]:
        print(f"\n📁 Testing folder {folder_id}...")
        
        try:
            response = requests.get(f"{base_url}/api/brightdata/job-results/{folder_id}/", timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('total_results', 0) > 0:
                    posts = data.get('data', [])
                    print(f"   🎉 SUCCESS! Found {len(posts)} posts in folder {folder_id}")
                    
                    # Look for our admin test posts
                    admin_posts = [p for p in posts if 'ADMIN_TEST_' in p.get('post_id', '')]
                    if admin_posts:
                        print(f"   🎯 Found {len(admin_posts)} of our admin test posts!")
                        for post in admin_posts[:2]:  # Show first 2
                            print(f"      📄 {post.get('post_id', 'N/A')}")
                    else:
                        print(f"   📋 No admin test posts found, but {len(posts)} total posts exist")
                        
                else:
                    print(f"   ➖ No data in folder {folder_id}: {data.get('error', 'Unknown')}")
            else:
                print(f"   ❌ API error for folder {folder_id}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception for folder {folder_id}: {e}")

def main():
    print("🎯 DIRECT ADMIN VERIFICATION")
    print("=" * 60)
    
    # Create trackable admin test data
    sent_posts, timestamp = create_admin_visible_data()
    
    # Check webhook events
    check_webhook_events()
    
    # Check scraped posts
    check_scraped_posts()
    
    # Provide manual verification steps
    manual_admin_verification_steps()
    
    # Test direct API
    test_direct_api_verification()
    
    print(f"\n🎊 ADMIN VERIFICATION SUMMARY")
    print("=" * 60)
    
    print(f"✅ Sent {len(sent_posts)} trackable admin test posts")
    print(f"🕐 Test timestamp: {timestamp}")
    print(f"🔍 Search for: 'ADMIN_TEST_{timestamp}' in Django admin")
    
    print(f"\n📋 WHAT TO CHECK:")
    print("   1. BrightData Scraped Posts - look for ADMIN_TEST_ posts")
    print("   2. Verify folder_id = 216 or 219 (not 1)")
    print("   3. Check if webhook created BrightDataScrapedPost records")
    print("   4. Look for recent webhook events with completed status")
    
    print(f"\n🌐 ADMIN ACCESS:")
    print("   URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/admin/")
    print("   Username: superadmin")
    print("   Password: admin123")
    
    print(f"\n🎯 IF DATA APPEARS IN ADMIN:")
    print("   • The webhook fix is working correctly")
    print("   • BrightDataScrapedPost records are being created")
    print("   • Issue might be in job-results API query logic")
    
    print(f"\n⚠️ IF NO DATA IN ADMIN:")
    print("   • Check production deployment status")
    print("   • Verify webhook processing logs")
    print("   • May need to restart production server")

if __name__ == "__main__":
    main()