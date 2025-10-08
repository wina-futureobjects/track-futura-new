#!/usr/bin/env python3

import requests
import json

def fix_local_brightdata_config():
    print('🔧 FIXING LOCAL BRIGHTDATA CONFIGURATION')
    print('=' * 50)

    backend_url = 'http://127.0.0.1:8080'
    
    print('\n1. UPDATING INSTAGRAM CONFIG:')
    
    # Update Instagram config
    instagram_config = {
        'name': 'Instagram Posts Scraper',
        'platform': 'instagram',
        'dataset_id': 'gd_lk5ns7kz21pck8jpis',  # Your correct Instagram dataset
        'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb',  # Your working token
        'is_active': True
    }
    
    try:
        # Get existing configs first
        response = requests.get(f'{backend_url}/api/brightdata/configs/')
        
        if response.status_code == 200:
            configs = response.json()
            if isinstance(configs, dict) and 'results' in configs:
                configs = configs['results']
            
            # Find Instagram config to update
            instagram_config_id = None
            for config in configs:
                if isinstance(config, dict) and config.get('platform') == 'instagram':
                    instagram_config_id = config.get('id')
                    break
            
            if instagram_config_id:
                # Update existing
                response = requests.put(f'{backend_url}/api/brightdata/configs/{instagram_config_id}/',
                                      json=instagram_config,
                                      headers={'Content-Type': 'application/json'})
                print(f'   Update status: {response.status_code}')
            else:
                # Create new
                response = requests.post(f'{backend_url}/api/brightdata/configs/',
                                       json=instagram_config,
                                       headers={'Content-Type': 'application/json'})
                print(f'   Create status: {response.status_code}')
                
        print(f'   Response: {response.text}')
        
    except Exception as e:
        print(f'   ❌ Instagram config error: {str(e)}')

    print('\n2. UPDATING FACEBOOK CONFIG:')
    
    # Update Facebook config
    facebook_config = {
        'name': 'Facebook Posts Scraper',
        'platform': 'facebook',
        'dataset_id': 'gd_lkaxegm826bjpoo9m5',  # Your correct Facebook dataset
        'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb',  # Your working token
        'is_active': True
    }
    
    try:
        # Find Facebook config to update
        facebook_config_id = None
        for config in configs:
            if isinstance(config, dict) and config.get('platform') == 'facebook':
                facebook_config_id = config.get('id')
                break
        
        if facebook_config_id:
            # Update existing
            response = requests.put(f'{backend_url}/api/brightdata/configs/{facebook_config_id}/',
                                  json=facebook_config,
                                  headers={'Content-Type': 'application/json'})
            print(f'   Update status: {response.status_code}')
        else:
            # Create new
            response = requests.post(f'{backend_url}/api/brightdata/configs/',
                                   json=facebook_config,
                                   headers={'Content-Type': 'application/json'})
            print(f'   Create status: {response.status_code}')
            
        print(f'   Response: {response.text}')
        
    except Exception as e:
        print(f'   ❌ Facebook config error: {str(e)}')

    print('\n3. TESTING FIXED CONFIGURATION:')
    
    # Test Instagram scraper
    test_data = {
        'platform': 'instagram',
        'urls': ['https://www.instagram.com/nike/']
    }
    
    try:
        response = requests.post(f'{backend_url}/api/brightdata/trigger-scraper/',
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f'   Instagram test: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'   ✅ Instagram working! Batch Job: {result.get("batch_job_id")}')
        else:
            print(f'   ❌ Instagram still failing: {response.text}')
            
    except Exception as e:
        print(f'   ❌ Test error: {str(e)}')

if __name__ == '__main__':
    fix_local_brightdata_config()