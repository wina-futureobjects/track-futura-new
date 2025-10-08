import requests
import json
from datetime import datetime

token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
job_id = 's_mghy2ys41je6of7vqb'

print(f'🔍 Checking BrightData Job Status: {job_id}')
print('=' * 60)

# Check job status
url = f'https://api.brightdata.com/datasets/v3/snapshot/{job_id}?format=json'
headers = {'Authorization': f'Bearer {token}'}

try:
    response = requests.get(url, headers=headers)
    print(f'📡 API Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'📊 Job Status: {data.get("status", "Unknown")}')
        print(f'📅 Created: {data.get("created_at", "Unknown")}')
        print(f'📈 Progress: {data.get("progress", "0")}%')
        
        if "errors" in data and data["errors"]:
            print('❌ Errors Found:')
            for error in data["errors"]:
                print(f'   - {error}')
        else:
            print('✅ No errors detected')
            
        # Check for discovery phase specifically
        if "discovery_phase_error" in str(data).lower():
            print('❌ Discovery Phase Error Still Present')
        elif data.get("status") == "running":
            print('✅ Job is running - Discovery phase passed!')
        elif data.get("status") == "completed":
            print('🎉 Job completed successfully!')
            
        print('\n🔗 Full Response:')
        print(json.dumps(data, indent=2))
    else:
        print(f'❌ Failed to get job status: {response.text}')
        
except Exception as e:
    print(f'❌ Error checking job: {e}')

print('\n' + '=' * 60)
print('✅ BrightData Job Status Check Complete')