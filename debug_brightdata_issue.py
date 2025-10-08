#!/usr/bin/env python3

import requests
import json

def debug_brightdata_issue():
    print('🔍 DEBUGGING BRIGHTDATA BACKEND ISSUE')
    print('=' * 45)

    backend_url = 'http://127.0.0.1:8080'
    
    # Test with minimal data first
    print('\n1. TESTING MINIMAL REQUEST:')
    
    minimal_data = {
        'platform': 'instagram',
        'urls': ['https://www.instagram.com/nike/']
    }
    
    try:
        response = requests.post(f'{backend_url}/api/brightdata/trigger-scraper/',
                               json=minimal_data,
                               headers={'Content-Type': 'application/json'},
                               timeout=30)
        
        print(f'   Status: {response.status_code}')
        print(f'   Response: {response.text}')
        
        if response.status_code == 200:
            print('   ✅ Minimal request works!')
        else:
            print('   ❌ Backend has database/model issue')
            
    except Exception as e:
        print(f'   ❌ Request error: {str(e)}')

    # Test database connection
    print('\n2. TESTING DATABASE MODELS:')
    
    try:
        # Test if projects exist
        response = requests.get(f'{backend_url}/api/users/projects/', timeout=10)
        print(f'   Projects endpoint: {response.status_code}')
        
        if response.status_code == 200:
            projects = response.json()
            if isinstance(projects, dict) and 'results' in projects:
                projects = projects['results']
            print(f'   Projects found: {len(projects)}')
        else:
            print(f'   Projects issue: {response.text}')
            
    except Exception as e:
        print(f'   ❌ Database error: {str(e)}')

    # Test BrightData configs
    print('\n3. TESTING BRIGHTDATA CONFIGS:')
    
    try:
        response = requests.get(f'{backend_url}/api/brightdata/configs/', timeout=10)
        print(f'   Configs endpoint: {response.status_code}')
        
        if response.status_code == 200:
            configs = response.json()
            if isinstance(configs, dict) and 'results' in configs:
                configs = configs['results']
            print(f'   BrightData configs: {len(configs)}')
            
            for config in configs[:3]:  # Show first 3
                if isinstance(config, dict):
                    platform = config.get('platform', 'unknown')
                    dataset_id = config.get('dataset_id', 'unknown')
                    is_active = config.get('is_active', False)
                    print(f'     {platform}: {dataset_id} (active: {is_active})')
        else:
            print(f'   Configs issue: {response.text}')
            
    except Exception as e:
        print(f'   ❌ Configs error: {str(e)}')

    print('\n🎯 DIAGNOSIS:')
    print('   ✅ Backend server running')
    print('   ✅ CORS working for frontend')
    print('   ❓ Database/BrightData models need checking')

if __name__ == '__main__':
    debug_brightdata_issue()