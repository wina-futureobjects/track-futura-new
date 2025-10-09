#!/usr/bin/env python
"""
Test the data-storage authentication fix
"""
import requests
import json

# Test the data storage API endpoints
BASE_URL = "http://localhost:8080/api"
TOKEN = "e242daf2ea05576f08fb8d808aba529b0c7ffbab"
TEMP_TOKEN = "temp-token-for-testing"

headers = {
    'Authorization': f'Token {TOKEN}',
    'Content-Type': 'application/json'
}

temp_headers = {
    'Authorization': f'Token {TEMP_TOKEN}',
    'Content-Type': 'application/json'
}

def test_data_storage_endpoints():
    print("🔍 TESTING DATA STORAGE AUTHENTICATION")
    print("=" * 60)
    
    # Test the main job results endpoint that the data-storage page calls
    endpoints_to_test = [
        '/brightdata/job-results/195/',  # The specific job causing 401
        '/brightdata/job-results/191/',  # Another common job
        '/brightdata/batch-jobs/',       # List of batch jobs
        '/brightdata/scraper-requests/', # List of scraper requests
        '/brightdata/configs/',          # BrightData configurations
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n🎯 Testing: {BASE_URL}{endpoint}")
        
        # Test with real token
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
            print(f"   ✅ Real Token: {response.status_code} - {response.reason}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        if 'results' in data:
                            print(f"      📊 Found {len(data['results'])} items")
                        elif 'scraped_posts' in data:
                            print(f"      📝 Found {len(data['scraped_posts'])} scraped posts")
                        elif 'error' in data:
                            print(f"      ⚠️  API Error: {data['error']}")
                        else:
                            print(f"      📋 Response keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"      📊 Found {len(data)} items")
                except:
                    print(f"      📄 Response length: {len(response.text)} characters")
            elif response.status_code == 404:
                print(f"      ℹ️  Resource not found (expected for some jobs)")
            else:
                print(f"      ❌ Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"      ❌ Request Error: {str(e)}")
        
        # Test with temp token for one endpoint
        if endpoint == '/brightdata/job-results/195/':
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=temp_headers, timeout=10)
                print(f"   🌟 Temp Token: {response.status_code} - {response.reason}")
            except Exception as e:
                print(f"      ❌ Temp Token Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 DATA STORAGE AUTHENTICATION TEST COMPLETE!")
    print("✅ If you see 200 OK responses, authentication is working")  
    print("✅ If you see 404 responses, that's expected for missing jobs")
    print("❌ If you see 401 Unauthorized, authentication needs more fixes")

if __name__ == '__main__':
    test_data_storage_endpoints()