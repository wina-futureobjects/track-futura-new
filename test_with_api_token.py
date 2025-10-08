#!/usr/bin/env python3
"""
Direct API Token Update Script
Uses the BrightData API key: 8af6995e-3baa-4b69-9df7-8d7671e621eb
"""

import requests
import json
import time

def update_tokens_directly():
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    print("🔧 UPDATING BRIGHTDATA API TOKENS")
    print("=" * 50)
    print(f"Using API token: {api_token}")
    
    # Test with longer timeout
    print("\n1. Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/health/", timeout=30)
        print(f"   Health status: {response.status_code} ✅")
    except requests.exceptions.Timeout:
        print("   ❌ Server timeout - trying alternative approach")
        return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False
    
    # Test scraper with the correct API token
    print("\n2. Testing scraper trigger with known good API token...")
    
    # Test Instagram
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json={
                "platform": "instagram",
                "urls": ["https://www.instagram.com/nike/"],
                "api_token": api_token  # Pass token directly if supported
            },
            headers={"Content-Type": "application/json"},
            timeout=45
        )
        
        print(f"   Instagram trigger status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Instagram response: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print("   ✅ INSTAGRAM SUCCESS! API integration working!")
            else:
                print(f"   ❌ Instagram failed: {data.get('error')}")
        else:
            print(f"   Instagram error: HTTP {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            
    except requests.exceptions.Timeout:
        print("   ❌ Instagram trigger timeout")
    except Exception as e:
        print(f"   ❌ Instagram error: {e}")
    
    # Test Facebook
    print("\n3. Testing Facebook scraper...")
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json={
                "platform": "facebook",
                "urls": ["https://www.facebook.com/nike"],
                "api_token": api_token  # Pass token directly if supported
            },
            headers={"Content-Type": "application/json"},
            timeout=45
        )
        
        print(f"   Facebook trigger status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Facebook response: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print("   ✅ FACEBOOK SUCCESS! API integration working!")
            else:
                print(f"   ❌ Facebook failed: {data.get('error')}")
        else:
            print(f"   Facebook error: HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ❌ Facebook trigger timeout")
    except Exception as e:
        print(f"   ❌ Facebook error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 API TOKEN DIAGNOSIS COMPLETE")
    print(f"📍 API Token Used: {api_token}")
    print("📍 If you see SUCCESS above, the integration is working!")
    print("📍 If not, we need to update the database configurations.")
    
    return True

if __name__ == "__main__":
    update_tokens_directly()