import requests
import time

print('🔥 TESTING SEPTEMBER DATES FIX')
print('=' * 50)

# Test with problematic October dates - system should force September dates
api_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/'
test_data = {
    'folder_id': 1,
    'user_id': 3,
    'num_of_posts': 10,
    'date_range': {
        'start_date': '2025-10-01T00:00:00.000Z',
        'end_date': '2025-10-08T00:00:00.000Z'  # This should trigger September override
    }
}

try:
    response = requests.post(api_url, json=test_data)
    data = response.json()
    
    print(f'✅ API Status: {response.status_code}')
    print(f'✅ Success: {data.get("success")}')
    
    if data.get('success'):
        job_id = data.get('results', {}).get('instagram', {}).get('job_id')
        print(f'✅ Job ID: {job_id}')
        print('🎯 System should have forced September dates!')
        
        # Wait and check job status
        print('\n⏳ Waiting 30 seconds to check for discovery error...')
        time.sleep(30)
        
        # Check if discovery phase error is gone
        token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
        status_url = f'https://api.brightdata.com/datasets/v3/snapshot/{job_id}?format=json'
        headers = {'Authorization': f'Bearer {token}'}
        
        status_response = requests.get(status_url, headers=headers)
        print(f'📊 Status Check: {status_response.status_code}')
        
        if 'Discovery phase error' in status_response.text:
            print('❌ STILL HAS DISCOVERY PHASE ERROR')
            print('Need different approach...')
        else:
            print('✅ NO DISCOVERY PHASE ERROR!')
            print('🎉 September dates fix worked!')
            
        print(f'Status response: {status_response.text[:300]}')
    else:
        print(f'❌ API Error: {data}')
        
except Exception as e:
    print(f'❌ Test failed: {e}')

print('\n' + '=' * 50)
print('If still failing, we need to check the exact BrightData API requirements')