#!/usr/bin/env python
"""
Test different BrightData authentication and API formats
"""
import requests

def test_brightdata_auth_formats():
    api_token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
    scraper_id = 'hl_f7614f18'
    
    payload = {
        "url": "https://www.instagram.com/nike/"
    }
    
    # Try different auth formats
    auth_formats = [
        {'Authorization': f'Bearer {api_token}'},
        {'Authorization': f'Token {api_token}'},
        {'X-API-Key': api_token},
        {'api_token': api_token},
    ]
    
    # Try different base URLs and paths
    base_configs = [
        ('https://api.brightdata.com', f'/scrapers/{scraper_id}/run'),
        ('https://api.brightdata.com', f'/datasets/{scraper_id}/run'),
        ('https://api.brightdata.com', f'/collections/{scraper_id}/run'),
        ('https://brightdata.com/api', f'/scrapers/{scraper_id}/run'),
        ('https://brightdata.com/api', f'/datasets/{scraper_id}/run'),
        ('https://api.brightdata.com/v2', f'/scrapers/{scraper_id}/trigger'),
        ('https://api.brightdata.com/v1', f'/scrapers/{scraper_id}/trigger'),
    ]
    
    for base_url, path in base_configs:
        for auth_headers in auth_formats:
            url = base_url + path
            headers = {**auth_headers, 'Content-Type': 'application/json'}
            
            print(f"\n🧪 Testing: {url}")
            print(f"Auth: {auth_headers}")
            
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                print(f"Status: {response.status_code}")
                
                if response.status_code not in [404, 401]:
                    print(f"Response: {response.text[:300]}")
                    if response.status_code in [200, 201, 202]:
                        print(f"✅ SUCCESS! Working config found:")
                        print(f"   URL: {url}")
                        print(f"   Auth: {auth_headers}")
                        return url, auth_headers
                else:
                    print(f"Status {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print("\n❌ No working configuration found")
    return None, None

if __name__ == '__main__':
    print("🚀 Testing BrightData authentication and API formats...")
    working_url, working_auth = test_brightdata_auth_formats()
    
    if working_url:
        print(f"\n✅ Use this configuration:")
        print(f"   URL: {working_url}")
        print(f"   Auth: {working_auth}")
    else:
        print("\n❌ Need to check BrightData account settings and documentation")