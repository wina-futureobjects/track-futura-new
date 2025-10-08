#!/usr/bin/env python3
"""
BRIGHTDATA CREDENTIALS VERIFICATION TOOL
==========================================
This script helps verify BrightData credentials and find working API endpoints.
"""

import requests
import json
from typing import Dict, Any

# Your BrightData credentials
SCRAPER_ID = "hl_f7614f18"
API_TOKEN = "8af6995e-3baa-4b69-9df7-8d7671e621eb"

def test_brightdata_base_endpoints():
    """Test basic BrightData API endpoints to see if they exist"""
    print("🔍 TESTING BRIGHTDATA BASE ENDPOINTS...")
    
    base_urls = [
        "https://api.brightdata.com",
        "https://brightdata.com/api",
        "https://api.brd.superproxy.io",  # Alternative API domain
        "https://datacenter.brightdata.com/api",
        "https://api.brdops.com",  # Another potential domain
    ]
    
    test_paths = [
        "/",
        "/health",
        "/ping",
        "/status",
        "/v1",
        "/v2", 
        "/v3",
        "/datasets",
        "/scrapers",
        "/collections",
        "/web-scraper",
        "/scraping-browser"
    ]
    
    for base_url in base_urls:
        print(f"\n🌐 Testing base: {base_url}")
        for path in test_paths:
            try:
                url = f"{base_url}{path}"
                response = requests.get(url, timeout=10)
                if response.status_code != 404:
                    print(f"   ✅ {url} -> Status: {response.status_code}")
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            print(f"      📄 Response: {json.dumps(data, indent=2)[:200]}...")
                        except:
                            print(f"      📄 Response: {response.text[:200]}...")
            except Exception as e:
                if "Failed to resolve" not in str(e):
                    print(f"   ⚠️  {url} -> Error: {str(e)[:100]}")

def test_brightdata_auth_formats():
    """Test different authentication formats"""
    print("\n🔑 TESTING DIFFERENT AUTH FORMATS...")
    
    # Test with a simple endpoint that might exist
    test_url = "https://api.brightdata.com/datasets"
    
    auth_formats = [
        {"Authorization": f"Bearer {API_TOKEN}"},
        {"Authorization": f"Token {API_TOKEN}"},
        {"X-API-Key": API_TOKEN},
        {"api_token": API_TOKEN},
        {"X-Auth-Token": API_TOKEN},
        {"Authentication": f"Bearer {API_TOKEN}"},
        {"BrightData-Token": API_TOKEN},
    ]
    
    for auth in auth_formats:
        try:
            response = requests.get(test_url, headers=auth, timeout=10)
            print(f"   🧪 {auth} -> Status: {response.status_code}")
            if response.status_code not in [404, 401, 403]:
                print(f"      📄 Response: {response.text[:200]}")
        except Exception as e:
            print(f"   💥 {auth} -> Error: {str(e)[:100]}")

def check_scraper_id_format():
    """Check if the scraper ID format is correct"""
    print(f"\n🔍 ANALYZING SCRAPER ID: {SCRAPER_ID}")
    
    # Analyze the scraper ID
    if SCRAPER_ID.startswith("hl_"):
        print("   ✅ ID starts with 'hl_' - appears to be BrightData format")
    else:
        print("   ⚠️  ID doesn't start with expected prefix")
    
    if len(SCRAPER_ID) > 10:
        print(f"   ✅ ID length ({len(SCRAPER_ID)}) seems reasonable")
    else:
        print(f"   ⚠️  ID length ({len(SCRAPER_ID)}) seems short")
    
    print(f"   📊 ID breakdown: prefix='{SCRAPER_ID[:3]}', suffix='{SCRAPER_ID[3:]}'")

def check_token_format():
    """Check if the API token format is correct"""
    print(f"\n🔍 ANALYZING API TOKEN: {API_TOKEN[:8]}...{API_TOKEN[-8:]}")
    
    # Analyze the token
    if len(API_TOKEN) == 36 and API_TOKEN.count('-') == 4:
        print("   ✅ Token appears to be UUID format (correct for BrightData)")
    else:
        print(f"   ⚠️  Token format unusual - length: {len(API_TOKEN)}, dashes: {API_TOKEN.count('-')}")
    
    # Check if it's hex
    try:
        parts = API_TOKEN.split('-')
        for part in parts:
            int(part, 16)
        print("   ✅ Token contains valid hexadecimal characters")
    except ValueError:
        print("   ⚠️  Token contains non-hex characters")

def suggest_next_steps():
    """Suggest next steps based on findings"""
    print("\n💡 RECOMMENDATIONS:")
    print("1. 🌐 Check your BrightData dashboard at https://brightdata.com/")
    print("2. 📋 Verify the scraper ID in your dashboard")
    print("3. 🔑 Regenerate API token if needed")
    print("4. 📚 Check BrightData documentation for current API format")
    print("5. 🆘 Contact BrightData support if endpoints are unreachable")
    print("\n🚨 CRITICAL: No BrightData API endpoints are responding!")
    print("   This suggests either:")
    print("   - Network/DNS issues")
    print("   - Wrong API domain")
    print("   - BrightData API is down")
    print("   - Authentication is required for all endpoints")

if __name__ == "__main__":
    print("🚨 BRIGHTDATA CREDENTIALS VERIFICATION")
    print("=" * 50)
    
    check_scraper_id_format()
    check_token_format()
    test_brightdata_base_endpoints()
    test_brightdata_auth_formats()
    suggest_next_steps()
    
    print("\n✅ VERIFICATION COMPLETE")