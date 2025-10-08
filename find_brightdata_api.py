#!/usr/bin/env python
"""
URGENT: Find the correct BrightData API format
"""
import requests
import json

def find_correct_brightdata_api():
    print("🔍 FINDING CORRECT BRIGHTDATA API FORMAT...")
    
    api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    scraper_id = "hl_f7614f18"
    
    # Try different base URLs and formats
    base_urls = [
        "https://api.brightdata.com",
        "https://brightdata.com/api",
        "https://app.brightdata.com/api",
        "https://datacenter.brightdata.com/api",
    ]
    
    api_paths = [
        f"/datasets/v3/{scraper_id}",
        f"/datasets/{scraper_id}",
        f"/scrapers/{scraper_id}",
        f"/collections/{scraper_id}",
        f"/v1/datasets/{scraper_id}",
        f"/v2/datasets/{scraper_id}",
        f"/web-scraper/{scraper_id}",
        f"/scraping-browser/{scraper_id}",
    ]
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # Also try different auth formats
    auth_formats = [
        {'Authorization': f'Bearer {api_token}'},
        {'Authorization': f'Token {api_token}'},
        {'X-API-Key': api_token},
        {'api_token': api_token},
    ]
    
    print("🧪 Testing different BrightData API combinations...")
    
    for base_url in base_urls:
        for path in api_paths:
            for auth_header in auth_formats:
                try:
                    full_url = f"{base_url}{path}"
                    print(f"\n🎯 Testing: {full_url}")
                    print(f"   Auth: {auth_header}")
                    
                    response = requests.get(full_url, headers=auth_header, timeout=5)
                    print(f"   Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"✅ SUCCESS! Found working endpoint!")
                        print(f"   Response: {response.text[:200]}...")
                        return full_url, auth_header
                    elif response.status_code == 401:
                        print(f"🔑 Auth issue: {response.text[:100]}...")
                    elif response.status_code != 404:
                        print(f"⚠️  Different error: {response.text[:100]}...")
                        
                except Exception as e:
                    print(f"   💥 Exception: {e}")
    
    return None, None

def check_brightdata_account_info():
    print("\n🔍 CHECKING BRIGHTDATA ACCOUNT INFO...")
    
    api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    # Try to get account info or list datasets
    account_endpoints = [
        "https://api.brightdata.com/datasets",
        "https://api.brightdata.com/user",
        "https://api.brightdata.com/account",
        "https://api.brightdata.com/scrapers",
        "https://brightdata.com/api/datasets",
        "https://app.brightdata.com/api/datasets",
    ]
    
    auth_formats = [
        {'Authorization': f'Bearer {api_token}'},
        {'Authorization': f'Token {api_token}'},
        {'X-API-Key': api_token},
    ]
    
    for endpoint in account_endpoints:
        for auth_header in auth_formats:
            try:
                print(f"\n🧪 Testing account endpoint: {endpoint}")
                response = requests.get(endpoint, headers=auth_header, timeout=5)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"✅ SUCCESS! Account info:")
                    print(f"Response: {response.text[:300]}...")
                elif response.status_code == 401:
                    print(f"🔑 Auth error: {response.text[:100]}...")
                elif response.status_code != 404:
                    print(f"⚠️  Status {response.status_code}: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"💥 Exception: {e}")

if __name__ == '__main__':
    print("🚨 FINDING CORRECT BRIGHTDATA API...")
    
    working_url, working_auth = find_correct_brightdata_api()
    
    if working_url:
        print(f"\n🎉 FOUND WORKING API!")
        print(f"URL: {working_url}")
        print(f"Auth: {working_auth}")
    else:
        print(f"\n❌ NO WORKING API FOUND")
        check_brightdata_account_info()
        
    print(f"\n💡 NEXT STEPS:")
    print(f"1. Check if scraper ID 'hl_f7614f18' is correct in your BrightData dashboard")
    print(f"2. Verify the API token is valid and has proper permissions")
    print(f"3. Check BrightData documentation for the correct API format")
    print(f"4. Make sure you're using the right product (Web Scraper vs Datasets vs etc.)")