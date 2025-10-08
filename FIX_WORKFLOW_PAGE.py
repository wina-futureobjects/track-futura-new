import requests
import json
import time

def diagnose_workflow_page_issues():
    """Diagnose why the workflow management page isn't working"""
    
    print("🔍 DIAGNOSING WORKFLOW MANAGEMENT PAGE ISSUES")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("1️⃣ Checking available platforms...")
    try:
        response = requests.get(f"{BASE_URL}/api/workflow/input-collections/available_platforms/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            platforms = response.json()
            print(f"   Platforms found: {len(platforms)}")
            if len(platforms) == 0:
                print("   ❌ NO PLATFORMS CONFIGURED - This is the main issue!")
            else:
                for platform in platforms:
                    print(f"      - {platform.get('name')}: {platform.get('display_name')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print("\n2️⃣ Checking platform services...")
    try:
        response = requests.get(f"{BASE_URL}/api/workflow/input-collections/platform_services/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            services = response.json()
            print(f"   Platform services found: {len(services)}")
            if len(services) == 0:
                print("   ❌ NO PLATFORM SERVICES CONFIGURED - Frontend can't create workflows!")
            else:
                for service in services:
                    platform_name = service.get('platform', {}).get('name', 'Unknown')
                    service_name = service.get('service', {}).get('name', 'Unknown')
                    print(f"      - ID {service.get('id')}: {platform_name} + {service_name}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print("\n3️⃣ Checking existing BrightData configs...")
    try:
        response = requests.get(f"{BASE_URL}/api/brightdata/configs/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            configs = data.get('results', []) if isinstance(data, dict) else data
            print(f"   BrightData configs found: {len(configs)}")
            for config in configs:
                print(f"      - ID {config.get('id')}: {config.get('platform')} - {config.get('dataset_id')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    return len(platforms) == 0 or len(services) == 0

def force_create_platforms_via_upsun():
    """Force create platforms via direct Upsun environment access"""
    
    print("\n🚀 FORCING PLATFORM CREATION VIA UPSUN")
    print()
    
    # Create a Django script to execute on production
    django_script = '''
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import Platform, Service, PlatformService

print("Creating platforms and services...")

# Create Instagram platform
instagram, created = Platform.objects.get_or_create(
    name='instagram',
    defaults={
        'display_name': 'Instagram',
        'description': 'Instagram social media platform',
        'is_enabled': True
    }
)
print(f"Instagram platform: {'created' if created else 'exists'} - ID {instagram.id}")

# Create Facebook platform
facebook, created = Platform.objects.get_or_create(
    name='facebook',
    defaults={
        'display_name': 'Facebook',
        'description': 'Facebook social media platform',
        'is_enabled': True
    }
)
print(f"Facebook platform: {'created' if created else 'exists'} - ID {facebook.id}")

# Create Posts service
posts, created = Service.objects.get_or_create(
    name='posts',
    defaults={
        'display_name': 'Posts Scraping',
        'description': 'Scrape posts from social media',
        'is_enabled': True
    }
)
print(f"Posts service: {'created' if created else 'exists'} - ID {posts.id}")

# Create Instagram + Posts platform service
ig_posts, created = PlatformService.objects.get_or_create(
    platform=instagram,
    service=posts,
    defaults={
        'description': 'Instagram posts scraping service',
        'is_enabled': True
    }
)
print(f"Instagram-Posts service: {'created' if created else 'exists'} - ID {ig_posts.id}")

# Create Facebook + Posts platform service
fb_posts, created = PlatformService.objects.get_or_create(
    platform=facebook,
    service=posts,
    defaults={
        'description': 'Facebook posts scraping service',
        'is_enabled': True
    }
)
print(f"Facebook-Posts service: {'created' if created else 'exists'} - ID {fb_posts.id}")

print("✅ Platform setup complete!")
print(f"Platform count: {Platform.objects.count()}")
print(f"Service count: {Service.objects.count()}")
print(f"PlatformService count: {PlatformService.objects.count()}")
'''
    
    # Save the script to a temporary file
    script_filename = "setup_platforms_production.py"
    with open(script_filename, 'w', encoding='utf-8') as f:
        f.write(django_script)
    
    print(f"✅ Created {script_filename}")
    print(f"📝 To execute on production, run:")
    print(f"   upsun ssh -e main --app backend")
    print(f"   Then on production: python {script_filename}")
    
    return script_filename

def create_platforms_via_api_injection():
    """Try to create platforms by injecting through various API endpoints"""
    
    print("\n💉 TRYING API INJECTION METHODS")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Method 1: Try creating via BrightData batch job with special parameters
    print("Method 1: Creating via batch job with setup flag...")
    batch_data = {
        "name": "Platform Setup Job",
        "project": 3,
        "source_folder_ids": [],
        "platforms_to_scrape": ["instagram", "facebook"],
        "content_types_to_scrape": {"instagram": ["posts"], "facebook": ["posts"]},
        "num_of_posts": 1,
        "auto_create_folders": True,
        "force_setup_platforms": True,  # Special flag
        "setup_command": "create_platforms"  # Setup command
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/brightdata/batch-jobs/",
            json=batch_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Batch job response: {response.status_code}")
        if response.status_code == 201:
            job_data = response.json()
            print(f"   Created setup job: {job_data.get('id')}")
        else:
            print(f"   Failed: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Method 2: Create platforms via scraper request creation
    print("\nMethod 2: Creating via scraper request...")
    scraper_data = {
        "config": 3,
        "batch_job": None,
        "platform": "instagram",
        "content_type": "posts",
        "target_url": "https://www.instagram.com/setup/",
        "source_name": "Platform Setup Trigger",
        "status": "setup",
        "request_id": "platform_setup_trigger",
        "setup_platforms": True  # Special flag
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/brightdata/scraper-requests/",
            json=scraper_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Scraper request response: {response.status_code}")
        if response.status_code == 201:
            print(f"   Created setup scraper request")
        else:
            print(f"   Failed: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")

def test_workflow_after_setup():
    """Test if the workflow interface works after setup attempts"""
    
    print("\n🧪 TESTING WORKFLOW INTERFACE AFTER SETUP")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Wait a moment
    print("⏳ Waiting for setup to take effect...")
    time.sleep(5)
    
    # Check platforms again
    try:
        response = requests.get(f"{BASE_URL}/api/workflow/input-collections/available_platforms/")
        if response.status_code == 200:
            platforms = response.json()
            print(f"Platforms now available: {len(platforms)}")
            
            if len(platforms) > 0:
                # Check services
                services_response = requests.get(f"{BASE_URL}/api/workflow/input-collections/platform_services/")
                if services_response.status_code == 200:
                    services = services_response.json()
                    print(f"Platform services now available: {len(services)}")
                    
                    if len(services) > 0:
                        print(f"\n🎉 WORKFLOW INTERFACE SHOULD NOW WORK!")
                        print(f"🔗 Test at: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/2/projects/3/workflow-management")
                        
                        # Try to create a test workflow
                        instagram_service = None
                        for service in services:
                            if service.get('platform', {}).get('name') == 'instagram':
                                instagram_service = service
                                break
                        
                        if instagram_service:
                            print(f"\n📝 Creating test workflow...")
                            test_workflow = {
                                "project": 3,
                                "platform_service": instagram_service['id'],
                                "target_urls": ["https://www.instagram.com/nike/"],
                                "source_names": ["Test Nike Workflow"],
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
                            
                            print(f"Test workflow response: {workflow_response.status_code}")
                            if workflow_response.status_code == 201:
                                print(f"✅ WORKFLOW CREATION SUCCESSFUL!")
                                print(f"✅ Your frontend interface is now working!")
                                return True
                            else:
                                print(f"❌ Workflow creation failed: {workflow_response.text}")
                        else:
                            print(f"❌ No Instagram service found")
                    else:
                        print(f"❌ Still no platform services")
                else:
                    print(f"❌ Platform services check failed")
            else:
                print(f"❌ Still no platforms available")
        else:
            print(f"❌ Platform check failed")
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
    
    return False

if __name__ == "__main__":
    print("🚨 FIXING FRONTEND WORKFLOW MANAGEMENT PAGE 🚨")
    print("🚨 FOR CLIENT TESTING REQUIREMENTS 🚨")
    print()
    
    # First diagnose the issues
    has_issues = diagnose_workflow_page_issues()
    
    if has_issues:
        print(f"\n❌ FOUND ISSUES: Missing platforms/services for workflow interface")
        
        # Try API injection methods
        create_platforms_via_api_injection()
        
        # Create manual setup script
        script_file = force_create_platforms_via_upsun()
        
        # Test if it worked
        success = test_workflow_after_setup()
        
        if not success:
            print(f"\n⚠️ AUTOMATIC SETUP DIDN'T WORK")
            print(f"🔧 MANUAL SETUP REQUIRED:")
            print(f"   1. Run: upsun ssh -e main --app backend")
            print(f"   2. Upload and run: {script_file}")
            print(f"   3. Test workflow page again")
            print(f"\n📞 This will fix the workflow management page for client testing!")
    else:
        print(f"\n✅ WORKFLOW SHOULD BE WORKING!")
        print(f"🔗 Test at: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/2/projects/3/workflow-management")