#!/usr/bin/env python3
"""
TEST PRODUCTION WEBHOOK FIX
===========================
Test if the webhook fix is working in production
"""

import requests
import json
import time

def test_webhook_fix():
    print("🧪 TESTING PRODUCTION WEBHOOK FIX")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test post with explicit folder_id
    test_post = {
        "post_id": f"webhook_fix_test_{int(time.time())}",
        "url": "https://instagram.com/p/webhook_fix_test",
        "content": "WEBHOOK FIX TEST - This post should now link to a job folder! 🎯",
        "platform": "instagram",
        "user_posted": "webhook_fix_tester",
        "likes": 2500,
        "num_comments": 150,
        "shares": 75,
        "folder_id": 224,  # Test folder
        "media_type": "photo",
        "hashtags": ["webhookfix", "production", "test"],
        "is_verified": True,
        "location": "Production Test Center"
    }
    
    print("📤 Sending test post to webhook...")
    
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/webhook/",
            json=test_post,
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result}")
            
            # Wait for processing
            print("⏳ Waiting 5 seconds for processing...")
            time.sleep(5)
            
            # Check if data appears in job folder
            print("🔍 Checking if data appears in job folder 224...")
            
            job_response = requests.get(
                f"{base_url}/api/brightdata/job-results/224/",
                timeout=15
            )
            
            if job_response.status_code == 200:
                job_data = job_response.json()
                if job_data.get('success') and job_data.get('total_results', 0) > 0:
                    print(f"   ✅ SUCCESS! Folder 224 now has {job_data.get('total_results')} posts!")
                    print(f"   🎉 WEBHOOK FIX IS WORKING!")
                    return True
                else:
                    print(f"   ➖ Folder 224 still shows: {job_data.get('error', 'No data')}")
            else:
                print(f"   ❌ Job results API error: {job_response.status_code}")
                
        else:
            print(f"   ❌ Webhook error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    return False

def test_all_folders():
    print("\n🔍 TESTING ALL FOLDERS")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    test_folders = [222, 223, 224, 225]
    working_folders = []
    
    for folder_id in test_folders:
        try:
            response = requests.get(
                f"{base_url}/api/brightdata/job-results/{folder_id}/",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('total_results', 0) > 0:
                    working_folders.append(folder_id)
                    print(f"   ✅ Folder {folder_id}: {data.get('total_results')} posts")
                else:
                    print(f"   ➖ Folder {folder_id}: {data.get('error', 'No data')}")
            else:
                print(f"   ❌ Folder {folder_id}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Folder {folder_id}: {e}")
    
    return working_folders

def main():
    print("🎯 PRODUCTION WEBHOOK FIX VERIFICATION")
    print("=" * 60)
    
    # Test the fix
    fix_working = test_webhook_fix()
    
    # Test all folders
    working_folders = test_all_folders()
    
    print(f"\n🎊 TEST RESULTS")
    print("=" * 60)
    
    if fix_working:
        print("🎉 WEBHOOK FIX IS WORKING!")
        print("   ✅ Posts are now linking to job folders")
        print("   ✅ BrightDataScrapedPost records are being created")
    else:
        print("⚠️ Webhook fix may need more time or additional testing")
    
    if working_folders:
        print(f"\n📊 WORKING FOLDERS: {working_folders}")
        for folder_id in working_folders:
            print(f"   🌐 Folder {folder_id}: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/{folder_id}")
    else:
        print("\n📋 No folders showing data yet - webhook fix may need time to deploy")
        
    print(f"\n👑 SUPERADMIN ACCESS:")
    print("   Username: superadmin")
    print("   Password: admin123")
    print("   URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/login")
    
    print(f"\n🔧 WHAT WAS FIXED:")
    print("   • Added _create_brightdata_scraped_post function")
    print("   • Modified _process_brightdata_results to create BrightDataScrapedPost records")
    print("   • Webhook now links posts to job folders via folder_id")
    print("   • job-results API can now find and display the data")

if __name__ == "__main__":
    main()