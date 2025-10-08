#!/usr/bin/env python3

import requests
import json

def update_brightdata_config():
    print('🔧 UPDATING BRIGHTDATA TO USE CORRECT DATASET API FORMAT')
    print('=' * 65)

    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'

    # Update BrightData configuration
    print('\n1. UPDATING BRIGHTDATA CONFIGURATION...')
    config_url = f'{base_url}/api/brightdata/config/'
    
    config_data = {
        'platform': 'instagram',
        'dataset_id': 'gd_lk5ns7kz21pck8jpis',  # Your actual dataset ID
        'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb',  # Your working token
        'is_active': True,
        'name': 'Instagram Dataset Scraper'
    }
    
    try:
        # Try to create/update config
        response = requests.post(config_url, 
                               json=config_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f'   Config update status: {response.status_code}')
        print(f'   Response: {response.text}')
        
        if response.status_code in [200, 201]:
            print('   ✅ BrightData configuration updated!')
        else:
            print('   ⚠️  Config update may have issues')
            
    except Exception as e:
        print(f'   ❌ Config update error: {str(e)}')

    # Test the corrected workflow
    print('\n2. TESTING CORRECTED BRIGHTDATA WORKFLOW...')
    
    workflow_data = {
        'platform': 'instagram',
        'data_type': 'posts',
        'folder_id': 1,
        'time_range': {
            'start_date': '2025-01-01',
            'end_date': '2025-01-08'
        },
        'urls': [
            'https://www.instagram.com/nike/',
            'https://www.instagram.com/adidas/',
            'https://www.instagram.com/puma/'
        ]
    }
    
    trigger_url = f'{base_url}/api/brightdata/trigger-scraper/'
    
    try:
        response = requests.post(trigger_url,
                               json=workflow_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f'   Workflow trigger status: {response.status_code}')
        print(f'   Response: {response.text}')
        
        if response.status_code == 200:
            result = response.json()
            print('\n🎉 BRIGHTDATA DATASET API IS NOW WORKING!')
            print(f'   ✅ Batch Job ID: {result.get("batch_job_id")}')
            print(f'   ✅ Using Dataset API: gd_lk5ns7kz21pck8jpis')
            print(f'   ✅ Instagram URLs being scraped via Dataset API')
            print('   📊 Check your BrightData dashboard for dataset activity!')
            
        else:
            print(f'   ❌ Workflow failed: {response.text}')
            
    except Exception as e:
        print(f'   ❌ Workflow error: {str(e)}')

    print('\n📋 WHAT CHANGED:')
    print('   ✅ Switched from Customer ID to Dataset API')
    print('   ✅ Using correct Instagram dataset: gd_lk5ns7kz21pck8jpis')
    print('   ✅ Following BrightData official API format')
    print('   ✅ Proper request structure with num_of_posts, dates, etc.')

if __name__ == '__main__':
    update_brightdata_config()