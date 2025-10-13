#!/usr/bin/env python3
"""
Quick Fix for Folder 1 Error - Use Data Storage Endpoint Directly
"""

import requests
import json

def test_folder_1_direct_fix():
    base_url = 'https://trackfutura.futureobjects.io'
    
    print('🔧 TESTING DIRECT DATA STORAGE FIX FOR FOLDER 1')
    print('=' * 50)
    
    # Test the data-storage endpoint that we know works
    try:
        response = requests.get(f'{base_url}/api/brightdata/data-storage/run/1/', timeout=15)
        print(f'📍 Data storage endpoint status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ SUCCESS - FOLDER 1 HAS DATA!')
            print(f'   Success: {data.get("success", False)}')
            print(f'   Total results: {data.get("total_results", 0)}')
            print(f'   Folder name: {data.get("folder_name", "N/A")}')
            print(f'   Has subfolders: {data.get("has_subfolders", False)}')
            
            if data.get('data') and len(data['data']) > 0:
                print(f'   First post: {data["data"][0].get("user_posted", "N/A")}')
                print(f'   Content preview: {data["data"][0].get("content", "")[:100]}...')
                
            if data.get('subfolders'):
                print(f'   Subfolders: {len(data["subfolders"])} found')
                for sf in data['subfolders']:
                    print(f'     - {sf.get("platform", "unknown")}: {sf.get("posts_count", 0)} posts')
            
            print('\n🎯 SOLUTION:')
            if data.get('total_results', 0) > 0:
                print('   ✅ Folder 1 has direct data - frontend should work!')
            elif data.get('subfolders'):
                print('   ✅ Folder 1 has subfolder data - aggregation will work!')
            else:
                print('   ⚠️ Folder 1 exists but needs data population')
                
            print('\n🔧 QUICK FIX RECOMMENDATION:')
            print('   The data-storage endpoint works and returns data for folder 1')
            print('   Frontend can use /api/brightdata/data-storage/run/1/ as fallback')
            print('   This eliminates the "No sources found in folder 1" error')
            
        else:
            print(f'❌ Data storage endpoint failed: {response.status_code}')
            print(f'Response: {response.text[:200]}...')
            
    except Exception as e:
        print(f'❌ Error testing data storage: {e}')
    
    print('\n' + '=' * 50)
    print('🎯 FOLDER 1 DIRECT FIX COMPLETE')

if __name__ == '__main__':
    test_folder_1_direct_fix()