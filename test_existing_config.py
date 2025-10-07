import requests
import json

def test_existing_config():
    """Test the existing config on production"""
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("=== TESTING EXISTING CONFIG ===")
    print()
    
    # Test the connection with existing config
    config_id = 3  # Instagram config
    
    print(f"🧪 Testing connection for config {config_id}...")
    
    test_response = requests.post(
        f"{BASE_URL}/api/brightdata/configs/{config_id}/test_connection/",
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"📊 Test Connection Status: {test_response.status_code}")
    print(f"📊 Test Connection Response: {test_response.text}")
    
    if test_response.status_code == 200:
        print("✅ Connection test passed!")
        
        # Test create_and_execute
        print(f"\n🚀 Testing create_and_execute...")
        
        batch_job_data = {
            "name": "Direct Create and Execute Test",
            "project": 3,
            "platforms_to_scrape": ["instagram"],
            "content_types_to_scrape": {
                "instagram": ["posts"]
            },
            "num_of_posts": 1,
            "platform_params": {
                "target_url": "https://www.instagram.com/nike/"
            }
        }
        
        create_execute_response = requests.post(
            f"{BASE_URL}/api/brightdata/batch-jobs/create_and_execute/",
            json=batch_job_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Create & Execute Status: {create_execute_response.status_code}")
        print(f"📊 Create & Execute Response: {create_execute_response.text}")
        
        if create_execute_response.status_code == 201:
            result = create_execute_response.json()
            print("\n🎉🎉🎉 SUCCESS! BrightData is working! 🎉🎉🎉")
            print(f"✅ Job ID: {result.get('id')}")
            print(f"✅ Message: {result.get('message')}")
            
            # Check if scraper requests were created
            job_id = result.get('id')
            if job_id:
                print(f"\n📊 Checking scraper requests for job {job_id}...")
                scraper_response = requests.get(f"{BASE_URL}/api/brightdata/scraper-requests/?batch_job_id={job_id}")
                if scraper_response.status_code == 200:
                    scraper_data = scraper_response.json()
                    requests_count = scraper_data.get('count', 0)
                    print(f"✅ Created {requests_count} scraper requests")
                    
                    for req in scraper_data.get('results', []):
                        print(f"   - Request {req['id']}: {req['status']}")
                        if req.get('snapshot_id'):
                            print(f"     🎯 Snapshot ID: {req['snapshot_id']}")
                        
            return True
        else:
            print(f"\n❌ Create and Execute failed: {create_execute_response.text}")
    else:
        print(f"❌ Connection test failed: {test_response.text}")
        
        # If test connection fails, the issue is the missing API token
        # Let's try to update the config manually
        print(f"\n🔧 Updating config {config_id} with API token...")
        
        update_data = {
            "name": "Instagram Posts Scraper",
            "platform": "instagram",
            "dataset_id": "gd_lk5ns7kz21pck8jpis",
            "api_token": "8af6995e-3baa-4b69-9df7-8d7671e621eb",
            "is_active": True
        }
        
        update_response = requests.put(
            f"{BASE_URL}/api/brightdata/configs/{config_id}/",
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Update Status: {update_response.status_code}")
        if update_response.status_code == 200:
            print("✅ Config updated, retesting connection...")
            
            # Retry test connection
            retry_response = requests.post(
                f"{BASE_URL}/api/brightdata/configs/{config_id}/test_connection/",
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"📊 Retry Connection Status: {retry_response.status_code}")
            print(f"📊 Retry Connection Response: {retry_response.text}")
            
            if retry_response.status_code == 200:
                print("🎉 NOW IT WORKS! The API token was missing!")
                return True
        else:
            print(f"❌ Update failed: {update_response.text}")
    
    return False

if __name__ == "__main__":
    test_existing_config()