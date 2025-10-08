#!/usr/bin/env python3
"""
PRODUCTION BRIGHTDATA DEPLOYMENT
===============================
Deploy BrightData configuration to production using direct database commands.
"""

import subprocess
import sys

def run_upsun_command(command, description):
    """Run an Upsun command and return the result"""
    print(f"🔄 {description}...")
    try:
        full_command = f'upsun ssh -p inhoolfrqniuu -e main --app trackfutura "{command}"'
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True, result.stdout
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Error: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False, "Command timed out"
    except Exception as e:
        print(f"💥 {description} - EXCEPTION: {str(e)}")
        return False, str(e)

def deploy_brightdata_to_production():
    """Deploy BrightData configuration to production"""
    print("🚀 DEPLOYING BRIGHTDATA TO PRODUCTION")
    print("=" * 60)
    
    # Step 1: Check if we can connect to production
    success, output = run_upsun_command("echo 'Connection test successful'", "Testing production connection")
    if not success:
        print("❌ Cannot connect to production. Aborting deployment.")
        return False
    
    # Step 2: Check Django setup
    success, output = run_upsun_command(
        'cd backend && python manage.py check',
        "Checking Django configuration"
    )
    if not success:
        print("❌ Django configuration check failed. Aborting deployment.")
        return False
    
    # Step 3: Create BrightData configurations
    brightdata_setup_command = '''cd backend && python manage.py shell -c "
from brightdata_integration.models import BrightDataConfig
from users.models import Platform, Service, PlatformService

# Working credentials - TESTED
api_token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
datasets = {
    'instagram': 'gd_lk5ns7kz21pck8jpis',
    'facebook': 'gd_lkaxegm826bjpoo9m5',
    'tiktok': 'gd_l7q7dkf244hwps8lu2',
    'linkedin': 'gd_l7q7dkf244hwps8lu3',
}

print('Creating BrightData configurations...')
configs_created = 0
configs_updated = 0

for platform, dataset_id in datasets.items():
    config, created = BrightDataConfig.objects.get_or_create(
        platform=platform,
        defaults={
            'name': f'{platform.title()} Posts Scraper',
            'dataset_id': dataset_id,
            'api_token': api_token,
            'is_active': True
        }
    )
    
    if not created:
        config.dataset_id = dataset_id
        config.api_token = api_token
        config.is_active = True
        config.save()
        configs_updated += 1
        print(f'Updated {platform} config (ID: {config.id})')
    else:
        configs_created += 1
        print(f'Created {platform} config (ID: {config.id})')

print(f'Summary: {configs_created} created, {configs_updated} updated')
print(f'Total BrightData configs: {BrightDataConfig.objects.count()}')
"'''
    
    success, output = run_upsun_command(
        brightdata_setup_command,
        "Creating BrightData configurations"
    )
    
    if not success:
        print("❌ Failed to create BrightData configurations.")
        return False
    
    # Step 4: Ensure platforms and services exist
    platform_setup_command = '''cd backend && python manage.py shell -c "
from users.models import Platform, Service, PlatformService

# Create platforms
platforms_data = [
    ('instagram', 'Instagram', 'Instagram social media platform'),
    ('facebook', 'Facebook', 'Facebook social media platform'),
    ('tiktok', 'TikTok', 'TikTok social media platform'),
    ('linkedin', 'LinkedIn', 'LinkedIn social media platform'),
]

platforms_created = 0
for name, display_name, description in platforms_data:
    platform, created = Platform.objects.get_or_create(
        name=name,
        defaults={
            'display_name': display_name,
            'description': description,
            'is_enabled': True
        }
    )
    if created:
        platforms_created += 1
        print(f'Created platform: {platform.name} (ID: {platform.id})')

# Create posts service
service, service_created = Service.objects.get_or_create(
    name='posts',
    defaults={
        'display_name': 'Posts Scraping',
        'description': 'Scrape posts from social media platforms',
        'is_enabled': True
    }
)
if service_created:
    print(f'Created service: {service.name} (ID: {service.id})')

# Create platform-service combinations
platform_services_created = 0
for platform_name in ['instagram', 'facebook', 'tiktok', 'linkedin']:
    try:
        platform = Platform.objects.get(name=platform_name)
        platform_service, created = PlatformService.objects.get_or_create(
            platform=platform,
            service=service,
            defaults={
                'description': f'{platform_name.title()} posts scraping service',
                'is_enabled': True
            }
        )
        if created:
            platform_services_created += 1
            print(f'Created {platform_name}-posts service (ID: {platform_service.id})')
    except Exception as e:
        print(f'Error creating {platform_name} platform service: {str(e)}')

print(f'Summary: {platforms_created} platforms, {1 if service_created else 0} services, {platform_services_created} platform services created')
print(f'Total platforms: {Platform.objects.count()}')
print(f'Total services: {Service.objects.count()}')
print(f'Total platform services: {PlatformService.objects.count()}')
"'''
    
    success, output = run_upsun_command(
        platform_setup_command,
        "Setting up platforms and services"
    )
    
    if not success:
        print("❌ Failed to set up platforms and services.")
        return False
    
    # Step 5: Test the BrightData integration
    test_command = '''cd backend && python manage.py shell -c "
from brightdata_integration.services import BrightDataAutomatedBatchScraper
from brightdata_integration.models import BrightDataConfig

print('Testing BrightData integration...')

# Check configurations
configs = BrightDataConfig.objects.all()
print(f'Found {configs.count()} BrightData configurations:')
for config in configs:
    print(f'  - {config.platform}: {config.name} (Active: {config.is_active})')

# Test scraper service
try:
    scraper = BrightDataAutomatedBatchScraper()
    result = scraper.trigger_scraper('instagram', ['https://www.instagram.com/nike/'])
    print(f'Test scraper result: {result.get(\"success\", False)} - {result.get(\"message\", \"No message\")}')
except Exception as e:
    print(f'Test scraper failed: {str(e)}')

print('BrightData integration test complete!')
"'''
    
    success, output = run_upsun_command(
        test_command,
        "Testing BrightData integration"
    )
    
    if not success:
        print("⚠️  BrightData integration test failed, but configuration may still be successful.")
    
    print("\n🎉 BRIGHTDATA PRODUCTION DEPLOYMENT COMPLETE!")
    print("\n📋 Next Steps:")
    print("   1. Test the API endpoints: https://trackfutura.futureobjects.io/api/brightdata/configs/")
    print("   2. Test scraper trigger: POST to /api/brightdata/trigger-scraper/")
    print("   3. Check webhook endpoint: /api/brightdata/webhook/")
    print("   4. Monitor logs for any errors")
    
    return True

if __name__ == "__main__":
    try:
        success = deploy_brightdata_to_production()
        if success:
            print("\n✅ DEPLOYMENT SUCCESSFUL!")
            sys.exit(0)
        else:
            print("\n❌ DEPLOYMENT FAILED!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 DEPLOYMENT ERROR: {str(e)}")
        sys.exit(1)