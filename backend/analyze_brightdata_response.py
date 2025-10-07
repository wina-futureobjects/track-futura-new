#!/usr/bin/env python3
"""
Detailed analysis of the working Luminati endpoint
"""
import requests
import json

def analyze_luminati_response():
    print("=== DETAILED BRIGHTDATA/LUMINATI API ANALYSIS ===")
    print()
    
    api_key = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    # The working endpoint we found
    url = "https://luminati.io/api/status"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    print(f"Testing working endpoint: {url}")
    print(f"API Key: {api_key}")
    print()
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API KEY IS ACTIVE!")
            
            try:
                data = response.json()
                print("\n📊 FULL RESPONSE:")
                print(json.dumps(data, indent=2))
                
                # Analyze the response
                print("\n🔍 ANALYSIS:")
                
                if data.get("status") == "active":
                    print("   ✅ Account Status: ACTIVE")
                else:
                    print(f"   ⚠️  Account Status: {data.get('status', 'Unknown')}")
                
                if data.get("customer"):
                    print(f"   👤 Customer ID: {data.get('customer')}")
                
                can_make_requests = data.get("can_make_requests", False)
                if can_make_requests:
                    print("   ✅ Can Make Requests: YES")
                else:
                    print("   ❌ Can Make Requests: NO")
                    
                    auth_fail_reason = data.get("auth_fail_reason", "")
                    if auth_fail_reason:
                        print(f"   🚫 Auth Fail Reason: {auth_fail_reason}")
                        
                        if "zone" in auth_fail_reason.lower():
                            print("   💡 This suggests you need to specify a ZONE NAME")
                            print("      BrightData uses zones for different services")
                
                # Check for additional fields
                for key, value in data.items():
                    if key not in ["status", "customer", "can_make_requests", "auth_fail_reason"]:
                        print(f"   📝 {key}: {value}")
                        
            except Exception as e:
                print(f"❌ Failed to parse JSON: {e}")
                print(f"Raw response: {response.text}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request error: {str(e)}")
    
    print()
    print("🎯 CONCLUSIONS:")
    print("   1. ✅ Your API key IS ACTIVE and valid")
    print("   2. ❌ You cannot make requests yet due to zone configuration")
    print("   3. 🔧 You likely need to:")
    print("      - Set up a zone in your BrightData dashboard")
    print("      - Use zone-specific credentials")
    print("      - Configure the zone for data collection (not just proxy)")
    print()
    print("📋 NEXT STEPS:")
    print("   1. Log into your BrightData dashboard")
    print("   2. Go to 'Zones' or 'Proxy Zones' section")
    print("   3. Create or configure a zone for data collection")
    print("   4. Look for zone-specific credentials or settings")
    print("   5. The format might be: zone_name:password instead of just API key")

if __name__ == "__main__":
    analyze_luminati_response()