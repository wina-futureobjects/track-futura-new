#!/usr/bin/env python3

import requests

def update_dataset_id():
    print('🔧 UPDATE BRIGHTDATA DATASET ID')
    print('=' * 40)
    
    print('Current dataset ID: hl_f7614f18 (NOT WORKING)')
    print()
    print('📋 TO GET YOUR CORRECT DATASET ID:')
    print('1. Go to https://app.brightdata.com/')
    print('2. Navigate to your Instagram scraping dataset')
    print('3. Copy the dataset/collector ID')
    print()
    
    new_dataset_id = input('🔑 Enter your CORRECT dataset ID: ').strip()
    
    if not new_dataset_id:
        print('❌ No dataset ID provided')
        return
        
    print(f'📝 Using dataset ID: {new_dataset_id}')
    
    # Update configuration
    config_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/configs/1/'
    
    update_data = {
        'dataset_id': new_dataset_id,
        'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb',
        'zone': 'web_unlocker1',
        'is_active': True
    }
    
    print('🔄 Updating configuration...')
    
    try:
        response = requests.patch(config_url, 
                                json=update_data,
                                headers={'Content-Type': 'application/json'})
        
        print(f'Update status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ Configuration updated successfully!')
            
            # Test with new dataset ID
            print('\n🧪 Testing with new dataset ID...')
            
            # Test trigger
            trigger_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/'
            test_response = requests.post(trigger_url, 
                                        json={'platform': 'instagram', 'data_type': 'posts'},
                                        headers={'Content-Type': 'application/json'})
            
            print(f'Trigger test: {test_response.status_code}')
            
            if test_response.status_code == 200:
                print('🎉 SUCCESS! Your BrightData scraper should now work!')
                print('📊 Check your BrightData dashboard for activity!')
            else:
                print(f'❌ Test failed: {test_response.text}')
                
        else:
            print(f'❌ Update failed: {response.text}')
            
    except Exception as e:
        print(f'❌ Error: {str(e)}')

if __name__ == '__main__':
    update_dataset_id()