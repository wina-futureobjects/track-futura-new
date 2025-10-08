import requests
import json

# Make a test call to see what dates our system actually sends
api_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/'
test_data = {
    'folder_id': 1,
    'user_id': 3,
    'num_of_posts': 5,
    'date_range': {
        'start_date': '2025-10-01T00:00:00.000Z',
        'end_date': '2025-10-08T00:00:00.000Z'
    }
}

print('🔍 Testing what dates our system actually sends to BrightData...')
print('Input dates: 2025-10-01 to 2025-10-08 (Oct 8 = TODAY)')
print('Expected: System should adjust to past dates only')
print('')

try:
    # This will trigger our system and show debug output in server logs
    response = requests.post(api_url, json=test_data)
    print(f'Response Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Success: {data.get("success")}')
        
        if data.get('success'):
            job_id = data.get('results', {}).get('instagram', {}).get('job_id')
            print(f'Job ID: {job_id}')
            
            # The debug output should be in server logs, but we can check the job
            print('\n⏳ Checking if job has discovery error...')
            
            import time
            time.sleep(15)
            
            # Check job status
            token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
            status_url = f'https://api.brightdata.com/datasets/v3/snapshot/{job_id}?format=json'
            headers = {'Authorization': f'Bearer {token}'}
            
            status_response = requests.get(status_url, headers=headers)
            if status_response.status_code == 202:
                status_text = status_response.text
                if 'Discovery phase error' in status_text:
                    print('❌ STILL HAS DISCOVERY PHASE ERROR!')
                    print('The date adjustment is not working correctly')
                else:
                    print('✅ No discovery phase error - dates were adjusted correctly')
            elif status_response.status_code == 200:
                print('✅ Job completed - dates were adjusted correctly')
            else:
                print(f'Status check: {status_response.status_code} - {status_response.text[:100]}')
        else:
            print(f'API Error: {data}')
    else:
        print(f'HTTP Error: {response.text}')
        
except Exception as e:
    print(f'Error: {e}')

print('')
print('🎯 If discovery error still occurs, the date adjustment logic needs fixing!')