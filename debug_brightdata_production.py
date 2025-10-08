#!/usr/bin/env python3
"""
Check BrightData configuration in production
"""
import requests
import json

# Production API URL
BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def check_brightdata_config():
    try:
        # Try to authenticate
        login_url = f"{BASE_URL}/api/users/login/"
        login_data = {
            'username': 'test',
            'password': 'test123'
        }
        
        session = requests.Session()
        response = session.post(login_url, data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access')
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Check BrightData configurations
            brightdata_url = f"{BASE_URL}/api/brightdata/configs/"
            brightdata_response = session.get(brightdata_url, headers=headers)
            
            print(f"🔍 CHECKING PRODUCTION BRIGHTDATA CONFIG")
            print(f"Auth status: {response.status_code}")
            print(f"BrightData API status: {brightdata_response.status_code}")
            
            if brightdata_response.status_code == 200:
                configs = brightdata_response.json()
                print(f"Found {len(configs)} BrightData configurations:")
                for config in configs:
                    print(f"  - Username: {config.get('username')}")
                    print(f"  - Zone: {config.get('zone')}")
                    print(f"  - Host: {config.get('host')}:{config.get('port')}")
                    print(f"  - API Token: {'*' * 20}{config.get('api_token', '')[-10:]}")
                    print(f"  - Enabled: {config.get('is_enabled')}")
                    print()
            else:
                print(f"❌ Failed to get BrightData configs: {brightdata_response.text}")
                
            # Also check if we can trigger a scraper
            scraper_url = f"{BASE_URL}/api/brightdata/trigger-scraper/"
            test_payload = {
                "platform": "instagram", 
                "urls": ["https://instagram.com/nike"],
                "input_collection_id": 1
            }
            
            scraper_response = session.post(scraper_url, headers=headers, json=test_payload)
            print(f"🚀 TESTING SCRAPER TRIGGER")
            print(f"Scraper trigger status: {scraper_response.status_code}")
            print(f"Response: {scraper_response.text[:500]}...")
            
        else:
            print(f"❌ Authentication failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_brightdata_config()