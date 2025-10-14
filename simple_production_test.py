#!/usr/bin/env python3
"""
Simple Production Deployment Test
================================
Tests the main deployment URL and reports status
"""
import requests
import sys

def test_production_deployment():
    url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/"
    
    print("🔍 Testing Production Deployment...")
    print(f"URL: {url}")
    print("-" * 50)
    
    try:
        response = requests.get(url, timeout=30)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("🎉 DEPLOYMENT SUCCESSFUL!")
            print(f"Content Length: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Deployment Issue - Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {str(e)}")
        return False

def test_api_endpoints():
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    endpoints = [
        "/api/track_accounts/unified_folders/",
        "/api/web-unlocker/scrape/",
        "/api/folders/"
    ]
    
    print("\n🔍 Testing API Endpoints...")
    print("-" * 50)
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)[:100]}")

if __name__ == "__main__":
    print("🚀 PRODUCTION DEPLOYMENT VERIFICATION")
    print("="*50)
    
    success = test_production_deployment()
    
    if success:
        test_api_endpoints()
        print("\n✅ All tests completed!")
    else:
        print("\n❌ Primary deployment test failed")
        sys.exit(1)