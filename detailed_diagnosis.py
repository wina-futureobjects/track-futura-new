import requests
import json

def detailed_execution_test():
    """Perform detailed testing to identify exact failure point"""
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("=== DETAILED EXECUTION DIAGNOSIS ===")
    print()
    
    # First, verify the configuration has api_token by creating a test config
    print("🧪 Testing if API token is properly saved...")
    
    test_config = {
        "name": "TEST Instagram Config",
        "platform": "instagram",
        "dataset_id": "gd_lk5ns7kz21pck8jpis", 
        "api_token": "8af6995e-3baa-4b69-9df7-8d7671e621eb",
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/brightdata/configs/",
        json=test_config,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 201:
        config = response.json()
        config_id = config['id']
        print(f"✅ Created test config (ID: {config_id})")
        
        # Try to get it back and see if api_token field exists
        get_response = requests.get(f"{BASE_URL}/api/brightdata/configs/{config_id}/")
        if get_response.status_code == 200:
            retrieved_config = get_response.json()
            print(f"📊 Retrieved config fields: {list(retrieved_config.keys())}")
            
            if 'api_token' not in retrieved_config:
                print("✅ API token is hidden (write_only works)")
            else:
                print(f"⚠️ API token is visible: {retrieved_config.get('api_token', 'None')}")
        
        # Now test the BrightData service test connection endpoint
        print(f"\n🧪 Testing BrightData connection for config {config_id}...")
        
        test_response = requests.post(
            f"{BASE_URL}/api/brightdata/configs/{config_id}/test_connection/",
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Test Connection Status: {test_response.status_code}")
        print(f"📊 Test Connection Response: {test_response.text}")
        
        if test_response.status_code == 200:
            test_result = test_response.json()
            print(f"✅ Connection test successful!")
            print(f"   Result: {test_result}")
            
            # If connection test works, try with the create_and_execute endpoint
            print(f"\n🚀 Testing create_and_execute endpoint...")
            
            batch_job_data = {
                "name": "Create and Execute Test",
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
                print("\n🎉🎉🎉 SUCCESS! Create and Execute works! 🎉🎉🎉")
                result = create_execute_response.json()
                print(f"✅ Job ID: {result.get('id')}")
                print(f"✅ Message: {result.get('message')}")
                return True
            else:
                print(f"\n❌ Create and Execute failed: {create_execute_response.text}")
                
        else:
            print(f"❌ Connection test failed: {test_response.text}")
            print("🔍 This suggests the BrightData service has an internal issue")
            
    else:
        print(f"❌ Failed to create test config: {response.status_code}")
        print(f"   Error: {response.text}")
    
    return False

if __name__ == "__main__":
    detailed_execution_test()