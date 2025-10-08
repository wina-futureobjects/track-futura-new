import requests
import json

print('🔍 PRODUCTION SYSTEM STATUS CHECK')
print('=' * 50)

base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'

# Test folder 140 (original issue)
print('Testing folder 140:')
try:
    response = requests.get(f'{base_url}/api/brightdata/job-results/140/')
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Success: {data.get("success")}')
        print(f'Total results: {data.get("total_results", 0)}')
        if data.get("total_results", 0) > 0:
            print('✅ DATA FOUND!')
        else:
            print('❌ NO DATA - This is the problem!')
    else:
        print(f'Response: {response.text[:200]}')
except Exception as e:
    print(f'Error: {e}')

# Test folder 144
print('\nTesting folder 144:')
try:
    response = requests.get(f'{base_url}/api/brightdata/job-results/144/')
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Success: {data.get("success")}')
        print(f'Total results: {data.get("total_results", 0)}')
        if data.get("total_results", 0) > 0:
            print('✅ DATA FOUND!')
        else:
            print('❌ NO DATA')
    else:
        print(f'Response: {response.text[:200]}')
except Exception as e:
    print(f'Error: {e}')

print('\n🚀 FORCING DATA CREATION FOR FOLDER 140')
print('=' * 50)

# Trigger scraper for folder 140
test_data = {
    'folder_id': 140,
    'user_id': 1,
    'platform': 'instagram',
    'target': 'nike',
    'num_of_posts': 5
}

try:
    response = requests.post(f'{base_url}/api/brightdata/trigger-scraper/', json=test_data)
    print(f'Trigger Status: {response.status_code}')
    data = response.json()
    print(f'Success: {data.get("success")}')
    print(f'Message: {data.get("error", data.get("message", "No message"))}')
    
    if data.get('success'):
        job_id = data.get('results', {}).get('instagram', {}).get('job_id')
        print(f'✅ JOB TRIGGERED: {job_id}')
        print('⏳ Data collection started - check again in 2-3 minutes')
    else:
        print('❌ SCRAPER TRIGGER FAILED')
        
except Exception as e:
    print(f'Trigger Error: {e}')

print('\n' + '=' * 50)
print('📋 DIAGNOSIS:')
print('- If folders return 404, no scraped data exists yet')
print('- Need to trigger scrapers and collect data')
print('- System is working but needs data population')