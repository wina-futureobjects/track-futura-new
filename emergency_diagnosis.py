#!/usr/bin/env python3

import requests
import json
import time

def diagnose_exact_problem():
    print('🚨 EMERGENCY DIAGNOSIS: FINDING EXACT ISSUE')
    print('=' * 50)

    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'
    
    # Test 1: Check if the endpoint exists
    print('1. 🔍 CHECKING IF BRIGHTDATA ENDPOINT EXISTS...')
    
    try:
        response = requests.get(f'{base_url}/api/brightdata/trigger-scraper/')
        print(f'   GET Status: {response.status_code}')
        print(f'   GET Response: {response.text[:200]}')
    except Exception as e:
        print(f'   GET Error: {str(e)}')
    
    # Test 2: Test POST with minimal data
    print('\n2. 🎯 TESTING POST WITH MINIMAL DATA...')
    
    minimal_data = {
        'platform': 'instagram',
        'urls': ['https://www.instagram.com/nike/']
    }
    
    try:
        response = requests.post(
            f'{base_url}/api/brightdata/trigger-scraper/',
            json=minimal_data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f'   POST Status: {response.status_code}')
        print(f'   POST Response: {response.text}')
        
        if response.status_code != 200:
            print(f'\n❌ FOUND THE PROBLEM!')
            print(f'   Status: {response.status_code}')
            print(f'   Error: {response.text}')
            return False
        else:
            print(f'\n✅ ENDPOINT IS WORKING!')
            return True
            
    except Exception as e:
        print(f'   POST Error: {str(e)}')
        return False

def check_all_brightdata_endpoints():
    print('\n3. 📋 CHECKING ALL BRIGHTDATA ENDPOINTS...')
    
    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'
    
    endpoints = [
        '/api/brightdata/configs/',
        '/api/brightdata/batch-jobs/',
        '/api/brightdata/scraper-requests/',
        '/api/brightdata/webhook/',
        '/api/brightdata/trigger-scraper/'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=10)
            print(f'   {endpoint}: {response.status_code}')
        except Exception as e:
            print(f'   {endpoint}: ERROR - {str(e)}')

def test_alternative_methods():
    print('\n4. 🔄 TESTING ALTERNATIVE METHODS...')
    
    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'
    
    # Method 1: Try batch-jobs endpoint
    print('   Testing batch-jobs endpoint...')
    batch_data = {
        "name": "Emergency Test",
        "project": 1,
        "source_folder_ids": [],
        "platforms_to_scrape": ["instagram"],
        "content_types_to_scrape": {"instagram": ["posts"]},
        "num_of_posts": 5
    }
    
    try:
        response = requests.post(f'{base_url}/api/brightdata/batch-jobs/', json=batch_data)
        print(f'   Batch jobs: {response.status_code} - {response.text[:100]}')
    except Exception as e:
        print(f'   Batch jobs error: {str(e)}')
    
    # Method 2: Try scraper-requests endpoint
    print('   Testing scraper-requests endpoint...')
    scraper_data = {
        "platform": "instagram",
        "urls": ["https://www.instagram.com/nike/"]
    }
    
    try:
        response = requests.post(f'{base_url}/api/brightdata/scraper-requests/', json=scraper_data)
        print(f'   Scraper requests: {response.status_code} - {response.text[:100]}')
    except Exception as e:
        print(f'   Scraper requests error: {str(e)}')

if __name__ == '__main__':
    print('🚨🚨🚨 EMERGENCY: FINDING WHY IT\'S NOT WORKING 🚨🚨🚨')
    print()
    
    # Run all diagnostics
    working = diagnose_exact_problem()
    check_all_brightdata_endpoints()
    test_alternative_methods()
    
    if not working:
        print(f'\n🚨 DIAGNOSIS COMPLETE - PROBLEM IDENTIFIED!')
        print(f'❌ The trigger-scraper endpoint is not working properly')
        print(f'🔧 I need to fix the endpoint immediately')
    else:
        print(f'\n✅ ENDPOINT IS WORKING - PROBLEM IS ELSEWHERE')
        print(f'🔍 The issue might be in your frontend connection')