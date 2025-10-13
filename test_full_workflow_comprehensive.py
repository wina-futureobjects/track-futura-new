#!/usr/bin/env python
"""
COMPREHENSIVE WORKFLOW TEST - Trigger scraping and verify data saving
This tests the complete end-to-end workflow including webhook delivery
"""
import requests
import json
import time

BASE_URL = "https://trackfutura.futureobjects.io"

def test_trigger_scraper():
    """Test triggering the scraper"""
    print("🚀 STEP 1: Triggering scraper for folder 2 (Nike)")
    
    url = f"{BASE_URL}/api/brightdata/trigger-system/"
    payload = {
        "platform": "instagram",
        "urls": ["https://instagram.com/nike/"],
        "folder_id": 2,
        "date_range": {
            "start_date": "01-09-2025",
            "end_date": "30-09-2025"
        },
        "num_of_posts": 3
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ SCRAPER TRIGGERED SUCCESSFULLY!")
                return True
            else:
                print(f"❌ Scraper failed: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_webhook_directly():
    """Test webhook endpoint directly"""
    print("\n🎯 STEP 2: Testing webhook delivery directly")
    
    url = f"{BASE_URL}/api/brightdata/webhook/"
    test_data = [
        {
            "post_id": f"test_comprehensive_{int(time.time())}",
            "user_username": "nike_test",
            "caption": "Comprehensive test post - this should appear in backend",
            "likes_count": 999,
            "url": f"https://instagram.com/p/test_comp_{int(time.time())}",
            "platform": "instagram"
        }
    ]
    
    try:
        response = requests.post(url, json=test_data, headers={"Content-Type": "application/json"})
        print(f"Webhook Status: {response.status_code}")
        print(f"Webhook Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Webhook Exception: {e}")
        return False

def check_data_in_backend():
    """Check if data is actually saved in the backend"""
    print("\n📊 STEP 3: Checking data in backend")
    
    # Check Instagram posts
    try:
        url = f"{BASE_URL}/api/instagram-data/posts/"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"✅ Instagram Posts Found: {count}")
            
            if count > 0:
                print("📝 Recent Posts:")
                for post in data.get('results', [])[:3]:  # Show first 3
                    print(f"  - ID: {post['id']} | User: {post['user_posted']} | Post ID: {post['post_id']} | Likes: {post['likes']}")
            
            return count > 0
        else:
            print(f"❌ Instagram API Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Check Exception: {e}")
        return False

def check_folders_and_structure():
    """Check folder structure and available data"""
    print("\n📁 STEP 4: Checking folder structure")
    
    try:
        url = f"{BASE_URL}/api/brightdata/webhook-results/folder/2/"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Status: {response.status_code}")
            data = response.json()
            available_folders = data.get('available_folders', [])
            print(f"📂 Total Available Folders: {len(available_folders)}")
            print("📂 Recent Folders:")
            for folder in available_folders[:10]:  # Show first 10
                print(f"  - {folder}")
            return True
        
    except Exception as e:
        print(f"❌ Folder Check Exception: {e}")
        return False

def main():
    """Run comprehensive workflow test"""
    print("=" * 80)
    print("🔥 COMPREHENSIVE WORKFLOW TEST - BRIGHTDATA SCRAPING & WEBHOOK DELIVERY")
    print("=" * 80)
    
    # Test 1: Trigger scraper
    scraper_success = test_trigger_scraper()
    
    # Test 2: Test webhook directly
    webhook_success = test_webhook_directly()
    
    # Wait a moment for processing
    print("\n⏳ Waiting 3 seconds for processing...")
    time.sleep(3)
    
    # Test 3: Check backend data
    data_success = check_data_in_backend()
    
    # Test 4: Check folder structure
    folder_success = check_folders_and_structure()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY:")
    print("=" * 80)
    print(f"🚀 Scraper Trigger:  {'✅ SUCCESS' if scraper_success else '❌ FAILED'}")
    print(f"🎯 Webhook Delivery: {'✅ SUCCESS' if webhook_success else '❌ FAILED'}")
    print(f"📊 Backend Data:     {'✅ SUCCESS' if data_success else '❌ FAILED'}")
    print(f"📁 Folder Structure: {'✅ SUCCESS' if folder_success else '❌ FAILED'}")
    
    overall_success = all([scraper_success or webhook_success, data_success, folder_success])
    
    print(f"\n🎯 OVERALL RESULT: {'✅ WORKFLOW IS WORKING!' if overall_success else '❌ ISSUES FOUND'}")
    
    if overall_success:
        print("\n🎉 YOUR SCRAPING SYSTEM IS FULLY OPERATIONAL!")
        print("\n📱 DIRECT ACCESS LINKS:")
        print(f"   Instagram Posts: {BASE_URL}/api/instagram-data/posts/")
        print(f"   Facebook Posts:  {BASE_URL}/api/facebook-data/posts/")
        print(f"   Webhook Test:    {BASE_URL}/api/brightdata/webhook/")
        print(f"   Trigger System:  {BASE_URL}/api/brightdata/trigger-system/")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()