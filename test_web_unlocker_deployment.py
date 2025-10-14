#!/usr/bin/env python3
"""
Simple Web Unlocker endpoint test to validate deployment
"""
import requests
import json
import time

def test_web_unlocker_endpoint():
    """Test the deployed Web Unlocker endpoint"""
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test basic site first
    print("🌐 Testing basic site connectivity...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"✅ Site status: {response.status_code}")
    except Exception as e:
        print(f"❌ Site connectivity failed: {e}")
        return False
    
    # Test Web Unlocker endpoint
    print("\n🔓 Testing Web Unlocker endpoint...")
    
    endpoint_url = f"{base_url}/api/brightdata/web-unlocker/scrape/"
    
    test_data = {
        "url": "https://httpbin.org/json",
        "scraper_name": "Deployment Test"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📡 Making request to: {endpoint_url}")
        print(f"📦 Payload: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            endpoint_url,
            headers=headers,
            json=test_data,
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print(f"📝 Response Content: {response.text}")
        
        if response.status_code == 200:
            print("✅ Web Unlocker endpoint is working!")
            return True
        else:
            print(f"⚠️ Endpoint returned error status: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (this might be normal for Web Unlocker processing)")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_web_unlocker_endpoint()
    
    if success:
        print("\n🎉 Web Unlocker integration deployed successfully!")
    else:
        print("\n🔧 Web Unlocker endpoint needs investigation")