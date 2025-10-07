#!/usr/bin/env python3
"""
Test BrightData API key validity and find correct endpoints
"""
import requests
import json
import base64

def test_brightdata_api_key():
    print("=== BRIGHTDATA API KEY VALIDATION TEST ===")
    print()
    
    api_key = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    print(f"Testing API Key: {api_key}")
    print()
    
    # Test different authentication methods and endpoints
    test_cases = [
        {
            "name": "Bearer Token - API v3",
            "url": "https://api.brightdata.com/datasets/v3",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Bearer Token - API v1", 
            "url": "https://api.brightdata.com/v1",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Bearer Token - Account Info",
            "url": "https://api.brightdata.com/user",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Basic Auth - API Key as username",
            "url": "https://api.brightdata.com/datasets/v3",
            "headers": {
                "Authorization": f"Basic {base64.b64encode(f'{api_key}:'.encode()).decode()}",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "X-API-Key Header",
            "url": "https://api.brightdata.com/datasets/v3", 
            "headers": {
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Alternative Base URL - brightdata.io",
            "url": "https://api.brightdata.io/datasets/v3",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Alternative Base URL - brightdata.com/api",
            "url": "https://brightdata.com/api/datasets/v3",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        }
    ]
    
    results = []
    
    for test in test_cases:
        print(f"🧪 Testing: {test['name']}")
        print(f"   URL: {test['url']}")
        
        try:
            response = requests.get(test['url'], headers=test['headers'], timeout=10)
            
            print(f"   Status Code: {response.status_code}")
            
            # Check for different response types
            if response.status_code == 200:
                print("   ✅ SUCCESS!")
                try:
                    data = response.json()
                    print(f"   Response Type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"   Keys: {list(data.keys())[:5]}")
                    elif isinstance(data, list):
                        print(f"   List Length: {len(data)}")
                    results.append({
                        "test": test['name'],
                        "success": True,
                        "status": response.status_code,
                        "data": data
                    })
                except:
                    print(f"   Response Text: {response.text[:200]}")
                    results.append({
                        "test": test['name'],
                        "success": True,
                        "status": response.status_code,
                        "text": response.text[:200]
                    })
            elif response.status_code == 401:
                print("   ❌ UNAUTHORIZED - API key might be invalid or wrong auth method")
                results.append({
                    "test": test['name'],
                    "success": False,
                    "status": 401,
                    "error": "Unauthorized"
                })
            elif response.status_code == 403:
                print("   ❌ FORBIDDEN - API key valid but no permission for this endpoint")
                results.append({
                    "test": test['name'],
                    "success": False,
                    "status": 403,
                    "error": "Forbidden"
                })
            elif response.status_code == 404:
                print("   ❌ NOT FOUND - Endpoint doesn't exist")
                results.append({
                    "test": test['name'],
                    "success": False,
                    "status": 404,
                    "error": "Not Found"
                })
            else:
                print(f"   ⚠️  Unexpected Status: {response.text[:100]}")
                results.append({
                    "test": test['name'],
                    "success": False,
                    "status": response.status_code,
                    "error": response.text[:100]
                })
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ REQUEST FAILED: {str(e)}")
            results.append({
                "test": test['name'],
                "success": False,
                "error": str(e)
            })
        
        print()
    
    # Test specific BrightData endpoints that might exist
    print("🔍 TESTING SPECIFIC BRIGHTDATA ENDPOINTS:")
    specific_endpoints = [
        "https://api.brightdata.com/v2/zone",
        "https://api.brightdata.com/v2/zones",
        "https://api.brightdata.com/datacollector",
        "https://api.brightdata.com/collector",
        "https://api.brightdata.com/scraper"
    ]
    
    for endpoint in specific_endpoints:
        print(f"   Testing: {endpoint}")
        try:
            response = requests.get(endpoint, headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }, timeout=5)
            print(f"   Status: {response.status_code}")
            if response.status_code != 404:
                print(f"   Response: {response.text[:100]}")
        except:
            print(f"   Failed to connect")
        print()
    
    # Summary
    print("📊 TEST SUMMARY:")
    successful_tests = [r for r in results if r.get('success', False)]
    
    if successful_tests:
        print("   ✅ WORKING ENDPOINTS FOUND:")
        for test in successful_tests:
            print(f"     - {test['test']}: Status {test['status']}")
        print()
        print("   🎉 YOUR API KEY IS ACTIVE!")
        print("   Use the working endpoint configuration above.")
    else:
        print("   ❌ NO WORKING ENDPOINTS FOUND")
        print("   This could mean:")
        print("     1. API key is invalid/expired")
        print("     2. BrightData uses different authentication")
        print("     3. Different base URL is required")
        print("     4. Account needs activation")
        print()
        print("   🔧 NEXT STEPS:")
        print("     1. Check BrightData dashboard for API documentation")
        print("     2. Verify account is active and has API access")
        print("     3. Contact BrightData support for correct API endpoints")

if __name__ == "__main__":
    test_brightdata_api_key()