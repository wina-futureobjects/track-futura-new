import requests
import json
from datetime import datetime, timedelta

# Direct BrightData test to confirm working vs failing dates
token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
dataset_id = 'gd_lk5ns7kz21pck8jpis'
url = 'https://api.brightdata.com/datasets/v3/trigger'

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
}

params = {
    'dataset_id': dataset_id,
    'include_errors': 'true',
    'type': 'discover_new',
    'discover_by': 'url',
}

print('🧪 DIRECT BRIGHTDATA TESTING')
print('=' * 50)

# Test 1: Your working example (September dates)
print('\n🟢 TEST 1: Known working dates (September)')
working_payload = [{
    'url': 'https://www.instagram.com/nike/',
    'num_of_posts': 10,
    'posts_to_not_include': '',
    'start_date': '01-09-2025',
    'end_date': '30-09-2025', 
    'post_type': 'Post'
}]

try:
    response = requests.post(url, headers=headers, params=params, json=working_payload, timeout=30)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text[:200]}')
    
    if response.status_code == 200:
        data = response.json()
        job_id = data.get('snapshot_id')
        print(f'✅ September dates work! Job: {job_id}')
        
        # Quick status check
        import time
        time.sleep(10)
        status_url = f'https://api.brightdata.com/datasets/v3/snapshot/{job_id}?format=json'
        status_response = requests.get(status_url, headers={'Authorization': f'Bearer {token}'})
        if 'Discovery phase error' in status_response.text:
            print('❌ Still has discovery error')
        else:
            print('✅ No discovery error')
            
except Exception as e:
    print(f'Error: {e}')

# Test 2: Your failing example (October dates including today)
print('\n🔴 TEST 2: Failing dates (October including today)')
failing_payload = [{
    'url': 'https://www.instagram.com/nike/',
    'num_of_posts': 10,
    'posts_to_not_include': '',
    'start_date': '01-10-2025',
    'end_date': '08-10-2025',  # TODAY!
    'post_type': 'Post'
}]

try:
    response = requests.post(url, headers=headers, params=params, json=failing_payload, timeout=30)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text[:200]}')
    
    if response.status_code == 200:
        data = response.json()
        job_id = data.get('snapshot_id')
        print(f'📊 October dates job: {job_id}')
        
        # Quick status check
        import time
        time.sleep(10)
        status_url = f'https://api.brightdata.com/datasets/v3/snapshot/{job_id}?format=json'
        status_response = requests.get(status_url, headers={'Authorization': f'Bearer {token}'})
        if 'Discovery phase error' in status_response.text:
            print('❌ Has discovery phase error (as expected)')
        else:
            print('✅ No discovery error (unexpected)')
            
except Exception as e:
    print(f'Error: {e}')

# Test 3: Safe October dates (past only)
print('\n🟡 TEST 3: Safe October dates (past only)')
today = datetime.now()
safe_end = today - timedelta(days=2)  # October 6th
safe_start = safe_end - timedelta(days=7)  # October 1st is still past, so use Sep 29

safe_payload = [{
    'url': 'https://www.instagram.com/nike/',
    'num_of_posts': 10,
    'posts_to_not_include': '',
    'start_date': safe_start.strftime('%d-%m-%Y'),
    'end_date': safe_end.strftime('%d-%m-%Y'),
    'post_type': 'Post'
}]

print(f'Testing dates: {safe_start.strftime("%d-%m-%Y")} to {safe_end.strftime("%d-%m-%Y")}')

try:
    response = requests.post(url, headers=headers, params=params, json=safe_payload, timeout=30)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text[:200]}')
    
    if response.status_code == 200:
        data = response.json()
        job_id = data.get('snapshot_id')
        print(f'📊 Safe October dates job: {job_id}')
        
        # Quick status check
        import time
        time.sleep(10)
        status_url = f'https://api.brightdata.com/datasets/v3/snapshot/{job_id}?format=json'
        status_response = requests.get(status_url, headers={'Authorization': f'Bearer {token}'})
        if 'Discovery phase error' in status_response.text:
            print('❌ Still has discovery error - might be different issue')
        else:
            print('✅ No discovery error - safe dates work!')
            
except Exception as e:
    print(f'Error: {e}')

print('\n' + '=' * 50)
print('🎯 CONCLUSION: The system needs to ensure NO dates include today (Oct 8)')