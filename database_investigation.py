#!/usr/bin/env python3
"""
🔍 DEEP DATABASE INVESTIGATION
==============================
Check exactly what's in BrightDataScrapedPost for folder 216/219
"""

import requests
import json

def investigate_database_contents():
    print("🔍 DEEP DATABASE INVESTIGATION")
    print("=" * 50)
    
    print("📊 ADMIN PANEL SHOWS:")
    print("   • 27 BrightDataScrapedPost records exist ✅")
    print("   • Folders visible: 191, 177, 170, 167, 1, 188, 181, 152, 144")
    print("   • NO folders 216, 219 visible in list")
    print("   • Our test posts NOT found in search")
    
    print(f"\n🔍 CRITICAL QUESTIONS:")
    print("   1. Are folder 216/219 posts being saved correctly?")
    print("   2. Is there a folder_id mismatch?")
    print("   3. Are the posts getting filtered out?")
    
    print(f"\n📋 INVESTIGATION PLAN:")
    print("   1. Send a post to existing folder (like 191)")
    print("   2. Send a post to folder 216")
    print("   3. Compare results")

def test_existing_folder():
    print(f"\n🧪 TEST 1: SEND TO EXISTING FOLDER 191")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test post to folder 191 (we know this works)
    test_191_post = {
        "post_id": "INVESTIGATION_191_TEST",
        "url": "https://facebook.com/p/investigation_191",
        "content": "🔍 Investigation test for existing folder 191",
        "platform": "facebook",
        "user_posted": "investigation_user",
        "likes": 191,
        "num_comments": 19,
        "shares": 1,
        "folder_id": 191,
        "media_type": "photo"
    }
    
    print(f"   📤 Sending to folder 191 (known working)...")
    
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/webhook/",
            json=test_191_post,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SUCCESS: {result}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_folder_216():
    print(f"\n🧪 TEST 2: SEND TO FOLDER 216")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test post to folder 216
    test_216_post = {
        "post_id": "INVESTIGATION_216_TEST",
        "url": "https://instagram.com/p/investigation_216",
        "content": "🔍 Investigation test for folder 216",
        "platform": "instagram",
        "user_posted": "investigation_user",
        "likes": 216,
        "num_comments": 21,
        "shares": 2,
        "folder_id": 216,
        "media_type": "photo"
    }
    
    print(f"   📤 Sending to folder 216 (our target)...")
    
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/webhook/",
            json=test_216_post,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SUCCESS: {result}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_both_apis():
    print(f"\n🧪 TEST 3: CHECK BOTH APIS")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    import time
    print("⏳ Waiting 15 seconds for processing...")
    time.sleep(15)
    
    # Test folder 191 API
    print(f"\n📁 Testing job-results API for folder 191...")
    try:
        response = requests.get(f"{base_url}/api/brightdata/job-results/191/", timeout=20)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                posts = data.get('data', [])
                print(f"   🎉 Folder 191: Found {len(posts)} posts")
                
                # Look for our investigation post
                investigation_posts = [p for p in posts if 'INVESTIGATION_191' in p.get('post_id', '')]
                if investigation_posts:
                    print(f"   🎯 Found our investigation post in folder 191!")
                else:
                    print(f"   📋 Investigation post not found yet")
            else:
                print(f"   ➖ Folder 191: {data.get('error', 'No data')}")
        else:
            print(f"   ❌ Folder 191 API error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Folder 191 exception: {e}")
    
    # Test folder 216 API
    print(f"\n📁 Testing job-results API for folder 216...")
    try:
        response = requests.get(f"{base_url}/api/brightdata/job-results/216/", timeout=20)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                posts = data.get('data', [])
                print(f"   🎉 Folder 216: Found {len(posts)} posts")
                
                # Look for our investigation post
                investigation_posts = [p for p in posts if 'INVESTIGATION_216' in p.get('post_id', '')]
                if investigation_posts:
                    print(f"   🎯 Found our investigation post in folder 216!")
                else:
                    print(f"   📋 Investigation post not found yet")
            else:
                print(f"   ➖ Folder 216: {data.get('error', 'No data')}")
        else:
            print(f"   ❌ Folder 216 API error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Folder 216 exception: {e}")

def admin_panel_search_instructions():
    print(f"\n🔍 ADMIN PANEL SEARCH INSTRUCTIONS:")
    print("=" * 50)
    
    print("After running this investigation, search in admin panel for:")
    print("   • INVESTIGATION_191_TEST")
    print("   • INVESTIGATION_216_TEST")
    
    print(f"\n📊 EXPECTED RESULTS:")
    print("   • INVESTIGATION_191_TEST should appear (folder 191 works)")
    print("   • INVESTIGATION_216_TEST should appear (if folder 216 works)")
    
    print(f"\n🎯 DIAGNOSIS:")
    print("   • If 191 works but 216 doesn't → folder-specific issue")
    print("   • If both work → job-results API query issue")
    print("   • If neither works → webhook processing issue")

def main():
    print("🔍 DEEP DATABASE INVESTIGATION")
    print("=" * 60)
    
    investigate_database_contents()
    test_existing_folder()
    test_folder_216()
    test_both_apis()
    admin_panel_search_instructions()
    
    print(f"\n🎯 INVESTIGATION COMPLETE")
    print("=" * 60)
    print("This will definitively tell us if the issue is:")
    print("   1. Folder-specific (216/219 vs other folders)")
    print("   2. Job-results API query logic")
    print("   3. Webhook processing (unlikely since admin shows posts)")

if __name__ == "__main__":
    main()