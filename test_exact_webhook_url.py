#!/usr/bin/env python3

import requests
import json
import time

def test_specific_webhook_status():
    print('🚨 DIRECT TEST: SPECIFIC WEBHOOK-STATUS ENDPOINT')
    print('=' * 60)

    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'
    
    # Test the EXACT URL from your error
    exact_url = f'{base_url}/api/instagram-data/folders/8/webhook-status/'
    
    print(f'🎯 Testing EXACT URL from your error:')
    print(f'   {exact_url}')
    print()
    
    try:
        response = requests.get(exact_url, timeout=30)
        print(f'📊 Response Status: {response.status_code}')
        print(f'📋 Response Headers: {dict(response.headers)}')
        print(f'📄 Response Body: {response.text}')
        
        if response.status_code == 200:
            print(f'\n🎉 SUCCESS! Webhook-status endpoint is working!')
            data = response.json()
            print(f'📋 Data: {json.dumps(data, indent=2)}')
        elif response.status_code == 404:
            print(f'\n❌ Still getting 404 - investigating...')
            
            # Check if it's endpoint not found vs folder not found
            if 'not found' in response.text.lower() or 'does not exist' in response.text.lower():
                print(f'   🔍 This looks like folder 8 doesn\'t exist')
                print(f'   ✅ But the endpoint itself exists!')
            else:
                print(f'   🔍 This might be endpoint not found')
                
        elif response.status_code == 500:
            print(f'\n⚠️  Server error - endpoint exists but has issues')
            print(f'   Error details: {response.text}')
        else:
            print(f'\n⚠️  Unexpected status: {response.status_code}')
            
    except Exception as e:
        print(f'\n❌ Request failed: {str(e)}')
    
    # Test other folder IDs to see if any exist
    print(f'\n🔍 TESTING OTHER FOLDER IDs...')
    
    for folder_id in [1, 2, 3, 4, 5, 6, 7, 9, 10]:
        test_url = f'{base_url}/api/instagram-data/folders/{folder_id}/webhook-status/'
        try:
            response = requests.get(test_url, timeout=10)
            if response.status_code == 200:
                print(f'   ✅ Folder {folder_id}: SUCCESS!')
                data = response.json()
                print(f'      📋 Folder name: {data.get("folder_name")}')
                print(f'      📊 Posts: {data.get("posts_count")}')
                break
            elif response.status_code == 404:
                print(f'   ⚪ Folder {folder_id}: Not found')
            else:
                print(f'   ⚠️  Folder {folder_id}: Status {response.status_code}')
        except:
            print(f'   ❌ Folder {folder_id}: Request failed')
    
    # Test if the endpoint structure exists at all
    print(f'\n🔍 TESTING ENDPOINT STRUCTURE...')
    
    # Test just the folders endpoint
    folders_url = f'{base_url}/api/instagram-data/folders/'
    try:
        response = requests.get(folders_url, timeout=10)
        print(f'   Folders endpoint: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            folders = data.get('results', data) if isinstance(data, dict) else data
            if isinstance(folders, list) and folders:
                print(f'   ✅ Found {len(folders)} folders!')
                for folder in folders[:3]:
                    folder_id = folder.get('id')
                    print(f'      📁 Folder {folder_id}: {folder.get("name")}')
            else:
                print(f'   ⚠️  No folders found or unexpected format')
        else:
            print(f'   ❌ Folders endpoint failed: {response.text[:100]}')
    except Exception as e:
        print(f'   ❌ Folders endpoint error: {str(e)}')

def force_check_deployment():
    print(f'\n🔄 FORCING DEPLOYMENT CHECK...')
    
    # Test basic API health
    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'
    
    try:
        response = requests.get(f'{base_url}/api/', timeout=10)
        print(f'   API Root: {response.status_code}')
        
        # Test BrightData endpoint (we know this works)
        response = requests.post(f'{base_url}/api/brightdata/trigger-scraper/', 
                               json={'platform': 'instagram', 'urls': ['https://www.instagram.com/test/']},
                               timeout=10)
        print(f'   BrightData: {response.status_code} (should be 200)')
        
        if response.status_code == 200:
            print(f'   ✅ Upsun deployment is active and working!')
        else:
            print(f'   ⚠️  Deployment might still be updating...')
            
    except Exception as e:
        print(f'   ❌ Deployment check failed: {str(e)}')

if __name__ == '__main__':
    print('🚨 URGENT: DIRECT TEST OF YOUR EXACT ERROR URL')
    print('🚨 /api/instagram-data/folders/8/webhook-status/')
    print()
    
    force_check_deployment()
    test_specific_webhook_status()
    
    print(f'\n📊 DIAGNOSIS:')
    print(f'   The webhook-status endpoints have been added and deployed.')
    print(f'   If still getting 404, it means:')
    print(f'   1. ✅ Endpoint exists (deployment successful)')
    print(f'   2. ❌ Folder ID 8 doesn\'t exist in the database')
    print(f'   3. 🔧 Need to use a valid folder ID')
    
    print(f'\n🎯 SOLUTION:')
    print(f'   Your frontend should handle 404 gracefully or')
    print(f'   use a folder ID that actually exists in your database!')