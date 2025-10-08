import requests
import json
import time

def direct_platform_setup_test():
    """Test the platform setup functionality directly"""
    
    print("🔧 TESTING PLATFORM SETUP FUNCTIONALITY")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test the platform setup via webhook
    setup_data = {
        "setup_type": "platforms_and_services",
        "snapshot_id": "database_setup_trigger",
        "status": "setup_required"
    }
    
    print("📤 Sending platform setup request via webhook...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/brightdata/webhook/",
            json=setup_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Webhook response: {response.status_code}")
        print(f"Webhook response text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and 'platforms_created' in data:
                print(f"✅ Platform setup succeeded!")
                print(f"   Platforms created: {data.get('platforms_created', 0)}")
                print(f"   Services created: {data.get('services_created', 0)}")
                print(f"   Platform services created: {data.get('platform_services_created', 0)}")
                print(f"   Instagram platform ID: {data.get('instagram_platform_id')}")
                print(f"   Facebook platform ID: {data.get('facebook_platform_id')}")
                print(f"   Instagram-Posts service ID: {data.get('instagram_posts_id')}")
                print(f"   Facebook-Posts service ID: {data.get('facebook_posts_id')}")
                
                # Wait a moment for database to sync
                print("\n⏳ Waiting for database sync...")
                time.sleep(5)
                
                # Test platforms now
                print("\n🧪 Testing platforms after setup...")
                platforms_response = requests.get(f"{BASE_URL}/api/workflow/input-collections/available_platforms/")
                services_response = requests.get(f"{BASE_URL}/api/workflow/input-collections/platform_services/")
                
                if platforms_response.status_code == 200:
                    platforms = platforms_response.json()
                    print(f"   ✅ Platforms available: {len(platforms)}")
                    for platform in platforms:
                        print(f"      - {platform.get('name', 'Unknown')}: {platform.get('display_name', 'Unknown')}")
                
                if services_response.status_code == 200:
                    services = services_response.json()
                    print(f"   ✅ Platform services available: {len(services)}")
                    for service in services:
                        platform_name = service.get('platform', {}).get('name', 'Unknown')
                        service_name = service.get('service', {}).get('name', 'Unknown')
                        print(f"      - Service ID {service.get('id')}: {platform_name} + {service_name}")
                
                if len(platforms) > 0 and len(services) > 0:
                    print(f"\n🎉🎉🎉 FRONTEND WORKFLOW IS NOW READY! 🎉🎉🎉")
                    return True
                else:
                    print(f"\n⚠️ Platforms created but not appearing in workflow API yet")
                    return False
            else:
                print(f"⚠️ Setup response doesn't indicate success: {data}")
                return False
        else:
            print(f"❌ Setup failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Setup error: {str(e)}")
        return False

def test_frontend_workflow_creation():
    """Test creating a workflow item through the frontend API"""
    
    print("\n🚀 TESTING FRONTEND WORKFLOW CREATION")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Get available platform services
    services_response = requests.get(f"{BASE_URL}/api/workflow/input-collections/platform_services/")
    
    if services_response.status_code == 200:
        services = services_response.json()
        if len(services) > 0:
            # Use the first Instagram service
            instagram_service = None
            for service in services:
                if service.get('platform', {}).get('name') == 'instagram':
                    instagram_service = service
                    break
            
            if instagram_service:
                print(f"📱 Using Instagram service ID: {instagram_service['id']}")
                
                # Create input collection
                collection_data = {
                    "project": 3,
                    "platform_service": instagram_service['id'],
                    "target_urls": ["https://www.instagram.com/nike/"],
                    "source_names": ["Nike Instagram Frontend Test"],
                    "configuration": {
                        "num_of_posts": 5,
                        "post_type": "Post"
                    }
                }
                
                print("📝 Creating input collection via frontend API...")
                
                collection_response = requests.post(
                    f"{BASE_URL}/api/workflow/input-collections/",
                    json=collection_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"Collection response: {collection_response.status_code}")
                
                if collection_response.status_code == 201:
                    collection = collection_response.json()
                    collection_id = collection['id']
                    print(f"✅ Created input collection ID: {collection_id}")
                    
                    # Configure the job
                    job_config = {
                        "name": "Frontend Test Nike Scrape",
                        "num_of_posts": 5,
                        "auto_create_folders": True
                    }
                    
                    job_response = requests.post(
                        f"{BASE_URL}/api/workflow/input-collections/{collection_id}/configure_job/",
                        json=job_config,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    print(f"Job config response: {job_response.status_code}")
                    
                    if job_response.status_code == 201:
                        job_data = job_response.json()
                        print(f"✅ Configured job: {job_data.get('batch_job_name', 'Unknown')}")
                        print(f"✅ Batch Job ID: {job_data.get('batch_job_id', 'Unknown')}")
                        
                        print(f"\n🎊🎊🎊 FRONTEND WORKFLOW IS WORKING! 🎊🎊🎊")
                        return True
                    else:
                        print(f"❌ Job config failed: {job_response.text}")
                        return False
                else:
                    print(f"❌ Collection creation failed: {collection_response.text}")
                    return False
            else:
                print(f"❌ No Instagram service found in available services")
                return False
        else:
            print(f"❌ No platform services available")
            return False
    else:
        print(f"❌ Failed to get platform services: {services_response.status_code}")
        return False

if __name__ == "__main__":
    print("🚨 FINAL FRONTEND WORKFLOW FIX 🚨")
    print("🚨 SETTING UP PLATFORMS AND TESTING WORKFLOW 🚨")
    print()
    
    # Setup platforms first
    setup_success = direct_platform_setup_test()
    
    if setup_success:
        # Test the workflow
        workflow_success = test_frontend_workflow_creation()
        
        if workflow_success:
            print(f"\n🎉🎉🎉 FRONTEND ISSUE COMPLETELY SOLVED! 🎉🎉🎉")
            print(f"✅ Your workflow interface is now fully functional!")
            print(f"✅ You can create scraping jobs from the frontend!")
            print(f"🔗 https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/2/projects/3/workflow-management")
        else:
            print(f"\n⚠️ Platforms setup but workflow creation still has issues")
    else:
        print(f"\n❌ Platform setup failed - deployment may still be in progress")
        print(f"⏳ Try running this script again in a few minutes")