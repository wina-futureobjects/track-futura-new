#!/usr/bin/env python3
"""
Test Correct Web Unlocker Endpoint
"""

import requests
import json

def test_correct_web_unlocker_endpoint():
    """Test the correct Web Unlocker endpoint path"""
    
    # The correct URL according to the URLs file
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    endpoint = f"{base_url}/api/brightdata/web-unlocker/scrape/"
    
    test_data = {
        "url": "https://example.com",
        "scraper_name": "Test Scraper with Correct URL"
    }
    
    print("🔧 Testing Correct Web Unlocker Endpoint")
    print(f"URL: {endpoint}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(
            endpoint,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=45
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"🎉 SUCCESS Response:")
                print(json.dumps(data, indent=2))
                return True
            except:
                print(f"📝 Raw Response: {response.text}")
                return True
        elif response.status_code == 500:
            print(f"🔧 Server Error (Enhanced logging should show details):")
            print(f"📝 Response: {response.text}")
            return False
        elif response.status_code == 404:
            print("❌ Endpoint still not found")
            return False
        else:
            print(f"⚠️ Status {response.status_code}:")
            print(f"📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_brightdata_endpoints():
    """Test available BrightData endpoints"""
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    endpoints_to_test = [
        "/api/brightdata/",
        "/api/brightdata/snapshots/",
        "/api/brightdata/configs/",
    ]
    
    print("🔍 Testing BrightData Base Endpoints:")
    print("-" * 50)
    
    for endpoint_path in endpoints_to_test:
        url = base_url + endpoint_path
        try:
            response = requests.get(url, timeout=15)
            print(f"✅ {endpoint_path} -> {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint_path} -> Error: {e}")
    
    print()

if __name__ == "__main__":
    print("🚀 Testing Correct Web Unlocker Implementation")
    print("=" * 60)
    
    test_brightdata_endpoints()
    
    if test_correct_web_unlocker_endpoint():
        print("\n🎉 SUCCESS: Web Unlocker endpoint is working!")
    else:
        print("\n⚠️ Web Unlocker endpoint needs investigation")