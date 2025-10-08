#!/usr/bin/env python3
"""
BRIGHTDATA PRODUCTION STATUS TEST
================================
Test the current production BrightData integration status.
"""

import requests
import json

def test_production_brightdata():
    """Test BrightData integration in production"""
    print("🧪 TESTING PRODUCTION BRIGHTDATA DEPLOYMENT")
    print("=" * 60)
    
    production_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test 1: Check if API endpoint is accessible
    print("\n1. Testing API endpoint accessibility...")
    try:
        response = requests.get(f"{production_url}/api/brightdata/configs/", timeout=10)
        print(f"   Config API status: {response.status_code}")
        if response.status_code == 404:
            print("   ❌ API endpoint not found - need to check URL routing")
        elif response.status_code in [401, 403]:
            print("   ⚠️  API endpoint requires authentication")
        elif response.status_code == 200:
            print("   ✅ API endpoint accessible")
    except Exception as e:
        print(f"   ❌ API endpoint test failed: {str(e)}")
    
    # Test 2: Check webhook endpoint
    print("\n2. Testing webhook endpoint...")
    try:
        webhook_url = f"{production_url}/api/brightdata/webhook/"
        response = requests.post(webhook_url, 
                               json={"test": "webhook"}, 
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        print(f"   Webhook status: {response.status_code}")
        if response.status_code in [200, 405]:  # 405 = Method not allowed but endpoint exists
            print("   ✅ Webhook endpoint exists")
        else:
            print(f"   ⚠️  Webhook response: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Webhook test failed: {str(e)}")
    
    # Test 3: Test scraper trigger endpoint
    print("\n3. Testing scraper trigger endpoint...")
    try:
        trigger_url = f"{production_url}/api/brightdata/trigger-scraper/"
        test_payload = {
            "platform": "instagram",
            "urls": ["https://www.instagram.com/nike/"]
        }
        
        response = requests.post(trigger_url,
                               json=test_payload,
                               headers={"Content-Type": "application/json"},
                               timeout=15)
        
        print(f"   Trigger API status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("   ✅ Scraper trigger successful!")
        elif response.status_code == 500:
            print("   ❌ Server error - configuration may be missing")
        elif response.status_code == 404:
            print("   ❌ Endpoint not found - check URL routing")
        else:
            print(f"   ⚠️  Unexpected response code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Scraper trigger test failed: {str(e)}")
    
    # Test 4: Test with authentication (if available)
    print("\n4. Testing authenticated API access...")
    try:
        # Try to get a token first
        login_url = f"{production_url}/api/users/login/"
        login_data = {
            "username": "test",
            "password": "test123"
        }
        
        login_response = requests.post(login_url, 
                                     json=login_data,
                                     headers={"Content-Type": "application/json"},
                                     timeout=10)
        
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            if "access" in token_data:
                headers = {"Authorization": f"Bearer {token_data['access']}"}
                
                # Test authenticated config access
                config_response = requests.get(f"{production_url}/api/brightdata/configs/",
                                             headers=headers,
                                             timeout=10)
                print(f"   Authenticated config access: {config_response.status_code}")
                
                if config_response.status_code == 200:
                    configs = config_response.json()
                    print(f"   ✅ Found {len(configs)} BrightData configurations")
                    
                    for config in configs[:3]:  # Show first 3 configs
                        print(f"      - {config.get('platform', 'unknown')}: {config.get('name', 'unnamed')}")
                else:
                    print(f"   ❌ Config access failed: {config_response.text[:100]}")
            else:
                print("   ❌ No access token in login response")
        else:
            print(f"   ⚠️  Login failed: {login_response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Authentication test failed: {str(e)}")
    
    print(f"\n📋 PRODUCTION TEST SUMMARY:")
    print(f"   Production URL: {production_url}")
    print(f"   Next steps:")
    print(f"   1. If endpoints are not found (404), check URL routing")
    print(f"   2. If authentication is required, create test user")
    print(f"   3. If server errors (500), check BrightData configuration")
    print(f"   4. Run deployment script to fix configuration issues")


if __name__ == "__main__":
    test_production_brightdata()