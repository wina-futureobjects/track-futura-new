#!/usr/bin/env python3
"""
Test specific BrightData endpoints to see what's available
"""
import requests
import json

def test_brightdata_endpoints():
    print("🔧 BRIGHTDATA ENDPOINT DIAGNOSTICS")
    print("=" * 40)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test BrightData specific endpoints
    brightdata_endpoints = [
        "/api/brightdata/configs/",
        "/api/brightdata/scraper-requests/", 
        "/api/brightdata/batch-jobs/",
        "/api/brightdata/data-storage/",  # Check if this base exists
        "/api/brightdata/results/",
        "/api/brightdata/trigger-scraper/",
        # Test our specific endpoints
        "/api/brightdata/data-storage/run/",  # Check base path
        "/api/brightdata/data-storage/run/17/",
        "/api/brightdata/data-storage/run/18/"
    ]
    
    for endpoint in brightdata_endpoints:
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            full_url = f"{base_url}{endpoint}"
            response = requests.get(full_url, timeout=30)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS")
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        print(f"   📊 Keys: {list(data.keys())}")
                        if 'posts' in data:
                            print(f"   🔢 Posts: {len(data['posts'])}")
                    elif isinstance(data, list):
                        print(f"   📊 List length: {len(data)}")
                except:
                    print(f"   📄 Text response ({len(response.text)} chars)")
                    
            elif response.status_code == 404:
                print(f"   ❌ NOT FOUND")
            elif response.status_code == 405:
                print(f"   ⚠️  METHOD NOT ALLOWED (endpoint exists but wrong method)")
            elif response.status_code == 500:
                print(f"   ❌ SERVER ERROR")
                print(f"   Error: {response.text[:100]}...")
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Also check the base BrightData response to see what endpoints it lists
    print(f"\n🔍 CHECKING BRIGHTDATA BASE RESPONSE...")
    try:
        response = requests.get(f"{base_url}/api/brightdata/", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   Available endpoints: {list(data.keys())}")
            for key, value in data.items():
                if isinstance(value, str) and value.startswith('http'):
                    print(f"   {key}: {value}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_brightdata_endpoints()