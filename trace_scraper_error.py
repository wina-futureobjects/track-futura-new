#!/usr/bin/env python3
"""
Find the root cause of 'System scraper error: No sources found in folder 1'
Let's simulate what happens when a scraper tries to access folder 1
"""

import requests
import json

def find_scraper_error_source():
    base_url = 'https://trackfutura.futureobjects.io'

    print('🔍 TRACING SCRAPER ERROR SOURCE')
    print('=' * 50)

    # Check what happens when we try to access sources in folder 1
    # This might be what's failing when the scraper runs
    
    print('📍 Testing source-related endpoints for folder 1...')
    
    source_endpoints = [
        '/api/track-accounts/sources/?folder_id=1',
        '/api/track-accounts/brand-sources/?folder_id=1',
        '/api/track-accounts/folders/1/sources/',
        '/api/track-accounts/unified-run-folders/1/',
        '/api/track-accounts/report-folders/1/sources/',
    ]
    
    for endpoint in source_endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=15)
            print(f'📍 {endpoint}')
            print(f'   Status: {response.status_code}')
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        if 'results' in data:
                            results = data['results']
                            print(f'   ✅ Found {len(results)} sources')
                        elif 'sources' in data:
                            sources = data['sources']
                            print(f'   ✅ Found {len(sources)} sources')
                        elif 'data' in data:
                            print(f'   ✅ Data length: {len(data["data"])}')
                        else:
                            print(f'   📊 Response keys: {list(data.keys())}')
                    elif isinstance(data, list):
                        print(f'   ✅ Found {len(data)} items')
                except Exception as parse_err:
                    print(f'   📄 Non-JSON response: {response.text[:100]}...')
            elif response.status_code == 404:
                print(f'   ❌ Not Found - This might be the issue!')
            elif response.status_code == 401:
                print(f'   🔒 Unauthorized')
            else:
                print(f'   ❌ Error {response.status_code}: {response.text[:100]}...')
                
        except Exception as e:
            print(f'   🚨 Connection Error: {str(e)[:50]}')

    print('\n🔍 Testing batch job and scraper request endpoints...')
    
    # Check if there are any batch jobs or scraper requests pointing to folder 1
    batch_endpoints = [
        '/api/brightdata/batch-jobs/?project_id=1',
        '/api/brightdata/scraper-requests/?folder_id=1',
    ]
    
    for endpoint in batch_endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=10)
            print(f'📍 {endpoint} -> {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'results' in data:
                    results = data['results']
                    print(f'   Found {len(results)} items')
                    if len(results) > 0:
                        for item in results[:3]:  # Show first 3
                            folder_id = item.get('folder_id') or item.get('source_folder_ids', [])
                            status = item.get('status', 'unknown')
                            print(f'     - Folder: {folder_id}, Status: {status}')
        except Exception as e:
            print(f'   Error: {str(e)[:30]}')

    print('\n🎯 CONCLUSION:')
    print('The error "No sources found in folder 1" likely means:')
    print('1. Folder 1 exists but has no track account sources')
    print('2. When scraper tries to run, it finds no sources to scrape from')
    print('3. This is expected since folder 1 is for results, not sources')

if __name__ == '__main__':
    find_scraper_error_source()