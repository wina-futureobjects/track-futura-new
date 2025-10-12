#!/usr/bin/env python3
"""
Test basic production endpoints to diagnose the issue
"""
import requests

def test_basic_production():
    print("🔧 BASIC PRODUCTION DIAGNOSTICS")
    print("=" * 40)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test basic endpoints that should exist
    basic_endpoints = [
        "/",  # Root 
        "/api/",  # API root
        "/api/health/",  # Health check
        "/api/brightdata/",  # BrightData API base
        "/api/brightdata/webhook/",  # Webhook endpoint
        "/admin/"  # Admin
    ]
    
    for endpoint in basic_endpoints:
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            full_url = f"{base_url}{endpoint}"
            response = requests.get(full_url, timeout=30, allow_redirects=True)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS")
                if 'json' in response.headers.get('content-type', ''):
                    try:
                        data = response.json()
                        print(f"   📊 JSON response keys: {list(data.keys())}")
                    except:
                        pass
                else:
                    print(f"   📄 HTML/Text response ({len(response.text)} chars)")
                    
            elif response.status_code == 404:
                print(f"   ❌ NOT FOUND")
            elif response.status_code == 500:
                print(f"   ❌ SERVER ERROR")
                print(f"   Error: {response.text[:100]}...")
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                print(f"   Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_basic_production()