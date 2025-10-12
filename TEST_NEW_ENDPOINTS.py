#!/usr/bin/env python3
"""
Test the new human-friendly data storage endpoints
"""

import requests
import json

PRODUCTION_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def test_new_endpoints():
    """Test the new human-friendly endpoints"""
    print("🧪 TESTING NEW HUMAN-FRIENDLY ENDPOINTS")
    print("=" * 60)
    
    # Test 1: Create sample data with scrape number for nike folder
    print("\n📋 1. TESTING FOLDER 'nike' SCRAPE 1")
    response = requests.get(f"{PRODUCTION_URL}/api/brightdata/data-storage/nike/1/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Message: {data.get('message')}")
        print(f"   Total Results: {data.get('total_results', 0)}")
    else:
        print(f"   Error: {response.text[:200]}...")
    
    # Test 2: Test platform filtering
    print("\n📋 2. TESTING NIKE SCRAPE 1 INSTAGRAM ONLY")
    response = requests.get(f"{PRODUCTION_URL}/api/brightdata/data-storage/nike/1/instagram/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Platform: {data.get('platform')}")
        print(f"   Total Results: {data.get('total_results', 0)}")
    else:
        print(f"   Error: {response.text[:200]}...")
    
    # Test 3: Test posts endpoint
    print("\n📋 3. TESTING NIKE SCRAPE 1 INSTAGRAM POSTS")
    response = requests.get(f"{PRODUCTION_URL}/api/brightdata/data-storage/nike/1/instagram/post/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Total Results: {data.get('total_results', 0)}")
    else:
        print(f"   Error: {response.text[:200]}...")
    
    # Test 4: Test account-specific posts
    print("\n📋 4. TESTING NIKE SCRAPE 1 INSTAGRAM POSTS BY 'nike' ACCOUNT")
    response = requests.get(f"{PRODUCTION_URL}/api/brightdata/data-storage/nike/1/instagram/post/nike/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Account: {data.get('account')}")
        print(f"   Total Results: {data.get('total_results', 0)}")
    else:
        print(f"   Error: {response.text[:200]}...")
    
    # Test 5: Test non-existent folder
    print("\n📋 5. TESTING NON-EXISTENT FOLDER")
    response = requests.get(f"{PRODUCTION_URL}/api/brightdata/data-storage/nonexistent/1/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 404:
        data = response.json()
        print(f"   ✅ Correctly returns 404 for non-existent folder")
        print(f"   Error: {data.get('error')}")
    else:
        print(f"   ❌ Expected 404, got {response.status_code}")
    
    # Test 6: Test non-existent scrape number
    print("\n📋 6. TESTING NON-EXISTENT SCRAPE NUMBER")
    response = requests.get(f"{PRODUCTION_URL}/api/brightdata/data-storage/nike/999/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 404:
        data = response.json()
        print(f"   ✅ Correctly returns 404 for non-existent scrape number")
        print(f"   Error: {data.get('error')}")
    else:
        print(f"   ❌ Expected 404, got {response.status_code}")

def main():
    print("🚀 NEW ENDPOINT PATTERN TESTING")
    print("=" * 70)
    print("🎯 New URL patterns:")
    print("   /api/brightdata/data-storage/<folder_name>/<scrape_num>/")
    print("   /api/brightdata/data-storage/<folder_name>/<scrape_num>/<platform>/")
    print("   /api/brightdata/data-storage/<folder_name>/<scrape_num>/<platform>/post/")
    print("   /api/brightdata/data-storage/<folder_name>/<scrape_num>/<platform>/post/<account>/")
    print()
    
    test_new_endpoints()
    
    print(f"\n💡 NEXT STEPS:")
    print(f"1. Apply the migration: python manage.py migrate brightdata_integration")
    print(f"2. When you run new scrapes, they will get scrape_number 2, 3, etc.")
    print(f"3. Frontend can use these human-friendly URLs instead of folder IDs")
    print(f"4. URLs like /data-storage/nike/2/instagram/ are much clearer!")

if __name__ == "__main__":
    main()