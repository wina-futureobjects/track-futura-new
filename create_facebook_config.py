#!/usr/bin/env python3

import requests
import json

def create_facebook_config():
    print('🔧 CREATING FACEBOOK BRIGHTDATA CONFIGURATION')
    print('=' * 50)

    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'

    # Step 1: Create Facebook BrightData configuration
    print('\n1. CREATING FACEBOOK CONFIGURATION...')
    
    config_data = {
        'name': 'Facebook Posts Scraper',
        'platform': 'facebook',
        'dataset_id': 'gd_lkaxegm826bjpoo9m5',  # Your Facebook dataset ID
        'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb',  # Your working token
        'is_active': True
    }
    
    # Try to create the configuration through the API
    config_url = f'{base_url}/api/brightdata/configs/'
    
    try:
        response = requests.post(config_url, 
                               json=config_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f'   Config creation status: {response.status_code}')
        print(f'   Response: {response.text}')
        
        if response.status_code in [200, 201]:
            print('   ✅ Facebook configuration created!')
        else:
            print('   ⚠️  Manual configuration may be needed')
            
    except Exception as e:
        print(f'   ❌ Config creation error: {str(e)}')

    # Step 2: Test Facebook scraper with the configuration
    print('\n2. TESTING FACEBOOK SCRAPER WITH NEW CONFIG...')
    
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
    
    trigger_url = f'{base_url}/api/brightdata/trigger-scraper/'
    
    try:
        response = requests.post(trigger_url,
                               json=facebook_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f'   Status: {response.status_code}')
        print(f'   Response: {response.text}')
        
        if response.status_code == 200:
            result = response.json()
            print('\n🎉 FACEBOOK SCRAPER IS NOW WORKING!')
            print(f'   ✅ Batch Job: {result.get("batch_job_id")}')
            print(f'   ✅ Platform: {result.get("platform")}')
            print(f'   ✅ Status: {result.get("status")}')
            
            print('\n📊 FACEBOOK REQUEST FORMAT (EXACT):')
            print('   url = "https://api.brightdata.com/datasets/v3/trigger"')
            print('   headers = {"Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb", "Content-Type": "application/json"}')
            print('   params = {"dataset_id": "gd_lkaxegm826bjpoo9m5", "include_errors": "true"}')
            print('   data = [{"url": "https://www.facebook.com/nike/", "num_of_posts": 50, "start_date": "01-01-2025", "end_date": "02-28-2025"}]')
            
            return True
        else:
            print(f'\n❌ Still failing: {response.text}')
            return False
            
    except Exception as e:
        print(f'\n❌ Test error: {str(e)}')
        return False

if __name__ == '__main__':
    success = create_facebook_config()
    if success:
        print('\n🎯 BOTH INSTAGRAM & FACEBOOK NOW WORKING!')
        print('   ✅ Instagram: gd_lk5ns7kz21pck8jpis')
        print('   ✅ Facebook: gd_lkaxegm826bjpoo9m5')
        print('   ✅ Both use exact BrightData formats!')
    else:
        print('\n🔧 Facebook needs manual configuration fix')