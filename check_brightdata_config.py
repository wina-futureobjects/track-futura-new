#!/usr/bin/env python3

import requests
import json

def check_brightdata_config():
    print('🔍 CHECKING BRIGHTDATA CONFIGURATION AND SERVICE')
    print('=' * 60)
    
    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata'
    
    # 1. Check configuration
    print('\n1. CHECKING BRIGHTDATA CONFIGURATION...')
    try:
        response = requests.get(f'{base_url}/configs/')
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            configs_data = response.json()
            print(f'   Response type: {type(configs_data)}')
            print(f'   Response: {str(configs_data)[:200]}...')
            
            # Handle different response formats
            if isinstance(configs_data, list):
                configs = configs_data
            elif isinstance(configs_data, dict) and 'results' in configs_data:
                configs = configs_data['results']
            else:
                configs = []
            
            print(f'   Found {len(configs)} configurations')
            
            for i, config in enumerate(configs):
                if isinstance(config, dict):
                    print(f'   Config {i+1}:')
                    print(f'     Zone: {config.get("zone", "NOT SET")}')
                    print(f'     Dataset ID: {config.get("dataset_id", "NOT SET")}')
                    print(f'     Token present: {"Yes" if config.get("api_token") else "No"}')
                    print(f'     Is active: {config.get("is_active", False)}')
                else:
                    print(f'   Config {i+1}: {str(config)}')
                    
        else:
            print(f'   Error: {response.text}')
    except Exception as e:
        print(f'   Error: {str(e)}')
    
    # 2. Test trigger and see what happens
    print('\n2. TESTING TRIGGER WITH DEBUG...')
    try:
        response = requests.post(f'{base_url}/trigger-scraper/', 
                               json={'platform': 'instagram', 'data_type': 'posts'},
                               headers={'Content-Type': 'application/json'})
        
        print(f'   Trigger status: {response.status_code}')
        print(f'   Trigger response: {response.text}')
        
        if response.status_code == 200:
            data = response.json()
            batch_job_id = data.get('batch_job_id')
            
            # Check the batch job details
            job_response = requests.get(f'{base_url}/batch-jobs/{batch_job_id}/')
            if job_response.status_code == 200:
                job_data = job_response.json()
                print(f'   Batch job status: {job_data.get("status")}')
                print(f'   Batch job created: {job_data.get("created_at")}')
                
    except Exception as e:
        print(f'   Error: {str(e)}')
    
    # 3. Provide specific fix instructions
    print('\n3. BRIGHTDATA ISSUE DIAGNOSIS:')
    print('   Based on the tests, here are the most likely issues:')
    print('')
    print('   ISSUE 1: Missing API Token')
    print('   - Your system creates batch jobs successfully')
    print('   - But the BrightData service cannot call the API without a token')
    print('   - Solution: Add your BrightData API token to the configuration')
    print('')
    print('   ISSUE 2: Incorrect Dataset Configuration')
    print('   - The dataset ID might be wrong or inactive')
    print('   - Solution: Verify dataset ID hl_f7614f18 is correct and active')
    print('')
    print('   ISSUE 3: Webhook Not Configured')
    print('   - BrightData might be running but not sending results back')
    print('   - Solution: Configure webhook URL in BrightData dataset settings')
    print('')
    print('   QUICK FIX STEPS:')
    print('   1. Get your BrightData API token from dashboard')
    print('   2. Create/update BrightData config with the token')
    print('   3. Verify dataset hl_f7614f18 exists and is active')
    print('   4. Set webhook URL to your system endpoint')

if __name__ == '__main__':
    check_brightdata_config()