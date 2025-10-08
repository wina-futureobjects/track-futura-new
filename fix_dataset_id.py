#!/usr/bin/env python3

import requests

def fix_dataset_id():
    print('🔧 FIX BRIGHTDATA DATASET ID')
    print('=' * 40)
    
    print('🚨 PROBLEM: Dataset hl_f7614f18 does not exist!')
    print()
    print('📋 TO FIND YOUR CORRECT DATASET ID:')
    print('1. Go to your BrightData dashboard')
    print('2. Navigate to "Data Collection" or "Datasets"')
    print('3. Find your Instagram scraping dataset') 
    print('4. Look for the dataset ID (usually in URL or settings)')
    print()
    
    print('💡 The dataset ID format is usually like:')
    print('   - hl_abc123def (Hybrid collector)')
    print('   - sc_xyz789abc (Scraping browser)')
    print('   - ws_123456789 (Web scraper)')
    print()
    
    current_id = 'hl_f7614f18'
    print(f'❌ Current (WRONG) ID: {current_id}')
    print()
    
    new_id = input('🔑 Enter your CORRECT dataset ID: ').strip()
    
    if not new_id:
        print('❌ No dataset ID provided!')
        return
        
    print(f'✅ New dataset ID: {new_id}')
    
    # Test the new dataset ID first
    print('\n🧪 Testing new dataset ID...')
    
    token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    test_url = f'https://api.brightdata.com/dca/trigger_immediate?collector={new_id}'
    test_data = {'url': 'https://instagram.com/test', 'country': 'US'}
    
    try:
        response = requests.post(test_url, json=test_data, headers=headers, timeout=15)
        print(f'Test status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ SUCCESS! Dataset ID is valid!')
            
            # Update the configuration
            config_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/configs/1/'
            
            update_data = {
                'dataset_id': new_id,
                'api_token': token,
                'zone': 'web_unlocker1',
                'is_active': True
            }
            
            print('\n🔄 Updating configuration...')
            config_response = requests.patch(config_url, json=update_data, headers={'Content-Type': 'application/json'})
            
            if config_response.status_code == 200:
                print('✅ Configuration updated successfully!')
                print('\n🎉 YOUR BRIGHTDATA SCRAPER SHOULD NOW WORK!')
                print('📊 Test it and check your BrightData dashboard!')
            else:
                print(f'❌ Config update failed: {config_response.text}')
                
        elif response.status_code == 404:
            print('❌ Dataset ID still not found!')
            print('Double-check the ID from your BrightData dashboard')
        else:
            print(f'❌ Test failed: {response.text}')
            
    except Exception as e:
        print(f'❌ Test error: {str(e)}')

if __name__ == '__main__':
    fix_dataset_id()