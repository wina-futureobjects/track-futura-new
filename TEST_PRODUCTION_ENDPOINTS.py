#!/usr/bin/env python3
"""
Test the new human-friendly endpoints on production after deployment
"""

import requests
import json
import time

PRODUCTION_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def test_folder_with_data():
    """Test with folder that has actual data"""
    print("🧪 TESTING FOLDER WITH ACTUAL DATA")
    print("=" * 45)
    
    # Based on our local test, "Job 3" has 39 posts
    test_cases = [
        ("Job 3", 1, "All data for Job 3 scrape 1"),
        ("nike", 1, "Nike folder scrape 1 (might be empty)"),
    ]
    
    for folder_name, scrape_num, description in test_cases:
        print(f"\n📋 TESTING: {description}")
        
        # URL encode spaces in folder names
        folder_name_encoded = folder_name.replace(" ", "%20")
        
        url = f"{PRODUCTION_URL}/api/brightdata/data-storage/{folder_name_encoded}/{scrape_num}/"
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: {data.get('success')}")
                print(f"   📊 Total Results: {data.get('total_results', 0)}")
                print(f"   📁 Folder Name: {data.get('folder_name')}")
                print(f"   🔢 Scrape Number: {data.get('scrape_number')}")
                
                if data.get('data') and len(data['data']) > 0:
                    first_post = data['data'][0]
                    print(f"   📝 First Post: {first_post.get('platform')} by {first_post.get('user_posted')}")
                
            elif response.status_code == 404:
                print(f"   ❌ 404 Not Found - Check if folder exists or deployment is complete")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"      Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")

def test_platform_filtering():
    """Test platform-specific filtering"""
    print(f"\n🎯 TESTING PLATFORM FILTERING")
    print("=" * 35)
    
    # Test Job 3 with Instagram filtering
    folder_name_encoded = "Job%203"
    url = f"{PRODUCTION_URL}/api/brightdata/data-storage/{folder_name_encoded}/1/instagram/"
    print(f"📋 Testing Instagram filter: {url}")
    
    try:
        response = requests.get(url)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('success')}")
            print(f"   📊 Instagram Posts: {data.get('total_results', 0)}")
            print(f"   🎯 Platform Filter: {data.get('platform')}")
        else:
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

def wait_for_deployment():
    """Wait for deployment to complete"""
    print("⏳ WAITING FOR DEPLOYMENT TO COMPLETE...")
    print("=" * 45)
    
    for i in range(6):  # Wait up to 60 seconds
        print(f"   Checking deployment status... ({i*10}s)")
        
        try:
            # Test a simple API endpoint to see if deployment is ready
            response = requests.get(f"{PRODUCTION_URL}/api/health/", timeout=10)
            if response.status_code == 200:
                print(f"   ✅ API is responding")
                break
        except:
            pass
            
        if i < 5:  # Don't sleep on the last iteration
            time.sleep(10)
    
    print(f"   🚀 Ready to test new endpoints!")

def main():
    print("🚀 TESTING NEW HUMAN-FRIENDLY ENDPOINTS ON PRODUCTION")
    print("=" * 65)
    
    # Wait a bit for deployment
    wait_for_deployment()
    
    # Test the new endpoints
    test_folder_with_data()
    test_platform_filtering()
    
    print(f"\n🎉 TESTING COMPLETE!")
    print(f"=" * 25)
    
    print(f"\n📋 WHAT TO EXPECT:")
    print(f"✅ If endpoints work: You'll see data returned with success=True")
    print(f"❌ If 404 errors: The new URL patterns might not be deployed yet")
    print(f"⚠️ If empty data: Folder exists but no scraped posts linked to it")
    
    print(f"\n🔗 NEW URL PATTERNS NOW AVAILABLE:")
    print(f"- /api/brightdata/data-storage/Job%203/1/")
    print(f"- /api/brightdata/data-storage/nike/1/")
    print(f"- /api/brightdata/data-storage/nike/1/instagram/")
    print(f"- /api/brightdata/data-storage/nike/1/instagram/post/nike/")

if __name__ == "__main__":
    main()