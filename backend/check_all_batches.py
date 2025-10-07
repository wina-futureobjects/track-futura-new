import requests
import json

headers = {'Authorization': 'Token e242daf2ea05576f08fb8d808aba529b0c7ffbab'}

# Check all batch jobs for which ones have results
for batch_id in [1, 2, 8, 9, 10, 11]:
    r = requests.get(f'http://127.0.0.1:8000/api/apify/batch-jobs/{batch_id}/results/', headers=headers)
    if r.status_code == 200:
        data = r.json()
        total = data.get('total_results', 0)
        print(f'Batch Job {batch_id}: {total} results')
        if total > 0:
            print(f'  Sample result structure:')
            print(f'  {list(data["results"][0].keys()) if data["results"] else "No results"}')
            if data["results"]:
                sample = data["results"][0]
                print(f'  Sample data: {json.dumps(sample, indent=4)[:500]}...')
    else:
        print(f'Batch Job {batch_id}: Error {r.status_code}')