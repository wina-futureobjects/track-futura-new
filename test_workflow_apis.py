import requests
import json

def test_workflow_apis():
    """Test workflow API endpoints"""
    base_url = "http://localhost:8080/api"
    
    try:
        # Test input collections endpoint
        print('=== TESTING INPUT COLLECTIONS API ===')
        response = requests.get(f'{base_url}/workflow/input-collections/')
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'Total collections: {len(data)}')
            if isinstance(data, list):
                for i, collection in enumerate(data):
                    if i >= 2:
                        break
                    if isinstance(collection, dict):
                        cid = collection.get('id')
                        status = collection.get('status')
                        print(f'  Collection {cid}: {status}')
            else:
                print(f'  Data structure: {type(data)}')
        else:
            print(f'Error: {response.text[:200]}')
        
        print('\n=== TESTING PLATFORM SERVICES API ===')
        response = requests.get(f'{base_url}/workflow/input-collections/platform_services/')
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'Platform services found: {len(data)}')
            for i, ps in enumerate(data):
                if i >= 2:
                    break
                platform_name = ps.get('platform', {}).get('name', 'unknown')
                service_name = ps.get('service', {}).get('name', 'unknown')
                print(f'  {platform_name} - {service_name}')
        else:
            print(f'Error: {response.text[:200]}')
        
        print('\n=== TESTING SCRAPING RUNS API ===')
        response = requests.get(f'{base_url}/workflow/scraping-runs/')
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'Scraping runs found: {len(data)}')
            for i, run in enumerate(data):
                if i >= 2:
                    break
                rid = run.get('id')
                name = run.get('name')
                status = run.get('status')
                print(f'  Run {rid}: {name} - {status}')
        else:
            print(f'Error: {response.text[:200]}')
        
        print('\n=== TESTING BRIGHTDATA TRIGGER API ===')
        payload = {
            "platform": "instagram",
            "urls": ["https://www.instagram.com/nike/"],
            "folder_id": 1
        }
        
        response = requests.post(f'{base_url}/brightdata/trigger-scraper/', json=payload)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'SUCCESS: {result.get("message")}')
            print(f'Batch Job ID: {result.get("batch_job_id")}')
        else:
            print(f'Error: {response.text[:200]}')

    except Exception as e:
        print(f'Error testing APIs: {e}')

if __name__ == "__main__":
    test_workflow_apis()