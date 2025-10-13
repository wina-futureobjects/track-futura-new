#!/usr/bin/env python3
"""
Test the folder aggregation fix for the "No sources found in folder 1" error
"""

import requests
import json

def test_folder_1_fix():
    print('🔧 TESTING FOLDER AGGREGATION FIX FOR FOLDER 1')
    print('=' * 50)

    base_url = 'https://trackfutura.futureobjects.io'

    # Test the webhook endpoint for folder 1 specifically
    print('📍 Testing webhook-results/job/1/')
    try:
        response = requests.get(f'{base_url}/api/brightdata/webhook-results/job/1/', timeout=30)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ SUCCESS!')
            print(f'   Total results: {data.get("total_results", 0)}')
            print(f'   Success: {data.get("success", False)}')
            print(f'   Source: {data.get("source", "unknown")}')
            print(f'   Folder name: {data.get("folder_name", "N/A")}')
            if data.get('data') and len(data['data']) > 0:
                print(f'   First post user: {data["data"][0].get("user_posted", "N/A")}')
                print(f'   First post content: {data["data"][0].get("content", "N/A")[:100]}...')
            print('🎉 FOLDER 1 ERROR SHOULD BE FIXED!')
        elif response.status_code == 202:
            data = response.json()
            print('⏳ WAITING FOR DATA')
            print(f'   Message: {data.get("message", "N/A")}')
            print(f'   Hint: {data.get("hint", "N/A")}')
        else:
            print(f'❌ Error {response.status_code}')
            print(f'   Response: {response.text[:200]}...')
            
    except Exception as e:
        print(f'❌ Connection error: {e}')

    print('\n📍 Testing the new folder aggregation endpoint directly')
    try:
        response = requests.get(f'{base_url}/api/brightdata/webhook-results/folder/1/', timeout=30)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ AGGREGATION SUCCESS!')
            print(f'   Total results: {data.get("total_results", 0)}')
            print(f'   Source: {data.get("source", "unknown")}')
            print(f'   Subfolders processed: {data.get("subfolders_processed", 0)}')
            print('🎯 Folder 1 now returns aggregated data from subfolders!')
        else:
            print(f'❌ Aggregation failed: {response.status_code}')
            print(f'   Response: {response.text[:200]}...')
            
    except Exception as e:
        print(f'❌ Aggregation error: {e}')

    print('\n🎯 FINAL TEST: Check if frontend will now work')
    try:
        # This is the actual endpoint the frontend uses
        response = requests.get(f'{base_url}/api/brightdata/webhook-results/job/1/', timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('total_results', 0) > 0:
                print('✅ FRONTEND FIX CONFIRMED!')
                print('   The "System scraper error: No sources found in folder 1" should be resolved')
                print(f'   Frontend will now display {data.get("total_results", 0)} posts from folder 1')
            else:
                print('⚠️ Endpoint works but no data returned')
        else:
            print('❌ Frontend endpoint still not working')
    except Exception as e:
        print(f'❌ Frontend test error: {e}')

    print('\n' + '=' * 50)
    print('🔧 FOLDER 1 AGGREGATION TEST COMPLETE')

if __name__ == '__main__':
    test_folder_1_fix()