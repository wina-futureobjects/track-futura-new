import requests
import json

def check_database_configurations():
    """Check the database configurations for platforms and services"""
    
    print("🔍 CHECKING DATABASE CONFIGURATIONS")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Check existing platforms
    print("1️⃣ Checking platforms in database...")
    try:
        response = requests.get(f"{BASE_URL}/api/workflow/input-collections/available_platforms/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            platforms = response.json()
            print(f"   Found {len(platforms)} platforms:")
            for platform in platforms:
                print(f"      - {platform}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    
    # Check platform services
    print("\n2️⃣ Checking platform services...")
    try:
        response = requests.get(f"{BASE_URL}/api/workflow/input-collections/platform_services/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            services = response.json()
            print(f"   Found {len(services)} services:")
            for service in services:
                print(f"      - {service}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    
    # Check BrightData configs in detail
    print("\n3️⃣ Checking BrightData configs in detail...")
    try:
        response = requests.get(f"{BASE_URL}/api/brightdata/configs/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            raw_response = response.text
            print(f"   Raw response: {raw_response[:500]}...")
            
            try:
                configs = response.json()
                if isinstance(configs, list):
                    print(f"   Found {len(configs)} configs:")
                    for config in configs:
                        print(f"      - ID: {config.get('id', 'N/A')}")
                        print(f"        Platform: {config.get('platform', 'N/A')}")
                        print(f"        Dataset: {config.get('dataset_id', 'N/A')}")
                        print(f"        Enabled: {config.get('is_enabled', 'N/A')}")
                else:
                    print(f"   Unexpected format: {type(configs)}")
            except Exception as parse_error:
                print(f"   JSON parse error: {str(parse_error)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {str(e)}")

def create_missing_platforms_and_services():
    """Create the missing platforms and services via API"""
    
    print("\n🔧 CREATING MISSING PLATFORMS AND SERVICES")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Try to create platforms directly via Django management
    print("Creating platforms and services via API call...")
    
    # Create a direct setup script
    setup_data = {
        "action": "setup_platforms",
        "platforms": [
            {
                "name": "instagram",
                "display_name": "Instagram",
                "description": "Instagram social media platform",
                "is_enabled": True
            },
            {
                "name": "facebook", 
                "display_name": "Facebook",
                "description": "Facebook social media platform", 
                "is_enabled": True
            }
        ],
        "services": [
            {
                "name": "posts",
                "display_name": "Posts Scraping", 
                "description": "Scrape posts from social media",
                "is_enabled": True
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/brightdata/setup-platforms/",
            json=setup_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Setup response: {response.status_code}")
        if response.status_code in [200, 201]:
            print("✅ Platforms and services created successfully!")
        else:
            print(f"❌ Setup failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Setup exception: {str(e)}")

if __name__ == "__main__":
    check_database_configurations()
    create_missing_platforms_and_services()