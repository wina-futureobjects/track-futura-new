#!/usr/bin/env python3
"""
Detailed investigation of Folder 1 error to find the exact root cause
"""

import requests
import json

def investigate_folder_1_error():
    base_url = 'https://trackfutura.futureobjects.io'

    print('🔍 DETAILED FOLDER 1 INVESTIGATION')
    print('=' * 50)

    # Test the exact endpoints that are being called
    endpoints = [
        '/api/brightdata/webhook-results/job/1/',
        '/api/track-accounts/report-folders/1/',
        '/api/brightdata/data-storage/run/1/',
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=15)
            print(f'📍 {endpoint}')
            print(f'   Status: {response.status_code}')
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f'   Success: {data.get("success", "N/A")}')
                    print(f'   Data length: {len(data.get("data", []))}')
                    print(f'   Total results: {data.get("total_results", "N/A")}')
                    print(f'   Message: {data.get("message", "N/A")}')
                except:
                    print(f'   Raw response: {response.text[:100]}...')
            else:
                print(f'   Error response: {response.text[:100]}...')
        except Exception as e:
            print(f'📍 {endpoint} -> Connection error: {str(e)[:50]}')

    print('\n🔍 Testing the folder structure endpoint')
    try:
        response = requests.get(f'{base_url}/api/track-accounts/report-folders/1/', timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f'✅ Folder 1 exists: {data.get("name")}')
            print(f'   Post count: {data.get("post_count", 0)}')
            print(f'   Subfolders: {len(data.get("subfolders", []))}')
            for sf in data.get('subfolders', []):
                print(f'     - {sf.get("platform")}: {sf.get("post_count", 0)} posts (ID: {sf.get("id")})')
    except Exception as e:
        print(f'Error checking folder structure: {e}')

    # Check if the JavaScript error might be coming from a different source
    print('\n🔍 Investigating potential source of the JavaScript error')
    
    # The error mentions "System scraper error" - this might be from scraper status checking
    scraper_endpoints = [
        '/api/brightdata/batch-jobs/',
        '/api/brightdata/scraper-requests/',
        '/api/apify/',
    ]
    
    for endpoint in scraper_endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=10)
            print(f'📍 {endpoint} -> {response.status_code}')
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'results' in data:
                        results = data['results']
                        print(f'   Found {len(results)} items')
                        if len(results) > 0:
                            print(f'   First item keys: {list(results[0].keys())}')
                    elif isinstance(data, list):
                        print(f'   Found {len(data)} items')
                except:
                    pass
        except Exception as e:
            print(f'📍 {endpoint} -> Error: {str(e)[:30]}')

if __name__ == '__main__':
    investigate_folder_1_error()