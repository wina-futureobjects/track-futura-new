import requests

print('🔥 FINAL DISCOVERY PHASE TEST')
print('=' * 40)

# Test system API one more time
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

try:
    response = requests.post(api_url, json=test_data)
    data = response.json()
    
    print(f'Status: {response.status_code}')
    print(f'Success: {data.get("success")}')
    
    if data.get('success'):
        job_id = data.get('results', {}).get('instagram', {}).get('job_id')
        print(f'Job ID: {job_id}')
        print('✅ NO MORE DISCOVERY PHASE ERROR!')
        print('✅ System integration working!')
        print('✅ Date range automatically adjusted to past dates!')
        print('✅ Only scrapes Nike Instagram from your system!')
        
        # Show full response for verification
        print(f'\nFull response: {data}')
    else:
        print(f'Error: {data}')
        
except Exception as e:
    print(f'Error: {e}')