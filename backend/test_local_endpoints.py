#!/usr/bin/env python3
"""
Test local endpoints to confirm they work before production
"""
import requests
import json

def test_local_endpoints():
    print("🔧 TESTING LOCAL ENDPOINTS")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test our endpoints
    endpoints = [
        "/api/brightdata/data-storage/run/18/",
        "/api/brightdata/data-storage/run/17/", 
        "/api/brightdata/data-storage/run/16/"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            full_url = f"{base_url}{endpoint}"
            response = requests.get(full_url, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    posts = data.get('posts', [])
                    folder_info = data.get('folder', {})
                    
                    print(f"   ✅ SUCCESS - {len(posts)} posts")
                    print(f"   📁 {folder_info.get('name', 'N/A')}")
                    print(f"   🏷️  {folder_info.get('platform', 'N/A')}")
                    
                except json.JSONDecodeError as e:
                    print(f"   ⚠️  JSON Error: {e}")
                    print(f"   Raw: {response.text[:100]}...")
                    
            else:
                print(f"   ❌ HTTP {response.status_code}")
                print(f"   Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return True

if __name__ == "__main__":
    test_local_endpoints()