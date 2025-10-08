import requests
import json

def test_frontend_workflow_creation():
    """Test creating a workflow through the frontend API endpoints"""
    
    print("🔍 TESTING FRONTEND WORKFLOW CREATION")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test 1: Check available platforms
    print("1️⃣ Testing available platforms...")
    try:
        response = requests.get(f"{BASE_URL}/api/workflow/input-collections/available_platforms/")
        if response.status_code == 200:
            platforms = response.json()
            print(f"   ✅ Found {len(platforms)} platforms:")
            for platform in platforms:
                print(f"      - {platform['name']}: {platform['display_name']}")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False
    
    # Test 2: Check platform services
    print("\n2️⃣ Testing platform services...")
    try:
        response = requests.get(f"{BASE_URL}/api/workflow/input-collections/platform_services/")
        if response.status_code == 200:
            services = response.json()
            print(f"   ✅ Found {len(services)} platform services:")
            for service in services:
                print(f"      - {service['platform']['name']} + {service['service']['name']}")
                if service['platform']['name'] == 'instagram':
                    instagram_service_id = service['id']
                    print(f"        📌 Instagram service ID: {instagram_service_id}")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False
    
    # Test 3: Try to create an input collection
    print("\n3️⃣ Testing input collection creation...")
    try:
        # Find Instagram platform service ID
        response = requests.get(f"{BASE_URL}/api/workflow/input-collections/platform_services/")
        services = response.json()
        instagram_service = None
        for service in services:
            if service['platform']['name'] == 'instagram':
                instagram_service = service
                break
        
        if not instagram_service:
            print("   ❌ No Instagram service found!")
            return False
        
        input_data = {
            "project": 3,  # Your project ID
            "platform_service": instagram_service['id'],
            "target_urls": ["https://www.instagram.com/nike/"],
            "source_names": ["Nike Instagram Test"],
            "configuration": {
                "num_of_posts": 5,
                "post_type": "Post"
            }
        }
        
        print(f"   📝 Creating input collection with data: {json.dumps(input_data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/workflow/input-collections/",
            json=input_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            collection_data = response.json()
            collection_id = collection_data['id']
            print(f"   ✅ Created input collection ID: {collection_id}")
            
            # Test 4: Configure the job
            print("\n4️⃣ Testing job configuration...")
            job_config = {
                "name": "Frontend Test Nike Scrape",
                "num_of_posts": 5,
                "auto_create_folders": True
            }
            
            config_response = requests.post(
                f"{BASE_URL}/api/workflow/input-collections/{collection_id}/configure_job/",
                json=job_config,
                headers={'Content-Type': 'application/json'}
            )
            
            if config_response.status_code == 201:
                config_data = config_response.json()
                print(f"   ✅ Configured job: {config_data.get('batch_job_name', 'Unknown')}")
                print(f"   ✅ Batch Job ID: {config_data.get('batch_job_id', 'Unknown')}")
                
                # Test 5: Check if BrightData scraper requests were created
                print("\n5️⃣ Checking BrightData scraper requests...")
                scraper_response = requests.get(f"{BASE_URL}/api/brightdata/scraper-requests/")
                if scraper_response.status_code == 200:
                    scrapers = scraper_response.json()
                    print(f"   ✅ Found {len(scrapers)} scraper requests total")
                    
                    recent_scrapers = [s for s in scrapers if 'Frontend Test' in s.get('source_name', '') or s.get('request_id', '').startswith('working_')]
                    print(f"   ✅ Found {len(recent_scrapers)} recent scraper requests")
                    
                    for scraper in recent_scrapers[-5:]:  # Show last 5
                        print(f"      - {scraper.get('source_name', 'Unknown')}: {scraper.get('status', 'Unknown')}")
                        if scraper.get('snapshot_id'):
                            print(f"        🎯 Snapshot: {scraper['snapshot_id']}")
                
                return True
            else:
                print(f"   ❌ Job configuration failed: {config_response.status_code} - {config_response.text}")
                return False
        else:
            print(f"   ❌ Input collection creation failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_brightdata_configs():
    """Test BrightData configurations"""
    
    print("\n🔧 TESTING BRIGHTDATA CONFIGURATIONS")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    try:
        response = requests.get(f"{BASE_URL}/api/brightdata/configs/")
        if response.status_code == 200:
            configs = response.json()
            print(f"✅ Found {len(configs)} BrightData configs:")
            for config in configs:
                print(f"   - ID {config['id']}: {config['platform']} - {config['content_type']}")
                print(f"     Dataset: {config['dataset_id']}")
                print(f"     Enabled: {config['is_enabled']}")
        else:
            print(f"❌ BrightData configs failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error checking configs: {str(e)}")

if __name__ == "__main__":
    print("🚨 COMPREHENSIVE FRONTEND WORKFLOW TEST 🚨")
    print()
    
    # Test BrightData configs first
    test_brightdata_configs()
    
    # Test the full workflow
    success = test_frontend_workflow_creation()
    
    if success:
        print("\n🎉🎉🎉 FRONTEND WORKFLOW TEST SUCCESSFUL! 🎉🎉🎉")
        print("✅ Your frontend should now be able to create scraping jobs!")
        print("✅ Check the workflow management page!")
    else:
        print("\n❌ FRONTEND WORKFLOW TEST FAILED!")
        print("❌ There are configuration issues preventing frontend scraping!")