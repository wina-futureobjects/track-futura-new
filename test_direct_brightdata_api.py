#!/usr/bin/env python3

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_brightdata_api():
    print('🔍 TESTING ACTUAL BRIGHTDATA API CALLS')
    print('=' * 50)

    # Get BrightData token
    brightdata_token = os.getenv('BRIGHTDATA_API_TOKEN')
    print(f'Token present: {"Yes" if brightdata_token else "No"}')

    if brightdata_token:
        headers = {
            'Authorization': f'Bearer {brightdata_token}',
            'Content-Type': 'application/json'
        }
        
        print('\n1. Testing dataset access...')
        try:
            # Check dataset
            response = requests.get('https://api.brightdata.com/dca/datasets/hl_f7614f18', 
                                   headers=headers, timeout=10)
            print(f'Dataset status: {response.status_code}')
            
            if response.status_code == 200:
                dataset = response.json()
                print(f'Dataset name: {dataset.get("name", "Unknown")}')
                print(f'Dataset active: {dataset.get("is_active", False)}')
            else:
                print(f'Dataset error: {response.text}')
                
        except Exception as e:
            print(f'Dataset check failed: {str(e)}')
        
        print('\n2. Testing collection trigger...')
        try:
            # Trigger a collection
            trigger_url = 'https://api.brightdata.com/dca/trigger_immediate?collector=hl_f7614f18'
            
            test_data = {
                'url': 'https://instagram.com/futureobjects',
                'country': 'US'
            }
            
            response = requests.post(trigger_url, json=test_data, headers=headers, timeout=30)
            print(f'Trigger status: {response.status_code}')
            print(f'Trigger response: {response.text}')
            
            if response.status_code == 200:
                print('✅ SUCCESS! BrightData collection triggered!')
                print('📊 Check your BrightData dashboard for the running collection')
                
                # Parse response to get snapshot ID
                try:
                    result = response.json()
                    snapshot_id = result.get('snapshot_id')
                    if snapshot_id:
                        print(f'📝 Snapshot ID: {snapshot_id}')
                        print('🔄 This should appear in your BrightData dashboard within 1-2 minutes')
                except:
                    pass
                    
            else:
                print('❌ BrightData trigger failed!')
                
        except Exception as e:
            print(f'Trigger failed: {str(e)}')

    else:
        print('❌ No BrightData token found!')
        print('Set BRIGHTDATA_API_TOKEN in your .env file')

if __name__ == '__main__':
    test_brightdata_api()