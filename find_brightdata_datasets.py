#!/usr/bin/env python3

import requests
import json

def find_correct_dataset():
    print('🔍 FINDING YOUR ACTUAL BRIGHTDATA DATASETS')
    print('=' * 50)

    token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    print('Fetching your BrightData datasets...')
    try:
        response = requests.get('https://api.brightdata.com/dca/datasets', 
                               headers=headers, timeout=15)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            datasets = response.json()
            print(f'Found {len(datasets)} datasets in your account:')
            print()
            
            for i, dataset in enumerate(datasets):
                dataset_id = dataset.get('id', 'No ID')
                name = dataset.get('name', 'No Name')
                is_active = dataset.get('is_active', False)
                status = dataset.get('status', 'Unknown')
                
                print(f'{i+1}. Dataset ID: {dataset_id}')
                print(f'   Name: {name}')
                print(f'   Active: {is_active}')
                print(f'   Status: {status}')
                print()
            
            if datasets:
                print('🎯 TO FIX YOUR BRIGHTDATA:')
                print('1. Choose the correct dataset ID from the list above')
                print('2. Update your configuration with the correct ID')
                print('3. Or create a new Instagram dataset if none exist')
                
                # Test the first active dataset
                active_datasets = [d for d in datasets if d.get('is_active')]
                if active_datasets:
                    first_active = active_datasets[0]
                    test_id = first_active.get('id')
                    print(f'\n🧪 Testing first active dataset: {test_id}')
                    
                    # Test trigger
                    trigger_url = f'https://api.brightdata.com/dca/trigger_immediate?collector={test_id}'
                    test_data = {'url': 'https://instagram.com/test', 'country': 'US'}
                    
                    test_response = requests.post(trigger_url, json=test_data, headers=headers, timeout=15)
                    print(f'Test trigger status: {test_response.status_code}')
                    
                    if test_response.status_code == 200:
                        print(f'✅ SUCCESS! Use dataset ID: {test_id}')
                    else:
                        print(f'❌ Test failed: {test_response.text[:100]}')
            else:
                print('❌ No datasets found! You need to create one in BrightData dashboard')
                
        elif response.status_code == 401:
            print('❌ Authentication failed - check your API token')
        else:
            print(f'❌ API error: {response.text[:200]}')
            
    except Exception as e:
        print(f'❌ Error: {str(e)}')

if __name__ == '__main__':
    find_correct_dataset()