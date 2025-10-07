#!/usr/bin/env python3
"""
Alternative BrightData API testing approaches
"""
import requests
import json

def test_brightdata_alternative_methods():
    print("=== ALTERNATIVE BRIGHTDATA API TESTING ===")
    print()
    
    api_key = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    # BrightData might use different API patterns
    alternative_tests = [
        {
            "name": "Direct Zone API (common pattern)",
            "url": f"https://brightdata.com/api/zone/{api_key}",
            "headers": {"Content-Type": "application/json"}
        },
        {
            "name": "Zone Management API",
            "url": "https://brightdata.com/api/zones",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Proxy Zone API",
            "url": f"https://brightdata.com/api/proxy_zones",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Account Status Check",
            "url": "https://brightdata.com/api/account",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "API with username format (zone_name:api_key)",
            "url": "https://brightdata.com/api/status",
            "headers": {
                "Authorization": f"Basic {requests.auth._basic_auth_str(api_key, '')}",
                "Content-Type": "application/json"
            }
        }
    ]
    
    working_endpoints = []
    
    for test in alternative_tests:
        print(f"🧪 Testing: {test['name']}")
        print(f"   URL: {test['url']}")
        
        try:
            response = requests.get(test['url'], headers=test['headers'], timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS!")
                working_endpoints.append(test)
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:300]}...")
                except:
                    print(f"   Response: {response.text[:200]}")
            elif response.status_code == 401:
                print("   ❌ Unauthorized")
            elif response.status_code == 403:
                print("   ❌ Forbidden")
            elif response.status_code == 404:
                print("   ❌ Not Found")
            else:
                print(f"   ⚠️  Status {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()
    
    # Test if this might be a Luminati/BrightData proxy API key
    print("🔍 TESTING LUMINATI/PROXY API PATTERNS:")
    
    luminati_tests = [
        {
            "name": "Luminati API Status",
            "url": "https://luminati.io/api/status",
            "headers": {"Authorization": f"Bearer {api_key}"}
        },
        {
            "name": "Proxy Status Check",
            "url": "https://brightdata.com/cp/api/stats",
            "headers": {"Authorization": f"Bearer {api_key}"}
        }
    ]
    
    for test in luminati_tests:
        print(f"   Testing: {test['name']}")
        try:
            response = requests.get(test['url'], headers=test['headers'], timeout=5)
            print(f"   Status: {response.status_code}")
            if response.status_code != 404:
                print(f"   Response: {response.text[:100]}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        print()
    
    # Test simple HTTP check to see if domain resolves
    print("🌐 BASIC CONNECTIVITY TEST:")
    try:
        response = requests.get("https://brightdata.com", timeout=5)
        print(f"   BrightData homepage: {response.status_code}")
        
        response = requests.get("https://api.brightdata.com", timeout=5)
        print(f"   BrightData API domain: {response.status_code}")
    except Exception as e:
        print(f"   Connectivity issue: {str(e)}")
    
    print()
    print("📋 SUMMARY:")
    if working_endpoints:
        print("   ✅ Found working endpoints!")
        for endpoint in working_endpoints:
            print(f"     - {endpoint['name']}")
    else:
        print("   ❌ No working endpoints found")
        print()
        print("   💡 POSSIBLE EXPLANATIONS:")
        print("   1. This API key might be for BrightData Proxy service, not Data Collection")
        print("   2. The API key might need to be paired with a username/zone name")
        print("   3. BrightData might have changed their API structure")
        print("   4. The API key might be expired or inactive")
        print()
        print("   🔧 RECOMMENDED ACTIONS:")
        print("   1. Log into your BrightData dashboard")
        print("   2. Look for 'Data Collection' or 'Web Scraping' section")
        print("   3. Check if you have any active collectors/scrapers")
        print("   4. Look for API documentation in the dashboard")
        print("   5. Verify this is a Data Collection API key, not a Proxy API key")

if __name__ == "__main__":
    test_brightdata_alternative_methods()