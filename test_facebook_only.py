#!/usr/bin/env python3

import requests
import json

def test_facebook_only():
    print('🔴 TESTING FACEBOOK SCRAPER ONLY')
    print('=' * 40)

    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'

    print('\n📋 FACEBOOK CONFIGURATION:')
    print('   Dataset ID: gd_lkaxegm826bjpoo9m5')
    print('   API Token: 8af6995e-3baa-4b69-9df7-8d7671e621eb')
    print('   Format: EXACT match to your example')

    facebook_data = {
        'platform': 'facebook',
        'data_type': 'posts',
        'folder_id': 1,
        'time_range': {
            'start_date': '2025-01-01',
            'end_date': '2025-02-28'
        },
        'urls': ['https://www.facebook.com/nike/']
    }
    
    print('\n🎯 REQUEST DATA:')
    print(json.dumps(facebook_data, indent=2))
    
    trigger_url = f'{base_url}/api/brightdata/trigger-scraper/'
    
    try:
        response = requests.post(trigger_url,
                               json=facebook_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f'\n📊 RESPONSE:')
        print(f'   Status: {response.status_code}')
        print(f'   Headers: {dict(response.headers)}')
        print(f'   Body: {response.text}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'\n✅ SUCCESS!')
            print(f'   Batch Job: {result.get("batch_job_id")}')
            print(f'   Platform: {result.get("platform")}')
            print(f'   Status: {result.get("status")}')
        else:
            print(f'\n❌ FAILED!')
            print(f'   This means there\'s a configuration issue')
            
            # Check if it's a BrightData config issue
            if '500' in str(response.status_code):
                print('\n🔍 POSSIBLE ISSUES:')
                print('   1. Facebook dataset ID not configured correctly')
                print('   2. BrightData Facebook API requires different format')
                print('   3. Configuration not created for Facebook platform')
                
        return response.status_code == 200
        
    except Exception as e:
        print(f'\n❌ Error: {str(e)}')
        return False

if __name__ == '__main__':
    success = test_facebook_only()
    if not success:
        print('\n🔧 SOLUTION: Let me check the backend configuration...')
    else:
        print('\n🎉 Facebook scraper is working!')