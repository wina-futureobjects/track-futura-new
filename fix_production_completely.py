import requests
import json

def fix_production_configs_completely():
    """Completely fix the production BrightData configurations with API tokens"""
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    API_KEY = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    print("=== COMPLETELY FIXING PRODUCTION CONFIGS ===")
    print()
    
    # Configuration updates with ALL required fields
    config_updates = [
        {
            'id': 1,
            'name': 'Instagram Posts Scraper',
            'platform': 'instagram',
            'dataset_id': 'gd_lk5ns7kz21pck8jpis',
            'api_token': API_KEY,
            'is_active': True
        },
        {
            'id': 2, 
            'name': 'Facebook Posts Scraper',
            'platform': 'facebook',
            'dataset_id': 'gd_lkaxegm826bjpoo9m5',
            'api_token': API_KEY,
            'is_active': True
        }
    ]
    
    for config in config_updates:
        print(f"🔧 COMPLETELY UPDATING {config['platform']} configuration...")
        
        # Use PUT to completely replace the configuration
        response = requests.put(
            f"{BASE_URL}/api/brightdata/configs/{config['id']}/",
            json=config,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            updated_config = response.json()
            print(f"✅ FIXED {config['platform']} config successfully")
            print(f"   Dataset ID: {updated_config['dataset_id']}")
            print(f"   Has API Token: {'api_token' in updated_config}")
            print(f"   Active: {updated_config['is_active']}")
        else:
            print(f"❌ Failed to fix {config['platform']} config: {response.status_code}")
            print(f"   Error: {response.text}")
        
        print()
    
    # Now create a fresh batch job with proper configuration
    print("🚀 Creating fresh batch job with proper config...")
    
    batch_job_data = {
        "name": "WORKING BrightData Job",
        "project": 3,
        "platforms_to_scrape": ["instagram"],
        "content_types_to_scrape": {
            "instagram": ["posts"]
        },
        "num_of_posts": 3,
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
        print(f"✅ Created fresh batch job: {batch_job['name']} (ID: {job_id})")
        
        # Try to execute it immediately
        print(f"\n🎯 Executing fresh batch job {job_id}...")
        execute_response = requests.post(
            f"{BASE_URL}/api/brightdata/batch-jobs/{job_id}/execute/",
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Execution Status: {execute_response.status_code}")
        print(f"📊 Execution Response: {execute_response.text}")
        
        if execute_response.status_code == 200:
            print("\n🎉 SUCCESS! BrightData execution is now working!")
            print("✅ Configurations fixed")
            print("✅ Batch job created") 
            print("✅ Batch job executed")
            print("✅ Check your BrightData dashboard for jobs!")
        else:
            print(f"\n❌ Still failing to execute: {execute_response.text}")
    else:
        print(f"❌ Failed to create batch job: {response.status_code}")
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    fix_production_configs_completely()