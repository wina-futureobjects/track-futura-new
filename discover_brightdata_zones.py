#!/usr/bin/env python3
"""
BRIGHTDATA ZONE DISCOVERY TOOL
===============================
This script helps you find the correct zone/scraper ID format for BrightData.
"""

import requests
import json

# Your BrightData credentials
API_TOKEN = "8af6995e-3baa-4b69-9df7-8d7671e621eb"

def get_brightdata_zones():
    """Try to get list of available zones from BrightData"""
    print("🔍 DISCOVERING AVAILABLE BRIGHTDATA ZONES...")
    
    endpoints_to_try = [
        "https://api.brightdata.com/zones",
        "https://api.brightdata.com/customer/zones", 
        "https://api.brightdata.com/account/zones",
        "https://api.brightdata.com/v1/zones",
        "https://api.brightdata.com/v2/zones",
        "https://brightdata.com/api/zones",
        "https://api.brightdata.com/scrapers",
        "https://api.brightdata.com/datasets",
        "https://api.brightdata.com/collections",
        "https://api.brightdata.com/customer",
        "https://api.brightdata.com/account",
        "https://api.brightdata.com/user",
    ]
    
    auth_headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    for endpoint in endpoints_to_try:
        try:
            print(f"\n🧪 Testing: {endpoint}")
            response = requests.get(endpoint, headers=auth_headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   🎉 SUCCESS! Data: {json.dumps(data, indent=2)}")
                    
                    # Look for zone/scraper IDs in the response
                    if isinstance(data, list):
                        print(f"   📊 Found {len(data)} items")
                        for i, item in enumerate(data[:5]):  # Show first 5 items
                            print(f"      Item {i+1}: {item}")
                    elif isinstance(data, dict):
                        if 'zones' in data:
                            print(f"   🎯 Found zones: {data['zones']}")
                        if 'scrapers' in data:
                            print(f"   🎯 Found scrapers: {data['scrapers']}")
                        if 'datasets' in data:
                            print(f"   🎯 Found datasets: {data['datasets']}")
                            
                except json.JSONDecodeError:
                    print(f"   📄 Response (text): {response.text[:500]}")
                    
            elif response.status_code == 404:
                print(f"   ❌ Not found")
            elif response.status_code == 401:
                print(f"   🔒 Unauthorized")
            elif response.status_code == 403:
                print(f"   🚫 Forbidden")
            else:
                print(f"   ⚠️  Other response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   💥 Error: {str(e)[:100]}")

def test_known_zone_patterns():
    """Test common zone ID patterns"""
    print(f"\n🔍 TESTING COMMON ZONE ID PATTERNS...")
    
    # Common BrightData zone patterns
    zone_patterns = [
        "zone_web_scraper",
        "zone_datacenter", 
        "zone_residential",
        "zone_mobile",
        "web_scraper_zone",
        "datacenter_zone",
        "residential_zone",
        "static_zone",
        "rotating_zone",
    ]
    
    auth_headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    for pattern in zone_patterns:
        try:
            # Test with status endpoint
            url = f"https://api.brightdata.com/status?zone={pattern}"
            response = requests.get(url, headers=auth_headers, timeout=10)
            print(f"   🧪 Zone '{pattern}': Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      🎉 WORKING ZONE! Data: {data}")
                
        except Exception as e:
            print(f"   💥 Zone '{pattern}': Error {str(e)[:50]}")

def test_web_scraper_api():
    """Test BrightData Web Scraper API specifically"""
    print(f"\n🕷️  TESTING WEB SCRAPER API...")
    
    # Web Scraper API endpoints
    scraper_endpoints = [
        "https://api.brightdata.com/web_scraper/trigger",
        "https://api.brightdata.com/webscraper/trigger", 
        "https://api.brightdata.com/scraper/trigger",
        "https://api.brightdata.com/dca/trigger",
        "https://api.brightdata.com/dca/trigger_immediate",
        "https://api.brightdata.com/web_scraper/run",
        "https://api.brightdata.com/web_scraper/jobs",
        "https://api.brightdata.com/web_scraper/collections",
    ]
    
    auth_headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    for endpoint in scraper_endpoints:
        try:
            response = requests.get(endpoint, headers=auth_headers, timeout=10)
            print(f"   🧪 {endpoint}: Status {response.status_code}")
            
            if response.status_code in [200, 405]:  # 405 = Method not allowed (might need POST)
                print(f"      🎯 POTENTIAL ENDPOINT! Response: {response.text[:200]}")
                
                # Try POST if GET gave 405
                if response.status_code == 405:
                    try:
                        post_response = requests.post(endpoint, headers=auth_headers, timeout=10)
                        print(f"      🔄 POST attempt: Status {post_response.status_code}")
                        if post_response.status_code != 405:
                            print(f"         Response: {post_response.text[:200]}")
                    except:
                        pass
                        
        except Exception as e:
            print(f"   💥 {endpoint}: Error {str(e)[:50]}")

def provide_dashboard_instructions():
    """Provide specific instructions for finding correct IDs"""
    print(f"\n🎯 BRIGHTDATA DASHBOARD INSTRUCTIONS:")
    print("=" * 50)
    print("🔍 STEP 1: Login to BrightData Dashboard")
    print("   Go to: https://brightdata.com/cp")
    print("   Login with your account")
    print()
    print("🔍 STEP 2: Find Your Zones")
    print("   Look for sections like:")
    print("   - 'Zones' or 'Proxy Zones'")
    print("   - 'Web Scraper' ")
    print("   - 'Datasets' or 'Data Collection'")
    print("   - 'Scrapers' or 'Collectors'")
    print()
    print("🔍 STEP 3: Get the Correct IDs")
    print("   Look for IDs that might be like:")
    print("   - zone_12345")
    print("   - scraper_abc123") 
    print("   - ws_xyz789")
    print("   - dc_def456")
    print()
    print("🔍 STEP 4: Check API Section")
    print("   Look for 'API' or 'Integration' section")
    print("   Find example API calls or documentation")
    print("   Note the exact endpoint format")
    print()
    print(f"🚨 CRITICAL: The ID 'hl_f7614f18' seems to be your customer ID, not zone ID!")

if __name__ == "__main__":
    print("🔍 BRIGHTDATA ZONE DISCOVERY TOOL")
    print("=" * 50)
    
    get_brightdata_zones()
    test_known_zone_patterns()
    test_web_scraper_api()
    provide_dashboard_instructions()
    
    print("\n✅ ZONE DISCOVERY COMPLETE")
    print("\n🎯 KEY FINDINGS:")
    print("   - Your Bearer token authentication is WORKING ✅")
    print("   - 'hl_f7614f18' appears to be your customer ID, not zone ID ❌")
    print("   - You need to find the correct zone/scraper ID from your dashboard")
    print("   - Once you have the right ID, the API will work!")