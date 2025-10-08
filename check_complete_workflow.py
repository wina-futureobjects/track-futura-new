#!/usr/bin/env python3

import requests
import json

def check_workflow():
    print('🔍 CHECKING COMPLETE WORKFLOW: InputCollection → BrightData → Folder')
    print('=' * 70)

    # Check InputCollections
    print('\n1. CHECKING INPUT COLLECTIONS...')
    input_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/workflow/input-collections/'

    try:
        response = requests.get(input_url)
        print(f'   InputCollections status: {response.status_code}')
        
        if response.status_code == 200:
            collections = response.json()
            if isinstance(collections, dict) and 'results' in collections:
                collections = collections['results']
            
            print(f'   Found {len(collections)} InputCollections:')
            
            for collection in collections:
                if isinstance(collection, dict):
                    coll_id = collection.get('id', 'N/A')
                    name = collection.get('name', 'N/A')
                    urls = collection.get('urls', [])
                    platform_info = collection.get('platform_service', {})
                    platform_name = 'N/A'
                    if isinstance(platform_info, dict):
                        platform_data = platform_info.get('platform', {})
                        if isinstance(platform_data, dict):
                            platform_name = platform_data.get('name', 'N/A')
                    
                    print(f'     Collection {coll_id}: {name}')
                    print(f'       URLs: {urls}')
                    print(f'       Platform: {platform_name}')
                    print()
                    
            if collections:
                print('   ✅ InputCollections exist with URLs to scrape!')
            else:
                print('   ❌ No InputCollections found!')
                
        else:
            print(f'   ❌ Error: {response.text}')
            
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')

    # Check folders
    print('\n2. CHECKING FOLDERS FOR DATA STORAGE...')
    folders_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/facebook-data/folders/'

    try:
        response = requests.get(folders_url)
        print(f'   Folders status: {response.status_code}')
        
        if response.status_code == 200:
            folders_data = response.json()
            if isinstance(folders_data, dict) and 'results' in folders_data:
                folders = folders_data['results']
            else:
                folders = folders_data
                
            print(f'   Found {len(folders)} folders')
            
            for folder in folders[:3]:
                if isinstance(folder, dict):
                    folder_id = folder.get('id', 'N/A')
                    folder_name = folder.get('name', 'N/A')
                    print(f'     Folder {folder_id}: {folder_name}')
                    
        else:
            print(f'   ❌ Error: {response.text}')
            
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')

    # Test workflow trigger
    print('\n3. TESTING WORKFLOW TRIGGER...')
    trigger_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/'
    
    test_data = {
        'platform': 'instagram',
        'data_type': 'posts',
        'input_collection_id': 1,  # Use first InputCollection
        'folder_id': 1,  # Use first folder
        'time_range': {
            'start_date': '2025-10-01',
            'end_date': '2025-10-08'
        }
    }
    
    try:
        response = requests.post(trigger_url, 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f'   Trigger status: {response.status_code}')
        print(f'   Response: {response.text}')
        
        if response.status_code == 200:
            print('   ✅ Workflow trigger works!')
        else:
            print('   ❌ Workflow trigger failed!')
            
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')

    print('\n🎯 WORKFLOW ANALYSIS:')
    print('   The system should:')
    print('   1. Take InputCollection URLs')
    print('   2. Send them to BrightData for scraping')
    print('   3. Store results in selected folder')
    print('   4. Apply time range filtering')
    print()
    print('🚨 NEXT STEP: Fix the BrightData service to connect all components!')

if __name__ == '__main__':
    check_workflow()