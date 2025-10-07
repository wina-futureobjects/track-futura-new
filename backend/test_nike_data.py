import requests
import json

headers = {'Authorization': 'Token e242daf2ea05576f08fb8d808aba529b0c7ffbab'}
r = requests.get('http://127.0.0.1:8000/api/apify/batch-jobs/8/results/', headers=headers)
data = r.json()

print(f'Total results: {data["total_results"]}')
print('Sample Nike post:')
print(json.dumps(data['results'][0], indent=2))