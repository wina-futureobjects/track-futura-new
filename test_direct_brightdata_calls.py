#!/usr/bin/env python3

import requests
import json

def test_direct_brightdata_calls():
    print('🔬 TESTING DIRECT BRIGHTDATA API CALLS')
    print('=' * 45)

    # Test the EXACT requests as per your examples
    api_token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
    
    print('\n🔵 TEST 1: INSTAGRAM (YOUR EXACT FORMAT)')
    
    url = "https://api.brightdata.com/datasets/v3/trigger"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    params = {
        "dataset_id": "gd_lk5ns7kz21pck8jpis",
        "include_errors": "true",
        "type": "discover_new",
        "discover_by": "url",
    }
    data = [
        {"url":"https://www.instagram.com/nike/","num_of_posts":10,"start_date":"01-01-2025","end_date":"03-01-2025","post_type":"Post"}
    ]

    try:
        response = requests.post(url, headers=headers, params=params, json=data)
        print(f'   Status: {response.status_code}')
        print(f'   Response: {response.text}')
        
        if response.status_code == 200:
            print('   ✅ Instagram DIRECT API works!')
        else:
            print('   ❌ Instagram DIRECT API failed!')
            
    except Exception as e:
        print(f'   ❌ Instagram error: {str(e)}')

    print('\n🔴 TEST 2: FACEBOOK (YOUR EXACT FORMAT)')
    
    params = {
        "dataset_id": "gd_lkaxegm826bjpoo9m5",
        "include_errors": "true",
    }
    data = [
        {"url":"https://www.facebook.com/nike/","num_of_posts":50,"start_date":"01-01-2025","end_date":"02-28-2025"}
    ]

    try:
        response = requests.post(url, headers=headers, params=params, json=data)
        print(f'   Status: {response.status_code}')
        print(f'   Response: {response.text}')
        
        if response.status_code == 200:
            print('   ✅ Facebook DIRECT API works!')
            facebook_working = True
        else:
            print('   ❌ Facebook DIRECT API failed!')
            print(f'   This tells us if the issue is with BrightData or our backend')
            facebook_working = False
            
    except Exception as e:
        print(f'   ❌ Facebook error: {str(e)}')
        facebook_working = False

    print('\n📊 DIAGNOSIS:')
    if facebook_working:
        print('   ✅ Facebook API works directly - backend configuration issue')
    else:
        print('   ❌ Facebook API fails directly - dataset ID or API issue')
        print('   💡 Check if dataset gd_lkaxegm826bjpoo9m5 exists in your BrightData account')

if __name__ == '__main__':
    test_direct_brightdata_calls()