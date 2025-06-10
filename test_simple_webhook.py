import requests
import json

# Test webhook endpoint directly
url = 'http://localhost:8000/api/brightdata/webhook/'
data = [{'post_id': 'test123', 'content': 'test'}]
headers = {
    'Content-Type': 'application/json',
    'X-Platform': 'facebook'
}

try:
    response = requests.post(url, json=data, headers=headers)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text[:1000]}')
except Exception as e:
    print(f'Error: {e}')
