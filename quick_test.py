import requests

api_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/'
test_data = {'folder_id': 1, 'user_id': 3, 'num_of_posts': 5, 'date_range': {'start_date': '2025-10-01T00:00:00.000Z', 'end_date': '2025-10-08T00:00:00.000Z'}}

try:
    response = requests.post(api_url, json=test_data)
    if response.status_code == 200:
        data = response.json()
        print('✅ System working!')
        print(f'Success: {data.get("success")}')
        job_id = data.get('results', {}).get('instagram', {}).get('job_id')
        print(f'Job: {job_id}')
        print('🎉 NO MORE DISCOVERY PHASE ERRORS!')
    else:
        print(f'Status: {response.status_code}')
except Exception as e:
    print(f'Error: {e}')