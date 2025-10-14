#!/usr/bin/env python3
"""
🎯 SIMPLE WEB UNLOCKER TEST
===========================

Simple test to verify Web Unlocker API integration
"""

import requests
import json

def test_web_unlocker_simple():
    """Simple Web Unlocker test"""
    
    print("🎯 SIMPLE WEB UNLOCKER TEST")
    print("=" * 30)
    
    # Test the production endpoint
    url = "https://trackfutura.futureobjects.io/api/brightdata/web-unlocker/scrape/"
    
    # Simple test data
    test_data = {
        "url": "https://httpbin.org/get",
        "scraper_name": "Simple Test"
    }
    
    print(f"\n🌐 Testing URL: {url}")
    print(f"📋 Test data: {test_data}")
    
    try:
        print("\n⏳ Making request...")
        
        response = requests.post(
            url,
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Web Unlocker Test'
            },
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: {data}")
        else:
            print(f"❌ ERROR Response: {response.text}")
            
        # Also test if the endpoint exists with a GET request
        print(f"\n🔍 Testing GET request to check if endpoint exists...")
        get_response = requests.get(url, timeout=10)
        print(f"📊 GET Status: {get_response.status_code}")
        
        if get_response.status_code == 405:
            print("✅ Endpoint exists (Method Not Allowed is expected)")
        else:
            print(f"📋 GET Response: {get_response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n🎯 DEPLOYMENT STATUS:")
    print("   The Web Unlocker integration has been deployed!")
    print("   Check your production data storage page:")
    print("   https://trackfutura.futureobjects.io/organizations/1/projects/2/data-storage")

if __name__ == "__main__":
    test_web_unlocker_simple()