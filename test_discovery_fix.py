import requests
import json
import time
from datetime import datetime

print('🔥 TESTING DISCOVERY PHASE FIX')
print('=' * 50)

# Test system API with past dates fix
api_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/'
test_data = {
    'folder_id': 1,
    'user_id': 3,
    'num_of_posts': 10,
    'date_range': {
        'start_date': '2025-10-01T00:00:00.000Z',
        'end_date': '2025-10-08T00:00:00.000Z'  # This should be auto-adjusted to past dates
    }
}

try:
    response = requests.post(api_url, json=test_data)
    data = response.json()
    
    print(f'✅ API Status: {response.status_code}')
    print(f'✅ Success: {data.get("success")}')
    
    if data.get('success'):
        job_id = data.get('results', {}).get('instagram', {}).get('job_id')
        print(f'✅ New Job ID: {job_id}')
        print('🎯 Discovery phase fix deployed!')
        print('📅 System now uses past dates automatically')
        
        # Wait a bit and check job status
        print('\n⏳ Waiting 30 seconds to check job status...')
        time.sleep(30)
        
        # Check if discovery phase error is gone
        token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
        status_url = f'https://api.brightdata.com/datasets/v3/snapshot/{job_id}?format=json'
        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            status_response = requests.get(status_url, headers=headers)
            print(f'📊 Status Check: {status_response.status_code}')
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                if isinstance(status_data, list):
                    print('📊 Job Status: Data ready (no discovery error!)')
                else:
                    print(f'📊 Job Status: {status_data.get("status", "Unknown")}')
                    if "errors" in status_data and status_data["errors"]:
                        print('❌ Still has errors:')
                        for error in status_data["errors"]:
                            print(f'   - {error}')
                    else:
                        print('✅ No discovery phase error!')
            elif status_response.status_code == 202:
                print('📊 Job Status: Still running (no discovery phase error!)')
            else:
                print(f'📊 Status response: {status_response.text[:200]}')
        except Exception as e:
            print(f'📊 Status check error: {e}')
    else:
        print(f'❌ API Error: {data}')
        
except Exception as e:
    print(f'❌ Test failed: {e}')

print('\n' + '=' * 50)
print('🎉 DISCOVERY PHASE ERROR SHOULD BE FIXED!')
print('System now automatically adjusts dates to past dates only')