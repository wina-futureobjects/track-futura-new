#!/usr/bin/env python3
"""
Production deployment verification script - test basic BrightData endpoints
"""

import requests
import time
import sys

# Configuration
BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
API_BASE = f"{BASE_URL}/api"

def test_basic_endpoints():
    """Test basic API endpoints to verify deployment"""
    print("🔍 TESTING BASIC API ENDPOINTS")
    print("=" * 50)
    
    # Test health check
    print("\n📋 Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/health/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test BrightData API base
    print("\n📋 Testing BrightData API base...")
    try:
        response = requests.get(f"{API_BASE}/brightdata/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 403, 405]:  # 405 = Method Not Allowed is OK for GET on API root
            print(f"   ✅ BrightData API endpoint is responding")
            if hasattr(response, 'text') and len(response.text) < 1000:
                print(f"   Response snippet: {response.text[:200]}...")
        else:
            print(f"   ❌ BrightData API not responding properly")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test existing brightdata endpoints
    print("\n📋 Testing existing BrightData endpoints...")
    existing_endpoints = [
        "/brightdata/configs/",
        "/brightdata/batch-jobs/", 
        "/brightdata/scraper-requests/"
    ]
    
    for endpoint in existing_endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            print(f"   {endpoint}: Status {response.status_code}")
            if response.status_code in [200, 401, 403]:  # These are "good" responses
                print(f"     ✅ Endpoint is deployed")
            else:
                print(f"     ❌ Endpoint issue")
        except Exception as e:
            print(f"     ❌ Error: {e}")

def test_new_endpoints():
    """Test our new data-storage endpoints with sample data"""
    print("\n🆕 TESTING NEW DATA-STORAGE ENDPOINTS")
    print("=" * 50)
    
    # Test endpoints that should exist (from our local testing)
    test_cases = [
        {
            'name': 'Job 3 folder (has data)',
            'url': f"{API_BASE}/brightdata/data-storage/Job%203/1/",
            'expected': 'Should return scraped data'
        },
        {
            'name': 'Nike folder (might be empty)',
            'url': f"{API_BASE}/brightdata/data-storage/nike/1/",
            'expected': 'Should return empty or data'
        },
        {
            'name': 'Non-existent folder',
            'url': f"{API_BASE}/brightdata/data-storage/nonexistent/1/",
            'expected': 'Should return folder not found error'
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        print(f"   URL: {test_case['url']}")
        print(f"   Expected: {test_case['expected']}")
        
        try:
            response = requests.get(test_case['url'], timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'success' in data:
                        print(f"   ✅ Success: {data.get('success')}")
                        if 'message' in data:
                            print(f"   Message: {data['message']}")
                        if 'data' in data and isinstance(data['data'], list):
                            print(f"   Data count: {len(data['data'])} items")
                    else:
                        print(f"   ⚠️ Unexpected response format")
                except:
                    print(f"   ⚠️ Non-JSON response: {response.text[:200]}...")
            elif response.status_code == 404:
                print(f"   ❌ 404 - Endpoint not found or folder doesn't exist")
            elif response.status_code == 500:
                print(f"   ❌ 500 - Server error, likely code issue")
            else:
                print(f"   ⚠️ Other status: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Connection error: {e}")

def check_deployment_status():
    """Check if deployment is complete and ready"""
    print("🚀 CHECKING DEPLOYMENT STATUS")
    print("=" * 50)
    
    # Sometimes Platform.sh takes a few minutes to fully deploy
    print("\nℹ️ Note: Platform.sh deployments can take a few minutes to fully propagate")
    print("If you're seeing 404s on new endpoints, try again in 2-3 minutes")
    
    print(f"\n🌐 Base URL: {BASE_URL}")
    print(f"🔗 API Base: {API_BASE}")
    
    # Basic connectivity test
    try:
        response = requests.get(BASE_URL, timeout=10)
        print(f"\n✅ Site is accessible (Status: {response.status_code})")
    except Exception as e:
        print(f"\n❌ Site connection error: {e}")

if __name__ == "__main__":
    print("🔍 PRODUCTION DEPLOYMENT VERIFICATION")
    print("=" * 60)
    print("Testing the new human-friendly data storage endpoints...")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    check_deployment_status()
    test_basic_endpoints()
    test_new_endpoints()
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. If 404s persist, wait 2-3 minutes and rerun this script")
    print("2. If endpoints work, test with your actual folder names")
    print("3. Check folder names in production database if needed")
    print("=" * 60)