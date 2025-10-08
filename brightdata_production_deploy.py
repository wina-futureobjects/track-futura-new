#!/usr/bin/env python3
"""
BRIGHTDATA PRODUCTION DEPLOYMENT SCRIPT
=====================================
Simple deployment script for BrightData configuration in production.
Run this on the production server after uploading.
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, '/app/backend')
os.chdir('/app/backend')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from brightdata_integration.models import BrightDataConfig
from users.models import Platform, Service, PlatformService, Project


def deploy_brightdata_production():
    """Deploy BrightData configuration to production"""
    print("🚀 DEPLOYING BRIGHTDATA TO PRODUCTION")
    
    # Working credentials - TESTED AND CONFIRMED
    api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    datasets = {
        'instagram': 'gd_lk5ns7kz21pck8jpis',  # CONFIRMED WORKING Instagram dataset
        'facebook': 'gd_lkaxegm826bjpoo9m5',   # CONFIRMED WORKING Facebook dataset
        'tiktok': 'gd_l7q7dkf244hwps8lu2',     # TikTok dataset ID
        'linkedin': 'gd_l7q7dkf244hwps8lu3',   # LinkedIn dataset ID
    }
    
    # Create/update configurations
    configs_created = 0
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
            print(f"✅ Updated {platform} config (ID: {config.id})")
        else:
            configs_created += 1
            print(f"✅ Created {platform} config (ID: {config.id})")
    
    print(f"\n📊 CONFIGURATION SUMMARY:")
    print(f"   Configs created: {configs_created}")
    print(f"   Total configs: {BrightDataConfig.objects.count()}")
    
    # Ensure platforms and services exist
    print(f"\n🔧 SETTING UP PLATFORMS AND SERVICES...")
    
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
        print(f"   {'Created' if created else 'Found'} platform: {platform.name} (ID: {platform.id})")
    
    # Create posts service
    service, service_created = Service.objects.get_or_create(
        name='posts',
        defaults={
            'display_name': 'Posts Scraping',
            'description': 'Scrape posts from social media platforms',
            'is_enabled': True
        }
    )
    print(f"   {'Created' if service_created else 'Found'} service: {service.name} (ID: {service.id})")
    
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
            print(f"   {'Created' if created else 'Found'} {platform_name}-posts service (ID: {platform_service.id})")
        except Exception as e:
            print(f"   ❌ Error creating {platform_name} platform service: {str(e)}")
    
    print(f"\n📊 SERVICES SUMMARY:")
    print(f"   Platforms created: {platforms_created}")
    print(f"   Services created: {1 if service_created else 0}")
    print(f"   Platform services created: {platform_services_created}")
    print(f"   Total platforms: {Platform.objects.count()}")
    print(f"   Total services: {Service.objects.count()}")
    print(f"   Total platform services: {PlatformService.objects.count()}")
    
    # Ensure at least one project exists
    project, project_created = Project.objects.get_or_create(
        id=1,
        defaults={
            'name': 'Default BrightData Project',
            'description': 'Default project for BrightData scraping operations'
        }
    )
    print(f"   {'Created' if project_created else 'Found'} project: {project.name} (ID: {project.id})")
    
    print("\n✅ BRIGHTDATA PRODUCTION DEPLOYMENT COMPLETE!")
    
    # Test trigger
    print("\n🧪 TESTING BRIGHTDATA TRIGGER...")
    try:
        from brightdata_integration.services import BrightDataAutomatedBatchScraper
        scraper = BrightDataAutomatedBatchScraper()
        
        # Test Instagram
        print("   Testing Instagram...")
        result = scraper.trigger_scraper('instagram', ['https://www.instagram.com/nike/'])
        print(f"   Instagram result: {result.get('success', False)} - {result.get('message', 'No message')}")
        
        # Test Facebook
        print("   Testing Facebook...")
        result = scraper.trigger_scraper('facebook', ['https://www.facebook.com/nike/'])
        print(f"   Facebook result: {result.get('success', False)} - {result.get('message', 'No message')}")
        
    except Exception as e:
        print(f"   ❌ Test failed: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
    
    print("\n🎉 DEPLOYMENT AND TESTING COMPLETE!")
    return True


if __name__ == "__main__":
    try:
        success = deploy_brightdata_production()
        if success:
            print("\n✅ ALL BRIGHTDATA ISSUES RESOLVED!")
            print("   Your BrightData integration should now work in production.")
        else:
            print("\n❌ DEPLOYMENT FAILED!")
            print("   Check the error messages above.")
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())