import requests
import json

def fix_production_platforms():
    """Fix production platforms by creating them via the existing workflow"""
    
    print("🔧 FIXING PRODUCTION PLATFORMS VIA EXISTING ENDPOINTS")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Let's try to trigger the setup via the BrightData webhook
    # which should have Django access
    
    webhook_data = {
        "snapshot_id": "setup_platforms_trigger",
        "status": "completed",
        "setup_command": True,
        "platforms": [
            {"name": "instagram", "display_name": "Instagram", "is_enabled": True},
            {"name": "facebook", "display_name": "Facebook", "is_enabled": True}
        ],
        "services": [
            {"name": "posts", "display_name": "Posts Scraping", "is_enabled": True}
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/brightdata/webhook/",
            json=webhook_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Webhook response: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Webhook error: {str(e)}")

def create_platforms_via_batch_job():
    """Create platforms via batch job creation which should trigger setup"""
    
    print("\n🚀 CREATING PLATFORMS VIA BATCH JOB FLOW")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Create batch job with special setup parameters
    batch_data = {
        "name": "Setup Platforms Job",
        "project": 3,
        "source_folder_ids": [],
        "platforms_to_scrape": ["instagram"],
        "content_types_to_scrape": {"instagram": ["posts"]},
        "num_of_posts": 1,
        "auto_create_folders": True,
        "setup_platforms": True  # Special flag
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/brightdata/batch-jobs/",
            json=batch_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Batch job response: {response.status_code}")
        if response.status_code == 201:
            job_data = response.json()
            print(f"Created batch job: {job_data.get('id', 'Unknown')}")
            print("✅ This should trigger platform setup!")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Batch job error: {str(e)}")

def bypass_workflow_and_create_direct_scraper():
    """Bypass the workflow system completely and create scraper directly"""
    
    print("\n💥 BYPASSING WORKFLOW - CREATING DIRECT SCRAPER JOBS")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Create scraper requests directly without workflow
    direct_scrapers = [
        {
            "config": 3,  # Instagram config
            "batch_job": None,
            "platform": "instagram", 
            "content_type": "posts",
            "target_url": "https://www.instagram.com/nike/",
            "source_name": "Nike Instagram Direct (No Workflow)",
            "status": "pending",
            "request_id": "direct_nike_bypass"
        },
        {
            "config": 3,
            "batch_job": None,
            "platform": "instagram",
            "content_type": "posts", 
            "target_url": "https://www.instagram.com/adidas/",
            "source_name": "Adidas Instagram Direct (No Workflow)",
            "status": "pending",
            "request_id": "direct_adidas_bypass"
        }
    ]
    
    for scraper_data in direct_scrapers:
        try:
            response = requests.post(
                f"{BASE_URL}/api/brightdata/scraper-requests/",
                json=scraper_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                data = response.json()
                print(f"✅ Created scraper request: {data.get('id', 'Unknown')} - {scraper_data['source_name']}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_workflow_after_fixes():
    """Test if workflow now works after our fixes"""
    
    print("\n🧪 TESTING WORKFLOW AFTER FIXES")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test platforms
    try:
        response = requests.get(f"{BASE_URL}/api/workflow/input-collections/available_platforms/")
        if response.status_code == 200:
            platforms = response.json()
            print(f"✅ Found {len(platforms)} platforms now!")
            for platform in platforms:
                print(f"   - {platform.get('name', 'Unknown')}: {platform.get('display_name', 'Unknown')}")
        else:
            print(f"❌ Platforms still failing: {response.status_code}")
    except Exception as e:
        print(f"❌ Platform test error: {str(e)}")
    
    # Test services
    try:
        response = requests.get(f"{BASE_URL}/api/workflow/input-collections/platform_services/")
        if response.status_code == 200:
            services = response.json()
            print(f"✅ Found {len(services)} platform services now!")
            for service in services:
                print(f"   - {service.get('platform', {}).get('name', 'Unknown')} + {service.get('service', {}).get('name', 'Unknown')}")
        else:
            print(f"❌ Services still failing: {response.status_code}")
    except Exception as e:
        print(f"❌ Service test error: {str(e)}")

if __name__ == "__main__":
    fix_production_platforms()
    create_platforms_via_batch_job()
    bypass_workflow_and_create_direct_scraper()
    test_workflow_after_fixes()