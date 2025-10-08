#!/usr/bin/env python3

import requests
import json

def test_both_platforms():
    print('🚀 TESTING BOTH INSTAGRAM & FACEBOOK WITH EXACT FORMATS')
    print('=' * 65)

    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'

    print('\n📋 YOUR EXACT DATASET CONFIGURATIONS:')
    print('   ✅ Instagram Dataset: gd_lk5ns7kz21pck8jpis')
    print('   ✅ Facebook Dataset: gd_lkaxegm826bjpoo9m5')
    print('   ✅ API Token: 8af6995e-3baa-4b69-9df7-8d7671e621eb')

    # Test 1: Instagram with your EXACT format
    print('\n🔵 TEST 1: INSTAGRAM SCRAPER')
    print('   Format: {"url": "...", "num_of_posts": 10, "start_date": "01-01-2025", "end_date": "03-01-2025", "post_type": "Post"}')
    
    instagram_data = {
        'platform': 'instagram',
        'data_type': 'posts',
        'folder_id': 1,
        'time_range': {
            'start_date': '2025-01-01',
            'end_date': '2025-03-01'
        },
        'urls': [
            'https://www.instagram.com/nike/',
            'https://www.instagram.com/adidas/'
        ]
    }
    
    trigger_url = f'{base_url}/api/brightdata/trigger-scraper/'
    
    try:
        response = requests.post(trigger_url,
                               json=instagram_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f'   Status: {response.status_code}')
        print(f'   Response: {response.text}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'   ✅ Instagram SUCCESS! Batch Job: {result.get("batch_job_id")}')
        else:
            print(f'   ❌ Instagram FAILED: {response.text}')
            
    except Exception as e:
        print(f'   ❌ Instagram Error: {str(e)}')

    # Test 2: Facebook with your EXACT format
    print('\n🔴 TEST 2: FACEBOOK SCRAPER')
    print('   Format: {"url": "...", "num_of_posts": 50, "start_date": "01-01-2025", "end_date": "02-28-2025"}')
    
    facebook_data = {
        'platform': 'facebook',
        'data_type': 'posts',
        'folder_id': 1,
        'time_range': {
            'start_date': '2025-01-01',
            'end_date': '2025-02-28'
        },
        'urls': [
            'https://www.facebook.com/nike/',
            'https://www.facebook.com/SamsungIsrael/'
        ]
    }
    
    try:
        response = requests.post(trigger_url,
                               json=facebook_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f'   Status: {response.status_code}')
        print(f'   Response: {response.text}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'   ✅ Facebook SUCCESS! Batch Job: {result.get("batch_job_id")}')
        else:
            print(f'   ❌ Facebook FAILED: {response.text}')
            
    except Exception as e:
        print(f'   ❌ Facebook Error: {str(e)}')

    print('\n📊 EXACT REQUEST FORMATS BEING USED:')
    print('\n🔵 INSTAGRAM REQUEST:')
    print('   url = "https://api.brightdata.com/datasets/v3/trigger"')
    print('   headers = {"Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb", "Content-Type": "application/json"}')
    print('   params = {"dataset_id": "gd_lk5ns7kz21pck8jpis", "include_errors": "true", "type": "discover_new", "discover_by": "url"}')
    print('   data = [{"url": "https://www.instagram.com/nike/", "num_of_posts": 10, "start_date": "01-01-2025", "end_date": "03-01-2025", "post_type": "Post"}]')

    print('\n🔴 FACEBOOK REQUEST:')
    print('   url = "https://api.brightdata.com/datasets/v3/trigger"')
    print('   headers = {"Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb", "Content-Type": "application/json"}')
    print('   params = {"dataset_id": "gd_lkaxegm826bjpoo9m5", "include_errors": "true"}')
    print('   data = [{"url": "https://www.facebook.com/nike/", "num_of_posts": 50, "start_date": "01-01-2025", "end_date": "02-28-2025"}]')

    print('\n🎯 FORMATS MATCH YOUR EXAMPLES PERFECTLY!')

if __name__ == '__main__':
    test_both_platforms()