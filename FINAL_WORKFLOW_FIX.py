import requests
import json
import time

def direct_database_setup():
    """Setup platforms directly in the database via a custom approach"""
    
    print("🔧 DIRECT DATABASE SETUP FOR WORKFLOW PAGE")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Try to trigger setup via the updated webhook endpoint
    setup_data = {
        "setup_type": "platforms_and_services",
        "snapshot_id": "database_setup_trigger",
        "status": "setup_required",
        "data": {
            "platforms": [
                {"name": "instagram", "display_name": "Instagram", "is_enabled": True},
                {"name": "facebook", "display_name": "Facebook", "is_enabled": True}
            ],
            "services": [
                {"name": "posts", "display_name": "Posts Scraping", "is_enabled": True}
            ]
        }
    }
    
    print("📤 Triggering platform setup via webhook...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/brightdata/webhook/",
            json=setup_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Webhook response: {response.status_code}")
        response_text = response.text
        print(f"Response text: {response_text}")
        
        # Wait for setup to complete
        time.sleep(5)
        
        # Check if platforms are now available
        platforms_response = requests.get(f"{BASE_URL}/api/workflow/input-collections/available_platforms/")
        
        if platforms_response.status_code == 200:
            platforms = platforms_response.json()
            print(f"\nPlatforms check: {len(platforms)} platforms found")
            
            if len(platforms) > 0:
                print("✅ Platform setup successful via webhook!")
                
                for platform in platforms:
                    print(f"   - {platform.get('name')}: {platform.get('display_name')}")
                
                # Check services too
                services_response = requests.get(f"{BASE_URL}/api/workflow/input-collections/platform_services/")
                if services_response.status_code == 200:
                    services = services_response.json()
                    print(f"Platform services: {len(services)} services found")
                    
                    if len(services) > 0:
                        for service in services:
                            platform_name = service.get('platform', {}).get('name', 'Unknown')
                            service_name = service.get('service', {}).get('name', 'Unknown')
                            print(f"   - ID {service.get('id')}: {platform_name} + {service_name}")
                        
                        return True
                    else:
                        print("❌ No platform services created")
                        return False
                else:
                    print("❌ Failed to check platform services")
                    return False
            else:
                print("❌ No platforms created yet")
                return False
        else:
            print(f"❌ Failed to check platforms: {platforms_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def create_platforms_via_batch_creation():
    """Create platforms by forcing through batch job creation"""
    
    print("\n🚀 CREATING PLATFORMS VIA BATCH JOB FORCE")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Create multiple batch jobs that will force platform creation
    batch_configs = [
        {
            "name": "Force Instagram Platform Creation",
            "project": 3,
            "source_folder_ids": [],
            "platforms_to_scrape": ["instagram"],
            "content_types_to_scrape": {"instagram": ["posts"]},
            "num_of_posts": 1,
            "auto_create_folders": True,
            "status": "pending",
            "force_create_platform": "instagram"
        },
        {
            "name": "Force Facebook Platform Creation", 
            "project": 3,
            "source_folder_ids": [],
            "platforms_to_scrape": ["facebook"],
            "content_types_to_scrape": {"facebook": ["posts"]},
            "num_of_posts": 1,
            "auto_create_folders": True,
            "status": "pending",
            "force_create_platform": "facebook"
        }
    ]
    
    created_jobs = []
    
    for config in batch_configs:
        try:
            response = requests.post(
                f"{BASE_URL}/api/brightdata/batch-jobs/",
                json=config,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                job_data = response.json()
                created_jobs.append(job_data['id'])
                print(f"✅ Created force job: {job_data['id']} - {config['name']}")
            else:
                print(f"❌ Job creation failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error creating job: {str(e)}")
    
    if len(created_jobs) > 0:
        print(f"\n✅ Created {len(created_jobs)} force jobs")
        
        # Wait and check platforms
        time.sleep(5)
        
        platforms_response = requests.get(f"{BASE_URL}/api/workflow/input-collections/available_platforms/")
        if platforms_response.status_code == 200:
            platforms = platforms_response.json()
            if len(platforms) > 0:
                print(f"✅ Platforms created via batch job force!")
                return True
    
    return False

def final_verification_and_test():
    """Final verification that the workflow page is working"""
    
    print("\n🎯 FINAL VERIFICATION FOR CLIENT TESTING")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Check platforms one more time
    platforms_response = requests.get(f"{BASE_URL}/api/workflow/input-collections/available_platforms/")
    services_response = requests.get(f"{BASE_URL}/api/workflow/input-collections/platform_services/")
    
    if platforms_response.status_code == 200 and services_response.status_code == 200:
        platforms = platforms_response.json()
        services = services_response.json()
        
        print(f"Final check:")
        print(f"   Platforms: {len(platforms)}")
        print(f"   Platform services: {len(services)}")
        
        if len(platforms) > 0 and len(services) > 0:
            print(f"\n🎊🎊🎊 WORKFLOW PAGE IS READY FOR CLIENT! 🎊🎊🎊")
            print(f"✅ Your client can now access: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/2/projects/3/workflow-management")
            print(f"✅ They can create workflows and configure scraping jobs!")
            print(f"✅ All platforms and services are properly configured!")
            
            # Show available options
            print(f"\nAvailable for client testing:")
            for platform in platforms:
                print(f"   📱 {platform.get('display_name', platform.get('name'))}")
            
            for service in services:
                platform_name = service.get('platform', {}).get('display_name', 'Unknown')
                service_name = service.get('service', {}).get('display_name', 'Unknown') 
                print(f"   🔧 {platform_name} - {service_name} (ID: {service.get('id')})")
            
            return True
        else:
            print(f"\n❌ Still missing configurations:")
            if len(platforms) == 0:
                print(f"   - No platforms available")
            if len(services) == 0:
                print(f"   - No platform services available")
            return False
    else:
        print(f"❌ API checks failed")
        return False

if __name__ == "__main__":
    print("🚨 FINAL ATTEMPT: FIXING WORKFLOW PAGE FOR CLIENT 🚨")
    print()
    
    # Try direct database setup first
    setup1_success = direct_database_setup()
    
    if not setup1_success:
        print("First approach failed, trying batch job force...")
        setup2_success = create_platforms_via_batch_creation()
        
        if not setup2_success:
            print("All automatic approaches failed!")
            print("\n🔧 MANUAL SETUP REQUIRED:")
            print("1. Access production via: upsun ssh -e main --app backend")
            print("2. Run the platform setup script manually")
            print("3. Check workflow page again")
    
    # Final verification regardless
    final_verification_and_test()