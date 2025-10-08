#!/usr/bin/env python3

import requests
import json

def test_alternative_endpoints():
    print('🔍 TESTING ALTERNATIVE BRIGHTDATA ENDPOINTS ON UPSUN')
    print('=' * 60)

    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'
    
    # Test different endpoint patterns
    endpoints = [
        'api/brightdata/trigger-scraper/',
        'api/brightdata/scraper-requests/trigger_scraper/',
        'api/brightdata/scraper-requests/',
        'api/brightdata/batch-jobs/create_and_execute/',
        'api/brightdata/',
    ]
    
    test_data = {
        'platform': 'instagram',
        'data_type': 'posts',
        'folder_id': 1,
        'urls': ['https://www.instagram.com/nike/']
    }
    
    for endpoint in endpoints:
        print(f'\n🎯 TESTING: {endpoint}')
        
        try:
            # Test GET first
            response = requests.get(f'{base_url}/{endpoint}', timeout=10)
            print(f'   GET Status: {response.status_code}')
            
            # Test POST with data
            response = requests.post(f'{base_url}/{endpoint}',
                                   json=test_data,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=15)
            
            print(f'   POST Status: {response.status_code}')
            
            if response.status_code == 200:
                result = response.json()
                print(f'   ✅ SUCCESS! Response: {result}')
                return True
            elif response.status_code == 201:
                result = response.json()
                print(f'   ✅ CREATED! Response: {result}')
                return True
            elif response.status_code in [404, 405]:
                print(f'   ❌ Endpoint not available')
            else:
                print(f'   ⚠️  Status {response.status_code}: {response.text[:100]}...')
                
        except Exception as e:
            print(f'   ❌ Error: {str(e)}')

    print('\n🔄 TRYING PRODUCTION DEPLOYMENT URL...')
    production_url = 'https://trackfutura.futureobjects.io'
    
    try:
        response = requests.post(f'{production_url}/api/brightdata/trigger-scraper/',
                               json=test_data,
                               headers={'Content-Type': 'application/json'},
                               timeout=15)
        
        print(f'   Production Status: {response.status_code}')
        if response.status_code == 200:
            result = response.json()
            print(f'   ✅ PRODUCTION WORKING! Response: {result}')
            return True
        else:
            print(f'   ❌ Production not ready: {response.status_code}')
            
    except Exception as e:
        print(f'   ❌ Production error: {str(e)}')

    return False

if __name__ == '__main__':
    success = test_alternative_endpoints()
    
    if success:
        print('\n🎉 FOUND WORKING ENDPOINT!')
    else:
        print('\n⏳ UPSUN DEPLOYMENT STILL IN PROGRESS...')
        print('   🔄 The deployment may take a few more minutes')
        print('   📋 Once ready, the endpoint will be: /api/brightdata/trigger-scraper/')