#!/usr/bin/env python3
"""
BRIGHTDATA API AUTHENTICATION TESTER
=====================================
Tests different authentication methods with the discovered working endpoints.
"""

import requests
import json
import base64
from typing import Dict, Any

# Your BrightData credentials
SCRAPER_ID = "hl_f7614f18"
API_TOKEN = "8af6995e-3baa-4b69-9df7-8d7671e621eb"

def test_working_endpoints():
    """Test the endpoints that returned 401 (meaning they exist)"""
    print("🎯 TESTING WORKING ENDPOINTS WITH DIFFERENT AUTH...")
    
    working_endpoints = [
        "https://api.brightdata.com/status",
        "https://api.brightdata.com/datasets",
        "https://brightdata.com/api/status"
    ]
    
    # Test different authentication methods
    auth_methods = [
        # Basic Auth variants
        {"Authorization": f"Basic {base64.b64encode(f'{API_TOKEN}:'.encode()).decode()}"},
        {"Authorization": f"Basic {base64.b64encode(f':{API_TOKEN}'.encode()).decode()}"},
        {"Authorization": f"Basic {base64.b64encode(f'{SCRAPER_ID}:{API_TOKEN}'.encode()).decode()}"},
        
        # Bearer token variants
        {"Authorization": f"Bearer {API_TOKEN}"},
        {"Authorization": f"bearer {API_TOKEN}"},
        
        # API Key variants
        {"X-API-Key": API_TOKEN},
        {"Api-Key": API_TOKEN},
        {"API_KEY": API_TOKEN},
        
        # Custom headers that BrightData might use
        {"X-Brightdata-Auth": API_TOKEN},
        {"Brightdata-Token": API_TOKEN},
        {"X-Auth-Token": API_TOKEN},
        
        # Query parameter instead of header
        {},  # Will add token as query param
    ]
    
    for endpoint in working_endpoints:
        print(f"\n🌐 Testing endpoint: {endpoint}")
        
        for i, auth in enumerate(auth_methods):
            try:
                # Test with headers
                if auth:
                    response = requests.get(endpoint, headers=auth, timeout=10)
                    auth_desc = str(auth)
                else:
                    # Test with query parameter
                    response = requests.get(f"{endpoint}?api_token={API_TOKEN}", timeout=10)
                    auth_desc = "Query parameter: api_token"
                
                print(f"   🧪 {auth_desc[:50]}... -> Status: {response.status_code}")
                
                # If we get something other than 401/404, it might be working!
                if response.status_code not in [401, 404, 403]:
                    print(f"      🎉 POTENTIAL SUCCESS! Response: {response.text[:200]}")
                    
                # Check for specific error messages that might help
                if response.status_code == 401:
                    try:
                        error_data = response.json()
                        if "error" in error_data:
                            print(f"      🔍 Error details: {error_data['error']}")
                    except:
                        if "auth" in response.text.lower() or "token" in response.text.lower():
                            print(f"      🔍 Auth hint: {response.text[:100]}")
                            
            except Exception as e:
                print(f"   💥 {str(auth)[:30]}... -> Error: {str(e)[:100]}")

def test_dataset_specific_endpoints():
    """Test endpoints specific to your scraper ID"""
    print(f"\n🎯 TESTING SCRAPER-SPECIFIC ENDPOINTS...")
    
    # Endpoints that might work with proper auth
    endpoints = [
        f"https://api.brightdata.com/datasets/{SCRAPER_ID}",
        f"https://api.brightdata.com/datasets/v3/{SCRAPER_ID}",
        f"https://api.brightdata.com/scrapers/{SCRAPER_ID}", 
        f"https://api.brightdata.com/collections/{SCRAPER_ID}",
        f"https://brightdata.com/api/datasets/{SCRAPER_ID}",
    ]
    
    # Use the most promising auth method
    auth_headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, headers=auth_headers, timeout=10)
            print(f"   🧪 {endpoint} -> Status: {response.status_code}")
            
            if response.status_code == 401:
                # Check for specific error messages
                try:
                    error_data = response.json()
                    print(f"      🔍 Error: {error_data}")
                except:
                    print(f"      🔍 Response: {response.text[:200]}")
                    
        except Exception as e:
            print(f"   💥 {endpoint} -> Error: {str(e)[:100]}")

def test_brightdata_documentation_examples():
    """Test endpoints based on common BrightData API patterns"""
    print(f"\n📚 TESTING COMMON BRIGHTDATA API PATTERNS...")
    
    # Common patterns from BrightData docs
    patterns = [
        # Dataset API patterns
        f"https://api.brightdata.com/dca/dataset/{SCRAPER_ID}",
        f"https://api.brightdata.com/dca/datasets/{SCRAPER_ID}",
        f"https://api.brightdata.com/dca/dataset/{SCRAPER_ID}/download",
        f"https://api.brightdata.com/dca/dataset/{SCRAPER_ID}/run",
        f"https://api.brightdata.com/dca/dataset/{SCRAPER_ID}/trigger",
        
        # Web Scraper API patterns  
        f"https://api.brightdata.com/dca/trigger?collector={SCRAPER_ID}",
        f"https://api.brightdata.com/dca/trigger_immediate?collector={SCRAPER_ID}",
        
        # Alternative formats
        f"https://api.brightdata.com/v1/scrapers/{SCRAPER_ID}/run",
        f"https://api.brightdata.com/v2/datasets/{SCRAPER_ID}/trigger",
    ]
    
    auth_headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    for pattern in patterns:
        try:
            response = requests.get(pattern, headers=auth_headers, timeout=10)
            print(f"   🧪 {pattern} -> Status: {response.status_code}")
            
            if response.status_code not in [404, 401]:
                print(f"      🎉 NON-ERROR RESPONSE: {response.text[:200]}")
                
        except Exception as e:
            if "404" not in str(e):
                print(f"   💥 {pattern} -> Error: {str(e)[:100]}")

def suggest_brightdata_dashboard_check():
    """Provide instructions for checking BrightData dashboard"""
    print(f"\n🎯 BRIGHTDATA DASHBOARD VERIFICATION STEPS:")
    print("=" * 50)
    print("1. 🌐 Go to: https://brightdata.com/cp/zones")
    print("2. 🔍 Look for your scraper/dataset with ID: hl_f7614f18")
    print("3. 📋 Verify this ID exists in your account")
    print("4. 🔑 Check API credentials section for correct token format")
    print("5. 📚 Look for API documentation or examples in your dashboard")
    print("6. 🚀 Try running a test scrape directly from the dashboard")
    print()
    print("🔍 WHAT TO LOOK FOR:")
    print("   - Exact scraper/dataset ID")
    print("   - Current API token")
    print("   - API endpoint format")
    print("   - Authentication method")
    print("   - Status of the scraper (active/inactive)")

if __name__ == "__main__":
    print("🎯 BRIGHTDATA API AUTHENTICATION TESTER")
    print("=" * 50)
    
    test_working_endpoints()
    test_dataset_specific_endpoints()
    test_brightdata_documentation_examples()
    suggest_brightdata_dashboard_check()
    
    print("\n✅ AUTHENTICATION TESTING COMPLETE")
    print("\n🚨 NEXT STEPS:")
    print("1. Check your BrightData dashboard to verify scraper ID")
    print("2. Confirm API token is current and has proper permissions")
    print("3. Look for specific API format in BrightData documentation")
    print("4. Contact BrightData support if authentication continues to fail")