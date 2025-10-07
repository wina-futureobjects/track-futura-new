import requests
import json

headers = {'Authorization': 'Token e242daf2ea05576f08fb8d808aba529b0c7ffbab'}
r = requests.get('http://127.0.0.1:8000/api/apify/batch-jobs/11/results/', headers=headers)

print('Status:', r.status_code)
print('Response type:', type(r.json()))
response_data = r.json()
print('Response keys:', list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict')
print('Response length:', len(response_data) if isinstance(response_data, (list, dict)) else 'Not countable')
print('Full response:')
print(json.dumps(response_data, indent=2)[:1000], '...' if len(str(response_data)) > 1000 else '')