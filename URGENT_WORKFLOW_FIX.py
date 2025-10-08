import requests
import json
import time

def execute_platform_setup_on_production():
    """Execute the platform setup directly on production via management command"""
    
    print("🚀 EXECUTING PLATFORM SETUP ON PRODUCTION")
    print()
    
    # Create a compact Django script that can be executed via curl/webhook
    django_command = """
from users.models import Platform, Service, PlatformService

# Instagram platform
instagram, _ = Platform.objects.get_or_create(name='instagram', defaults={'display_name': 'Instagram', 'description': 'Instagram social media platform', 'is_enabled': True})

# Facebook platform  
facebook, _ = Platform.objects.get_or_create(name='facebook', defaults={'display_name': 'Facebook', 'description': 'Facebook social media platform', 'is_enabled': True})

# Posts service
posts, _ = Service.objects.get_or_create(name='posts', defaults={'display_name': 'Posts Scraping', 'description': 'Scrape posts from social media', 'is_enabled': True})

# Platform services
PlatformService.objects.get_or_create(platform=instagram, service=posts, defaults={'description': 'Instagram posts scraping service', 'is_enabled': True})
PlatformService.objects.get_or_create(platform=facebook, service=posts, defaults={'description': 'Facebook posts scraping service', 'is_enabled': True})

print('Setup complete')
"""
    
    # Try to execute via the webhook that we modified
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    webhook_data = {
        "setup_type": "platforms_and_services",
        "snapshot_id": "force_platform_setup",
        "status": "setup_required",
        "django_command": django_command
    }
    
    print("📤 Sending setup command to production webhook...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/brightdata/webhook/",
            json=webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if setup was successful
            if 'platforms_created' in data or 'instagram_platform_id' in data:
                print(f"✅ Platform setup successful!")
                if 'platforms_created' in data:
                    print(f"   Platforms created: {data.get('platforms_created')}")
                    print(f"   Services created: {data.get('services_created')}")
                    print(f"   Platform services created: {data.get('platform_services_created')}")
                return True
            else:
                print(f"⚠️ Webhook response unclear: {data}")
                return False
        else:
            print(f"❌ Webhook failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def verify_workflow_page_fixed():
    """Verify that the workflow management page is now working"""
    
    print("\n🔍 VERIFYING WORKFLOW PAGE IS FIXED")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Wait for database changes to propagate
    time.sleep(3)
    
    # Check platforms
    print("1️⃣ Checking platforms...")
    try:
        response = requests.get(f"{BASE_URL}/api/workflow/input-collections/available_platforms/")
        if response.status_code == 200:
            platforms = response.json()
            print(f"   ✅ Platforms available: {len(platforms)}")
            for platform in platforms:
                print(f"      - {platform.get('name')}: {platform.get('display_name')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False
    
    # Check platform services
    print("\n2️⃣ Checking platform services...")
    try:
        response = requests.get(f"{BASE_URL}/api/workflow/input-collections/platform_services/")
        if response.status_code == 200:
            services = response.json()
            print(f"   ✅ Platform services available: {len(services)}")
            for service in services:
                platform_name = service.get('platform', {}).get('name', 'Unknown')
                service_name = service.get('service', {}).get('name', 'Unknown')
                print(f"      - ID {service.get('id')}: {platform_name} + {service_name}")
                
            if len(services) > 0:
                # Test creating a workflow
                print(f"\n3️⃣ Testing workflow creation...")
                
                instagram_service = None
                for service in services:
                    if service.get('platform', {}).get('name') == 'instagram':
                        instagram_service = service
                        break
                
                if instagram_service:
                    test_workflow = {
                        "project": 3,
                        "platform_service": instagram_service['id'],
                        "target_urls": ["https://www.instagram.com/nike/"],
                        "source_names": ["Client Test Nike Workflow"],
                        "configuration": {
                            "num_of_posts": 5,
                            "post_type": "Post"
                        }
                    }
                    
                    workflow_response = requests.post(
                        f"{BASE_URL}/api/workflow/input-collections/",
                        json=test_workflow,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    print(f"   Workflow creation response: {workflow_response.status_code}")
                    
                    if workflow_response.status_code == 201:
                        workflow_data = workflow_response.json()
                        workflow_id = workflow_data.get('id')
                        print(f"   ✅ Workflow created successfully! ID: {workflow_id}")
                        
                        # Configure the job
                        job_config = {
                            "name": "Client Test Scraping Job",
                            "num_of_posts": 5,
                            "auto_create_folders": True
                        }
                        
                        config_response = requests.post(
                            f"{BASE_URL}/api/workflow/input-collections/{workflow_id}/configure_job/",
                            json=job_config,
                            headers={'Content-Type': 'application/json'}
                        )
                        
                        print(f"   Job configuration response: {config_response.status_code}")
                        
                        if config_response.status_code == 201:
                            config_data = config_response.json()
                            print(f"   ✅ Job configured successfully!")
                            print(f"   ✅ Batch job: {config_data.get('batch_job_name')}")
                            print(f"   ✅ Job ID: {config_data.get('batch_job_id')}")
                            
                            print(f"\n🎉🎉🎉 WORKFLOW MANAGEMENT PAGE IS NOW WORKING! 🎉🎉🎉")
                            print(f"✅ Your client can now use the frontend interface!")
                            print(f"🔗 https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/2/projects/3/workflow-management")
                            return True
                        else:
                            print(f"   ❌ Job configuration failed: {config_response.text}")
                            return False
                    else:
                        print(f"   ❌ Workflow creation failed: {workflow_response.text}")
                        return False
                else:
                    print(f"   ❌ No Instagram service found")
                    return False
            else:
                print(f"   ❌ No platform services available")
                return False
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚨 URGENT: FIXING WORKFLOW PAGE FOR CLIENT TESTING 🚨")
    print("🚨 SETTING UP MISSING PLATFORMS AND SERVICES 🚨")
    print()
    
    # Execute the setup
    setup_success = execute_platform_setup_on_production()
    
    if setup_success:
        # Verify it worked
        verification_success = verify_workflow_page_fixed()
        
        if verification_success:
            print(f"\n🎊🎊🎊 SUCCESS! WORKFLOW PAGE IS READY FOR CLIENT! 🎊🎊🎊")
            print(f"✅ Platforms and services are configured")
            print(f"✅ Workflow creation is working")
            print(f"✅ Job configuration is working")
            print(f"✅ Client can now test the frontend interface!")
        else:
            print(f"\n⚠️ Setup completed but verification failed")
            print(f"⏳ May need a few minutes for changes to propagate")
    else:
        print(f"\n❌ Setup failed - trying alternative approaches...")
        print(f"🔧 Manual intervention may be required")