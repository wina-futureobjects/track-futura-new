import requests
from datetime import datetime

token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
job_id = 's_mghybon32gx22ep4f1'

print('🔍 Checking the working job...')
status_url = f'https://api.brightdata.com/datasets/v3/snapshot/{job_id}?format=json'
headers = {'Authorization': f'Bearer {token}'}

try:
    response = requests.get(status_url, headers=headers)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Job Status: {data.get("status", "Unknown")}')
        if "errors" in data and data["errors"]:
            print('❌ Errors found')
            for error in data["errors"]:
                print(f'   - {error}')
        else:
            print('✅ No errors - this job worked!')
    else:
        print(f'Failed: {response.text[:100]}')
except Exception as e:
    print(f'Error: {e}')

print('')
print('💡 KEY INSIGHT:')
print('The working date range was: 08-09-2025 to 05-10-2025 (past dates)')
print('Current failing range: 01-10-2025 to 08-10-2025 (includes today)')
print('BrightData likely needs past dates only for data discovery!')