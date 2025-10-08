#!/usr/bin/env python3

import requests
import json

def fix_brightdata_token():
    print('🔧 FIXING BRIGHTDATA API TOKEN')
    print('=' * 50)
    
    print('🔍 Step 1: Get your BrightData API token')
    print('   1. Go to your BrightData dashboard')
    print('   2. Navigate to API tokens section') 
    print('   3. Copy your API token')
    print('')
    
    token = input('🔑 Enter your BrightData API token: ').strip()
    
    if not token:
        print('❌ No token provided. Cannot continue.')
        return
    
    print(f'📝 Token received: {token[:20]}...')
    
    # Update the configuration
    config_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/configs/1/'
    
    update_data = {
        'api_token': token,
        'zone': 'web_unlocker1',  # Add the missing zone
        'is_active': True
    }
    
    print('\n🔄 Updating BrightData configuration...')
    
    try:
        response = requests.patch(config_url, 
                                json=update_data,
                                headers={'Content-Type': 'application/json'})
        
        print(f'Update status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ SUCCESS! BrightData token updated!')
            print('📊 Your scraper should now work properly')
            
            # Test the configuration
            print('\n🧪 Testing updated configuration...')
            
            trigger_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/'
            
            test_response = requests.post(trigger_url, 
                                        json={'platform': 'instagram', 'data_type': 'posts'},
                                        headers={'Content-Type': 'application/json'})
            
            print(f'Test trigger status: {test_response.status_code}')
            
            if test_response.status_code == 200:
                print('🎉 PERFECT! Your BrightData scraper is now working!')
                print('📈 Check your BrightData dashboard for incoming requests')
            else:
                print(f'❌ Test failed: {test_response.text}')
                
        else:
            print(f'❌ Update failed: {response.text}')
            
    except Exception as e:
        print(f'❌ Error updating config: {str(e)}')

if __name__ == '__main__':
    fix_brightdata_token()