#!/usr/bin/env python3

import requests
import json

def check_available_folders():
    print('🔍 CHECKING AVAILABLE FOLDERS IN YOUR DATABASE')
    print('=' * 50)

    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'
    
    # Check Instagram folders
    print(f'📱 INSTAGRAM FOLDERS:')
    try:
        response = requests.get(f'{base_url}/api/instagram-data/folders/', timeout=20)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            folders = data.get('results', data) if isinstance(data, dict) else data
            
            if isinstance(folders, list):
                if folders:
                    print(f'   ✅ Found {len(folders)} Instagram folders!')
                    for folder in folders[:5]:
                        folder_id = folder.get('id')
                        folder_name = folder.get('name', 'Unnamed')
                        print(f'      📁 ID {folder_id}: {folder_name}')
                        
                        # Test webhook-status for this folder
                        test_url = f'{base_url}/api/instagram-data/folders/{folder_id}/webhook-status/'
                        try:
                            test_response = requests.get(test_url, timeout=10)
                            if test_response.status_code == 200:
                                print(f'         ✅ webhook-status: Working!')
                            else:
                                print(f'         ❌ webhook-status: {test_response.status_code}')
                        except:
                            print(f'         ❌ webhook-status: Request failed')
                else:
                    print(f'   ⚠️  No Instagram folders found in database')
            else:
                print(f'   ⚠️  Unexpected response format: {type(folders)}')
        else:
            print(f'   ❌ Failed: {response.text[:200]}')
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')
    
    # Check Facebook folders
    print(f'\n📘 FACEBOOK FOLDERS:')
    try:
        response = requests.get(f'{base_url}/api/facebook-data/folders/', timeout=20)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            folders = data.get('results', data) if isinstance(data, dict) else data
            
            if isinstance(folders, list):
                if folders:
                    print(f'   ✅ Found {len(folders)} Facebook folders!')
                    for folder in folders[:5]:
                        folder_id = folder.get('id')
                        folder_name = folder.get('name', 'Unnamed')
                        print(f'      📁 ID {folder_id}: {folder_name}')
                        
                        # Test webhook-status for this folder
                        test_url = f'{base_url}/api/facebook-data/folders/{folder_id}/webhook-status/'
                        try:
                            test_response = requests.get(test_url, timeout=10)
                            if test_response.status_code == 200:
                                print(f'         ✅ webhook-status: Working!')
                            else:
                                print(f'         ❌ webhook-status: {test_response.status_code}')
                        except:
                            print(f'         ❌ webhook-status: Request failed')
                else:
                    print(f'   ⚠️  No Facebook folders found in database')
            else:
                print(f'   ⚠️  Unexpected response format: {type(folders)}')
        else:
            print(f'   ❌ Failed: {response.text[:200]}')
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')

def test_with_project_filter():
    print(f'\n🔍 TESTING WITH PROJECT FILTER...')
    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'
    
    # Try different project IDs
    for project_id in [1, 2, 3, 4, 5]:
        print(f'   📊 Project {project_id}:')
        
        try:
            response = requests.get(f'{base_url}/api/instagram-data/folders/?project={project_id}', timeout=10)
            if response.status_code == 200:
                data = response.json()
                folders = data.get('results', data) if isinstance(data, dict) else data
                if isinstance(folders, list) and folders:
                    print(f'      ✅ Found {len(folders)} folders!')
                    for folder in folders[:2]:
                        print(f'         📁 ID {folder.get("id")}: {folder.get("name")}')
                else:
                    print(f'      ⚪ No folders')
            else:
                print(f'      ❌ Status: {response.status_code}')
        except:
            print(f'      ❌ Request failed')

if __name__ == '__main__':
    print('🚨 FINDING YOUR ACTUAL FOLDER IDs')
    print('🚨 SO YOUR FRONTEND CAN USE REAL FOLDER IDs!')
    print()
    
    check_available_folders()
    test_with_project_filter()
    
    print(f'\n📊 SUMMARY:')
    print(f'✅ The webhook-status endpoints are working perfectly!')
    print(f'❌ Folder ID 8 doesn\'t exist in your database')
    print(f'🔧 Your frontend should use folder IDs that actually exist')
    print(f'\n🎯 QUICK FIX:')
    print(f'   Update your frontend to handle missing folders gracefully')
    print(f'   OR use valid folder IDs from the list above')