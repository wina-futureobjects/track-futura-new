#!/usr/bin/env python3
"""
Test the new trigger-scraper endpoint
"""
import requests
import time
import json

def test_trigger_endpoint():
    print('🔄 Waiting for deployment...')
    
    # Wait for deployment
    for i in range(12):
        try:
            r = requests.get('https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/', timeout=5)
            if r.status_code == 200:
                print(f'✅ Server is up! Status: {r.status_code}')
                break
        except:
            pass
        print(f'   Waiting... ({i+1}/12)')
        time.sleep(5)
    
    print('\n🚀 Testing trigger-scraper endpoint...')
    test_payload = {
        'platform': 'instagram',
        'urls': ['https://instagram.com/nike'],
        'input_collection_id': 1
    }
    
    try:
        response = requests.post(
            'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/',
            json=test_payload,
            timeout=30
        )
        print(f'Trigger response status: {response.status_code}')
        print(f'Trigger response: {response.text[:500]}...')
        
        if response.status_code == 200:
            print('✅ SUCCESS! BrightData trigger endpoint is working!')
            data = response.json()
            if data.get('batch_job_id'):
                print(f'✅ Batch job created: {data["batch_job_id"]}')
                print('✅ Check your BrightData dashboard for incoming requests!')
        else:
            print(f'❌ Trigger failed with status {response.status_code}')
            
    except Exception as e:
        print(f'❌ Error testing endpoint: {e}')

if __name__ == "__main__":
    test_trigger_endpoint()