#!/usr/bin/env python3
"""
Simple URL pattern test - verify our new endpoints are accessible
"""

import requests
import time

BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def test_url_patterns():
    """Test different URL pattern variations to debug the 404 issue"""
    
    print("🔍 DEBUGGING URL PATTERNS")
    print("=" * 50)
    
    # Test the basic BrightData API structure first
    print("\n1. Testing BrightData API structure...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/brightdata/", timeout=10)
        print(f"   /api/brightdata/ - Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("   Available endpoints:")
                for key, value in data.items():
                    print(f"     - {key}: {value}")
            except:
                print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test if our new URLs are in the API discovery
    print("\n2. Looking for data-storage in API response...")
    try:
        response = requests.get(f"{BASE_URL}/api/brightdata/", timeout=10)
        if response.status_code == 200:
            text = response.text.lower()
            if 'data-storage' in text:
                print("   ✅ Found 'data-storage' in API response")
            else:
                print("   ❌ 'data-storage' not found in API response")
                print("   This suggests the new URL patterns might not be deployed yet")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test various URL patterns
    print("\n3. Testing URL pattern variations...")
    
    test_urls = [
        "/api/brightdata/data-storage/",  # Base pattern
        "/api/brightdata/data-storage/test/1/",  # Simple test
        "/api/brightdata/data-storage/Job%203/1/",  # Our target
        "/api/brightdata/configs/",  # Known working endpoint for comparison
    ]
    
    for url_path in test_urls:
        full_url = f"{BASE_URL}{url_path}"
        try:
            response = requests.get(full_url, timeout=10)
            print(f"   {url_path} - Status: {response.status_code}")
            
            if response.status_code == 404:
                print(f"     ❌ Not found - URL pattern not deployed")
            elif response.status_code in [200, 401, 403, 405]:
                print(f"     ✅ Pattern exists (auth/method issues are normal)")
            else:
                print(f"     ⚠️ Unexpected: {response.status_code}")
                
        except Exception as e:
            print(f"     ❌ Connection error: {e}")
    
    print(f"\n4. Deployment timing check...")
    print(f"   Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Our commit was pushed around 11:46")
    print(f"   Platform.sh deployments typically take 2-5 minutes")
    print(f"   If still getting 404s, deployment may still be in progress")

if __name__ == "__main__":
    test_url_patterns()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS:")
    print("- If data-storage URLs return 404: Deployment still in progress")
    print("- If data-storage URLs return 401/403: Deployment successful, need auth")
    print("- If data-storage URLs return 200: Ready to test with real data")
    print("\n💡 TIP: Try running this script again in 2-3 minutes if seeing 404s")