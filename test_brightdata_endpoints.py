#!/usr/bin/env python
"""
Test different BrightData API endpoint formats
"""
import requests

def test_brightdata_endpoints():
    api_token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
    scraper_id = 'hl_f7614f18'
    
    # Test payload
    payload = {
        "url": "https://www.instagram.com/nike/"
    }
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # Try different endpoint formats
    endpoints = [
        f"https://api.brightdata.com/datasets/v3/{scraper_id}/trigger",
        f"https://api.brightdata.com/scrapers/{scraper_id}/trigger",
        f"https://brightdata.com/api/scrapers/{scraper_id}/trigger",
        f"https://brightdata.com/api/collectors/{scraper_id}/trigger",
        f"https://api.brightdata.com/collectors/{scraper_id}/trigger",
        f"https://api.brightdata.com/datasets/{scraper_id}/trigger",
    ]
    
    for url in endpoints:
        print(f"\n🧪 Testing: {url}")
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
            if response.status_code != 404:
                print(f"✅ Found working endpoint: {url}")
                return url
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("❌ No working endpoint found")
    return None

if __name__ == '__main__':
    print("🚀 Testing BrightData API endpoints...")
    working_endpoint = test_brightdata_endpoints()
    
    if working_endpoint:
        print(f"\n✅ Use this endpoint: {working_endpoint}")
    else:
        print("\n❌ Need to check BrightData documentation for correct API format")