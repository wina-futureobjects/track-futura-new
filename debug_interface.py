#!/usr/bin/env python3
"""
Interface Debug Test - Debug your frontend connection to BrightData
"""

import requests
import json

def debug_interface_connection():
    """Debug the connection between your interface and BrightData API"""
    
    print("🐛 DEBUGGING INTERFACE CONNECTION TO BRIGHTDATA")
    print("=" * 60)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test 1: Check if your interface can reach the trigger endpoint
    print("\n1. 🔍 TESTING TRIGGER ENDPOINT DIRECTLY...")
    try:
        test_payload = {
            "platform": "instagram",
            "urls": ["https://www.instagram.com/nike/"]
        }
        
        response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ ENDPOINT WORKING! Your interface should be able to connect!")
                print(f"   📊 Batch Job: {data.get('batch_job_id')}")
                print(f"   📊 Dataset: {data.get('dataset_id')}")
            else:
                print(f"   ❌ ENDPOINT ERROR: {data.get('error')}")
        else:
            print(f"   ❌ HTTP ERROR: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ CONNECTION ERROR: {e}")
    
    # Test 2: Check common interface issues
    print("\n2. 🔍 CHECKING COMMON INTERFACE ISSUES...")
    
    # Test CORS
    print("\n   a) CORS Headers Check:")
    try:
        response = requests.options(f"{base_url}/api/brightdata/trigger-scraper/")
        print(f"      OPTIONS Status: {response.status_code}")
        cors_headers = {k: v for k, v in response.headers.items() if 'cors' in k.lower() or 'access-control' in k.lower()}
        if cors_headers:
            print(f"      CORS Headers: {cors_headers}")
        else:
            print("      ⚠️  No CORS headers found - this might cause browser issues")
    except Exception as e:
        print(f"      CORS Check Error: {e}")
    
    # Test Authentication
    print("\n   b) Authentication Check:")
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json={"platform": "instagram", "urls": ["https://www.instagram.com/test/"]},
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test-token"  # Test with auth header
            },
            timeout=15
        )
        print(f"      Auth Test Status: {response.status_code}")
        if response.status_code == 401:
            print("      ⚠️  Endpoint requires authentication")
        elif response.status_code == 200:
            print("      ✅ No authentication required")
    except Exception as e:
        print(f"      Auth Check Error: {e}")
    
    # Test 3: Show exact interface code needed
    print("\n3. 💻 EXACT CODE FOR YOUR INTERFACE:")
    print("-" * 50)
    
    print("JavaScript/Frontend:")
    print("""
    const triggerScraper = async (platform, urls) => {
        try {
            const response = await fetch('https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    platform: platform,
                    urls: urls
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log('✅ Scraper triggered!', data);
                return data;
            } else {
                console.error('❌ Scraper failed:', data.error);
                return null;
            }
        } catch (error) {
            console.error('❌ Connection error:', error);
            return null;
        }
    };
    
    // Usage:
    triggerScraper('instagram', ['https://www.instagram.com/nike/']);
    """)
    
    print("\n" + "=" * 60)
    print("🎯 DEBUGGING SUMMARY:")
    print("If the direct test above shows ✅ SUCCESS, then:")
    print("1. The BrightData integration is working perfectly")
    print("2. The issue is in your frontend/interface code")
    print("3. Use the exact JavaScript code above in your interface")
    print("4. Check browser console for any errors")
    print("5. Make sure your interface is using the correct URL and payload format")
    
    print("\n📋 WHAT TO CHECK IN YOUR INTERFACE:")
    print("• Are you using the correct endpoint URL?")
    print("• Are you sending the correct JSON payload format?")
    print("• Are there any CORS errors in browser console?")
    print("• Are you handling the response correctly?")
    print("• Is your interface sending Content-Type: application/json header?")

if __name__ == "__main__":
    debug_interface_connection()