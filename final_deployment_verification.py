#!/usr/bin/env python3
"""
🚀 FINAL DEPLOYMENT VERIFICATION
=================================
Test after forcing deployment push
"""

import requests
import json
import time

def final_deployment_test():
    print("🚀 FINAL DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    print("🔄 DEPLOYMENT STATUS:")
    print("   • Admin fix committed ✅")
    print("   • Forced deployment push ✅")
    print("   • Should deploy in 2-5 minutes")
    
    print(f"\n⏳ Waiting 60 seconds for deployment...")
    time.sleep(60)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    timestamp = int(time.time())
    
    # Send final test post
    final_test_post = {
        "post_id": f"FINAL_DEPLOYMENT_TEST_{timestamp}",
        "url": f"https://instagram.com/p/final_test_{timestamp}",
        "content": f"🚀 FINAL DEPLOYMENT TEST - Admin panel should now show BrightDataScrapedPost! Timestamp: {timestamp}",
        "platform": "instagram",
        "user_posted": "final_test_user",
        "likes": 10000,
        "num_comments": 1000,
        "shares": 100,
        "folder_id": 216,
        "media_type": "photo",
        "hashtags": ["final", "deployment", "test"],
        "mentions": ["@trackfutura"]
    }
    
    print(f"\n📤 SENDING FINAL DEPLOYMENT TEST...")
    print(f"   Post ID: {final_test_post['post_id']}")
    
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/webhook/",
            json=final_test_post,
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

def admin_panel_final_check(timestamp):
    print(f"\n🔍 ADMIN PANEL FINAL CHECK:")
    print("=" * 50)
    
    print("🌐 Admin Panel (HARD REFRESH!):")
    print("   URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/admin/")
    print("   Username: superadmin")
    print("   Password: admin123")
    print("   HARD REFRESH: Ctrl+F5 or Cmd+Shift+R")
    
    print(f"\n📊 LOOK FOR NEW SECTION:")
    print("   BRIGHTDATA INTEGRATION should now have:")
    print("   • BrightData Batch Jobs")
    print("   • BrightData Configurations")
    print("   • BrightData Scraper Requests")
    print("   • BrightData Webhook Events")
    print("   • 🆕 BrightData Scraped Posts ← SHOULD BE HERE NOW!")
    
    print(f"\n🔍 SEARCH IN SCRAPED POSTS:")
    print(f"   • Click on 'BrightData Scraped Posts'")
    print(f"   • Search for: FINAL_DEPLOYMENT_TEST_{timestamp}")
    print("   • Should show 1 post with folder_id=216")

def final_api_test():
    print(f"\n🧪 FINAL API TEST:")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("⏳ Waiting 15 seconds for processing...")
    time.sleep(15)
    
    print(f"\n📁 Testing job-results API for folder 216...")
    
    try:
        response = requests.get(f"{base_url}/api/brightdata/job-results/216/", timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success') and data.get('total_results', 0) > 0:
                posts = data.get('data', [])
                print(f"   🎉 SUCCESS! Found {len(posts)} posts in folder 216")
                
                # Look for our test posts
                test_posts = [p for p in posts if 'TEST_' in p.get('post_id', '')]
                if test_posts:
                    print(f"   🎯 Found {len(test_posts)} test posts!")
                    for post in test_posts[:3]:
                        print(f"      📄 {post.get('post_id', 'N/A')}")
                else:
                    print(f"   📋 No test posts found yet, but {len(posts)} total posts exist")
                    
            else:
                print(f"   ➖ No data in folder 216: {data.get('error', 'Unknown')}")
        else:
            print(f"   ❌ API error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def main():
    print("🚀 FINAL DEPLOYMENT VERIFICATION")
    print("=" * 60)
    
    # Final test
    timestamp = final_deployment_test()
    
    # Admin panel check
    admin_panel_final_check(timestamp)
    
    # API test
    final_api_test()
    
    print(f"\n🎊 THIS IS IT!")
    print("=" * 60)
    
    print(f"✅ Deployment triggered with git push")
    print(f"🔍 Search term: FINAL_DEPLOYMENT_TEST_{timestamp}")
    print(f"🎯 If 'BrightData Scraped Posts' appears in admin:")
    print("   🎉 THE FIX IS COMPLETE!")
    print("   🎉 WEBHOOK PROCESSING IS WORKING!")
    print("   🎉 DATA STORAGE IS OPERATIONAL!")
    
    print(f"\n⚠️ IF STILL NOT VISIBLE:")
    print("   • Platform.sh deployment may take 5-10 minutes")
    print("   • Try again in a few minutes")
    print("   • Check deployment status in Platform.sh dashboard")

if __name__ == "__main__":
    main()