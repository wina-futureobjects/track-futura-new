import requests
import json

def force_execute_production_batch_job():
    """Force execute the batch job on production and check detailed errors"""
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("=== FORCE EXECUTING PRODUCTION BATCH JOB ===")
    print()
    
    # Execute the existing batch job
    batch_job_id = 2
    print(f"🚀 Force executing batch job {batch_job_id}...")
    
    response = requests.post(
        f"{BASE_URL}/api/brightdata/batch-jobs/{batch_job_id}/execute/",
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"📊 Response Status: {response.status_code}")
    print(f"📊 Response Headers: {dict(response.headers)}")
    print(f"📊 Response Content: {response.text}")
    
    if response.status_code != 200:
        print("\n❌ EXECUTION FAILED!")
        print("Let me check if the BrightData service is properly configured...")
        
        # Check if the service actually exists and is working
        print("\n🧪 Testing BrightData API directly from production perspective...")
        
        # Get the config to test with
        config_response = requests.get(f"{BASE_URL}/api/brightdata/configs/1/")
        if config_response.status_code == 200:
            config = config_response.json()
            print(f"✅ Config found: {config['name']}")
            print(f"   Dataset ID: {config['dataset_id']}")
            print(f"   API Token: {config['api_token'][:10]}...")
            
            # Test the actual BrightData API call directly
            test_url = "https://api.brightdata.com/datasets/v3/trigger"
            test_params = {
                'dataset_id': config['dataset_id'],
                'include_errors': 'true',
                'type': 'discover_new',
                'discover_by': 'url'
            }
            
            test_payload = [{
                "url": "https://www.instagram.com/nike/",
                "num_of_posts": 1,
                "start_date": "",
                "end_date": "",
                "post_type": "Post"
            }]
            
            headers = {
                'Authorization': f'Bearer {config["api_token"]}',
                'Content-Type': 'application/json'
            }
            
            api_response = requests.post(test_url, params=test_params, json=test_payload, headers=headers, timeout=30)
            
            print(f"\n🔍 Direct API Test:")
            print(f"   Status: {api_response.status_code}")
            if api_response.status_code == 200:
                api_data = api_response.json()
                print(f"   ✅ SUCCESS! Snapshot ID: {api_data.get('snapshot_id')}")
                print("\n🚨 THE API WORKS! The issue is in the production service execution!")
            else:
                print(f"   ❌ API Failed: {api_response.text}")
        else:
            print(f"❌ Failed to get config: {config_response.status_code}")
    else:
        print("✅ Execution successful!")
        result = response.json()
        print(f"Result: {result}")

if __name__ == "__main__":
    force_execute_production_batch_job()