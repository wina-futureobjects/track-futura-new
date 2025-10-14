#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_production_web_unlocker():
    """
    Test Web Unlocker API on production server
    """
    
    print("🧪 Testing Production Web Unlocker API...")
    print("=" * 50)
    
    # Production URL
    base_url = "https://trackfutura.futureobjects.io"
    
    # Test data
    test_data = {
        'url': 'https://example.com',
        'folder_name': 'Production Web Unlocker Test'
    }
    
    try:
        # Test Web Unlocker endpoint
        print(f"📡 Testing: {base_url}/api/web-unlocker/")
        print(f"📋 Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{base_url}/api/web-unlocker/",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Web Unlocker API working on production!")
            print(f"📁 Created folder: {result.get('folder_name')} (ID: {result.get('folder_id')})")
            print(f"🌐 Scraped URL: {result.get('url')}")
            print(f"📄 Content length: {len(result.get('content', ''))}")
            
            # Test dashboard access
            print("\n🔍 Testing Dashboard Access...")
            dashboard_response = requests.get(f"{base_url}/", timeout=10)
            
            if dashboard_response.status_code == 200:
                print("✅ Dashboard accessible!")
                print(f"📏 Dashboard size: {len(dashboard_response.text)} bytes")
            else:
                print(f"⚠️ Dashboard status: {dashboard_response.status_code}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"🔌 Connection Error: {e}")
    except Exception as e:
        print(f"💥 Unexpected Error: {e}")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_production_web_unlocker()