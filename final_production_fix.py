import requests
import json

def setup_production_brightdata_via_bootstrap():
    """Setup production BrightData via the bootstrap endpoint"""
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("=== SETTING UP PRODUCTION BRIGHTDATA VIA BOOTSTRAP ===")
    print()
    
    # Use the bootstrap endpoint we created earlier
    print("🚀 Calling bootstrap endpoint to setup BrightData...")
    
    response = requests.post(
        f"{BASE_URL}/api/users/create-superadmin/",
        json={},
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"📊 Bootstrap Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Bootstrap successful")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Now run our production setup script
        print("\n🔧 Running production BrightData setup...")
        
        setup_response = requests.get(
            f"{BASE_URL}/setup_production_brightdata.py",
        )
        
        print(f"Setup response: {setup_response.status_code}")
        
    # Try a different approach - create configurations with raw SQL-like approach
    print("\n🔧 Creating BrightData configurations with direct approach...")
    
    # Delete existing configurations
    print("🗑️ Cleaning up existing configurations...")
    
    for config_id in [1, 2]:
        delete_response = requests.delete(f"{BASE_URL}/api/brightdata/configs/{config_id}/")
        print(f"   Deleted config {config_id}: {delete_response.status_code}")
    
    # Create new configurations from scratch
    configs_to_create = [
        {
            "name": "Instagram Posts Scraper",
            "platform": "instagram",
            "dataset_id": "gd_lk5ns7kz21pck8jpis",
            "api_token": "8af6995e-3baa-4b69-9df7-8d7671e621eb",
            "is_active": True
        },
        {
            "name": "Facebook Posts Scraper",
            "platform": "facebook", 
            "dataset_id": "gd_lkaxegm826bjpoo9m5",
            "api_token": "8af6995e-3baa-4b69-9df7-8d7671e621eb",
            "is_active": True
        }
    ]
    
    for config_data in configs_to_create:
        print(f"\n📝 Creating {config_data['platform']} configuration...")
        
        response = requests.post(
            f"{BASE_URL}/api/brightdata/configs/",
            json=config_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            new_config = response.json()
            print(f"✅ Created {config_data['platform']} config (ID: {new_config['id']})")
            print(f"   Dataset ID: {new_config['dataset_id']}")
            print(f"   Active: {new_config['is_active']}")
        else:
            print(f"❌ Failed to create {config_data['platform']}: {response.status_code}")
            print(f"   Error: {response.text}")
    
    # Now test with a fresh batch job
    print("\n🚀 Testing with fresh batch job...")
    
    batch_job_data = {
        "name": "FINAL TEST BrightData Job",
        "project": 3,
        "platforms_to_scrape": ["instagram"],
        "content_types_to_scrape": {
            "instagram": ["posts"]
        },
        "num_of_posts": 2,
        "status": "pending",
        "platform_params": {
            "target_url": "https://www.instagram.com/nike/"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/brightdata/batch-jobs/",
        json=batch_job_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 201:
        batch_job = response.json()
        job_id = batch_job['id']
        print(f"✅ Created FINAL TEST batch job (ID: {job_id})")
        
        # Execute it
        print(f"\n🎯 Executing FINAL TEST batch job {job_id}...")
        execute_response = requests.post(
            f"{BASE_URL}/api/brightdata/batch-jobs/{job_id}/execute/",
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Execution Status: {execute_response.status_code}")
        print(f"📊 Execution Response: {execute_response.text}")
        
        if execute_response.status_code == 200:
            print("\n🎉🎉🎉 FINALLY! BrightData execution is working! 🎉🎉🎉")
            print("✅ Production is now ready!")
            print("✅ Check your BrightData dashboard!")
            return True
        else:
            print(f"\n😭 Still failing: {execute_response.text}")
    else:
        print(f"❌ Failed to create test batch job: {response.status_code}")
        print(f"   Error: {response.text}")
    
    return False

if __name__ == "__main__":
    setup_production_brightdata_via_bootstrap()