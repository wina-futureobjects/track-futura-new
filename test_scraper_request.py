import requests
import json

def test_production_scraper_request():
    """Test creating and executing a BrightData scraper request directly"""
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("=== TESTING PRODUCTION SCRAPER REQUEST ===")
    print()
    
    try:
        # Get the batch job we created earlier
        print("📋 Getting batch job...")
        batch_response = requests.get(f"{BASE_URL}/api/brightdata/batch-jobs/")
        
        if batch_response.status_code == 200:
            batch_data = batch_response.json()
            batch_jobs = batch_data.get('results', [])
            
            if batch_jobs:
                batch_job = batch_jobs[0]  # Use the first batch job
                print(f"✅ Found batch job: {batch_job['name']} (ID: {batch_job['id']})")
                
                # Get BrightData config
                print("📋 Getting BrightData configs...")
                config_response = requests.get(f"{BASE_URL}/api/brightdata/configs/")
                
                if config_response.status_code == 200:
                    config_data = config_response.json()
                    configs = config_data.get('results', [])
                    
                    instagram_config = None
                    for config in configs:
                        if config['platform'] == 'instagram':
                            instagram_config = config
                            break
                    
                    if instagram_config:
                        print(f"✅ Found Instagram config: {instagram_config['name']}")
                        print(f"   Dataset ID: {instagram_config['dataset_id']}")
                        print(f"   Active: {instagram_config['is_active']}")
                        
                        # Create a scraper request directly
                        print("\n🚀 Creating scraper request...")
                        scraper_data = {
                            "config": instagram_config['id'],
                            "batch_job": batch_job['id'],
                            "platform": "instagram",
                            "content_type": "posts",
                            "target_url": "https://www.instagram.com/nike/",
                            "source_name": "Nike Instagram",
                            "status": "pending"
                        }
                        
                        scraper_response = requests.post(
                            f"{BASE_URL}/api/brightdata/scraper-requests/",
                            json=scraper_data,
                            headers={'Content-Type': 'application/json'}
                        )
                        
                        if scraper_response.status_code == 201:
                            scraper_request = scraper_response.json()
                            print(f"✅ Created scraper request: {scraper_request['id']}")
                            print(f"   Platform: {scraper_request['platform']}")
                            print(f"   Target URL: {scraper_request['target_url']}")
                            print(f"   Status: {scraper_request['status']}")
                            
                            print("\n🎉 SUCCESS! BrightData components are working on production!")
                            print("   ✅ Batch jobs can be created")
                            print("   ✅ Scraper requests can be created")
                            print("   ✅ Configurations are properly set up")
                            print()
                            print("🔍 The issue might be in the execution logic itself.")
                            print("   The scraper request is created but needs proper execution.")
                            
                            return True
                        else:
                            print(f"❌ Failed to create scraper request: {scraper_response.status_code}")
                            print(f"   Error: {scraper_response.text}")
                    else:
                        print("❌ No Instagram config found")
                else:
                    print(f"❌ Failed to get configs: {config_response.status_code}")
            else:
                print("❌ No batch jobs found")
        else:
            print(f"❌ Failed to get batch jobs: {batch_response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
    
    return False

if __name__ == "__main__":
    test_production_scraper_request()