#!/usr/bin/env python3
"""
Test BrightData API with real tokens from environment
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

def test_brightdata_api_with_real_tokens():
    print("=== TESTING BRIGHTDATA API WITH REAL TOKENS ===")
    print()
    
    api_key = os.getenv('BRIGHTDATA_API_KEY')
    webhook_token = os.getenv('BRIGHTDATA_WEBHOOK_TOKEN')
    
    if not api_key:
        print("❌ BRIGHTDATA_API_KEY not found in environment!")
        return False
        
    print(f"✅ API Key found: {api_key[:15]}...")
    print(f"✅ Webhook Token: {webhook_token[:15]}..." if webhook_token else "⚠️  No webhook token")
    print()
    
    # Test various BrightData API endpoints
    base_urls = [
        "https://brightdata.com/api",
        "https://api.brightdata.com",
        "https://brightdata.com/cp/api"
    ]
    
    endpoints = [
        "/datasets",
        "/collections", 
        "/zones",
        "/account",
        "/status"
    ]
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    success_found = False
    
    for base_url in base_urls:
        print(f"🔍 Testing base URL: {base_url}")
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                status = response.status_code
                
                if status == 200:
                    print(f"   ✅ {endpoint}: {status} - SUCCESS!")
                    print(f"      Response: {response.text[:200]}...")
                    success_found = True
                elif status == 401:
                    print(f"   🔐 {endpoint}: {status} - Unauthorized (check API key)")
                elif status == 404:
                    print(f"   ❌ {endpoint}: {status} - Not Found")
                else:
                    print(f"   ⚠️  {endpoint}: {status} - {response.text[:100]}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   💥 {endpoint}: Connection error - {str(e)[:100]}")
        
        print()
    
    if success_found:
        print("🎉 BrightData API is responding! Your credentials are working.")
    else:
        print("❌ No successful API responses found.")
        print("   This might indicate:")
        print("   - Incorrect API key format")
        print("   - Wrong API endpoints")
        print("   - BrightData API structure has changed")
    
    return success_found

def test_scraping_request():
    """Test creating a scraping request similar to what the Django app would do"""
    print("=== TESTING SCRAPING REQUEST ===")
    
    api_key = os.getenv('BRIGHTDATA_API_KEY')
    
    # Try to create a simple scraping job
    test_data = {
        "urls": ["https://www.instagram.com/nike/"],
        "format": "json"
    }
    
    # Test different possible endpoints for creating scraping jobs
    possible_endpoints = [
        "https://brightdata.com/api/datasets/gd_lk5ns7kz21pck8jpis/trigger",
        "https://brightdata.com/api/collections/gd_lk5ns7kz21pck8jpis/trigger",
        "https://api.brightdata.com/datasets/gd_lk5ns7kz21pck8jpis/run",
        "https://brightdata.com/cp/api/datasets/gd_lk5ns7kz21pck8jpis/run"
    ]
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    for endpoint in possible_endpoints:
        print(f"🧪 Testing scraping endpoint: {endpoint}")
        try:
            response = requests.post(endpoint, headers=headers, json=test_data, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            
            if response.status_code in [200, 201, 202]:
                print("   ✅ Scraping request accepted!")
                return True
            elif response.status_code == 401:
                print("   🔐 Unauthorized - API key issue")
            elif response.status_code == 404:
                print("   ❌ Endpoint not found")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   💥 Connection error: {str(e)[:100]}")
        print()
    
    return False

if __name__ == "__main__":
    print("🚀 Starting BrightData API testing with real credentials...")
    print()
    
    # Test basic API connectivity
    api_works = test_brightdata_api_with_real_tokens()
    print()
    
    # Test scraping request creation
    scraping_works = test_scraping_request()
    print()
    
    if api_works or scraping_works:
        print("🎉 SUCCESS! BrightData API is accessible with your credentials!")
        print("   The integration should now work properly.")
    else:
        print("❌ ISSUE: Unable to connect to BrightData API")
        print("   Please check:")
        print("   1. API key is correct and active")
        print("   2. BrightData account has necessary permissions")
        print("   3. Check BrightData documentation for current API endpoints")