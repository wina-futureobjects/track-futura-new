import requests
import json

def update_production_brightdata_configs():
    """Update production BrightData configs with working API key"""
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    API_KEY = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    print("=== UPDATING PRODUCTION BRIGHTDATA CONFIGS ===")
    print()
    
    # Configuration updates
    config_updates = [
        {
            'id': 1,
            'platform': 'instagram',
            'dataset_id': 'gd_lk5ns7kz21pck8jpis',
            'name': 'Instagram Posts Scraper'
        },
        {
            'id': 2, 
            'platform': 'facebook',
            'dataset_id': 'gd_lkaxegm826bjpoo9m5',
            'name': 'Facebook Posts Scraper'
        }
    ]
    
    for config in config_updates:
        print(f"📝 Updating {config['platform']} configuration...")
        
        update_data = {
            'name': config['name'],
            'platform': config['platform'],
            'dataset_id': config['dataset_id'],
            'api_token': API_KEY,
            'is_active': True
        }
        
        response = requests.patch(
            f"{BASE_URL}/api/brightdata/configs/{config['id']}/",
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            updated_config = response.json()
            print(f"✅ Updated {config['platform']} config successfully")
            print(f"   Dataset ID: {updated_config['dataset_id']}")
            print(f"   Active: {updated_config['is_active']}")
        else:
            print(f"❌ Failed to update {config['platform']} config: {response.status_code}")
            print(f"   Error: {response.text}")
        
        print()
    
    # Test the API key directly
    print("🧪 Testing API key directly...")
    test_url = "https://api.brightdata.com/datasets/v3/trigger"
    test_params = {
        'dataset_id': 'gd_lk5ns7kz21pck8jpis',
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
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(test_url, params=test_params, json=test_payload, headers=headers, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API key test successful!")
        print(f"   Snapshot ID: {data.get('snapshot_id')}")
        print()
        print("🎯 PRODUCTION CONFIGS SHOULD NOW WORK!")
        print("Try creating a scraping run again on the frontend.")
    else:
        print(f"❌ API key test failed: {response.status_code}")
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    update_production_brightdata_configs()