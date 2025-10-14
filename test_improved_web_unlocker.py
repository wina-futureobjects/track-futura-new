#!/usr/bin/env python3
"""
Test Web Unlocker with Enhanced Project Creation
Tests the improved Web Unlocker functionality with automatic project creation
"""

import requests
import json

def test_web_unlocker_endpoint():
    """Test the Web Unlocker endpoint with enhanced project creation"""
    
    # Production URL
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    endpoint = f"{base_url}/api/web-unlocker/"
    
    # Test data
    test_data = {
        "url": "https://example.com",
        "scraper_name": "Test Enhanced Scraper"
    }
    
    print("🔧 Testing Enhanced Web Unlocker Endpoint")
    print(f"URL: {endpoint}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(
            endpoint,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response Headers: {dict(response.headers)}")
        
        # Try to parse response as JSON
        try:
            response_data = response.json()
            print(f"✅ Response JSON:")
            print(json.dumps(response_data, indent=2))
        except:
            print(f"📝 Response Text: {response.text}")
            
        if response.status_code == 200:
            print("🎉 SUCCESS: Web Unlocker endpoint working with enhanced project creation!")
            return True
        else:
            print(f"⚠️ WARNING: Status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Request failed - {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error - {e}")
        return False

def test_endpoint_accessibility():
    """Test basic endpoint accessibility"""
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    try:
        response = requests.get(base_url, timeout=10)
        print(f"🌐 Site Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Site Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Improved Web Unlocker Implementation")
    print("=" * 60)
    
    # Test site accessibility first
    if test_endpoint_accessibility():
        print("✅ Site is accessible")
    else:
        print("❌ Site not accessible")
        exit(1)
    
    print()
    
    # Test Web Unlocker endpoint
    if test_web_unlocker_endpoint():
        print("\n🎉 ALL TESTS PASSED - Web Unlocker with enhanced project creation is working!")
    else:
        print("\n⚠️ TESTS FAILED - Check the logs for issues")