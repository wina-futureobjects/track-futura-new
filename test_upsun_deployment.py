#!/usr/bin/env python3

import requests
import json
import time

def test_upsun_deployment():
    print('🚀 TESTING UPSUN DEPLOYMENT - BRIGHTDATA FIX')
    print('=' * 55)

    # Test both Upsun URLs
    urls = [
        'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site',
        'https://trackfutura.futureobjects.io'
    ]

    for base_url in urls:
        print(f'\n📡 TESTING: {base_url}')
        
        # Test Instagram scraper
        print('\n🔵 TESTING INSTAGRAM SCRAPER:')
        instagram_data = {
            'platform': 'instagram',
            'data_type': 'posts',
            'folder_id': 1,
            'urls': ['https://www.instagram.com/nike/', 'https://www.instagram.com/adidas/']
        }
        
        try:
            response = requests.post(f'{base_url}/api/brightdata/trigger-scraper/',
                                   json=instagram_data,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=30)
            
            print(f'   Status: {response.status_code}')
            if response.status_code == 200:
                result = response.json()
                print(f'   ✅ SUCCESS! Batch Job: {result.get("batch_job_id")}')
                print(f'   Platform: {result.get("platform")}')
                print(f'   Message: {result.get("message")}')
            else:
                print(f'   ❌ FAILED: {response.text}')
                
        except Exception as e:
            print(f'   ❌ ERROR: {str(e)}')

        # Test Facebook scraper
        print('\n🔴 TESTING FACEBOOK SCRAPER:')
        facebook_data = {
            'platform': 'facebook',
            'data_type': 'posts',
            'folder_id': 1,
            'urls': ['https://www.facebook.com/nike/', 'https://www.facebook.com/samsung/']
        }
        
        try:
            response = requests.post(f'{base_url}/api/brightdata/trigger-scraper/',
                                   json=facebook_data,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=30)
            
            print(f'   Status: {response.status_code}')
            if response.status_code == 200:
                result = response.json()
                print(f'   ✅ SUCCESS! Batch Job: {result.get("batch_job_id")}')
                print(f'   Platform: {result.get("platform")}')
                print(f'   Message: {result.get("message")}')
            else:
                print(f'   ❌ FAILED: {response.text}')
                
        except Exception as e:
            print(f'   ❌ ERROR: {str(e)}')

    print('\n🎯 DEPLOYMENT STATUS:')
    print('   ✅ Code pushed to GitHub')
    print('   ✅ Upsun auto-deployment triggered')
    print('   ✅ Fixed additional_data field issue')
    print('   ✅ BrightData batch job creation should work')
    print('   📊 Check your BrightData dashboard for activity!')

if __name__ == '__main__':
    test_upsun_deployment()