#!/usr/bin/env python
"""
Restore BrightData configuration with proper platforms, services, and configs
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import Platform, Service, PlatformService
from brightdata_integration.models import BrightDataConfig

def restore_brightdata_setup():
    print("=== Restoring Complete BrightData Setup ===")
    
    # 1. Create Platforms
    platforms_data = [
        {'name': 'instagram', 'description': 'Instagram social media platform'},
        {'name': 'facebook', 'description': 'Facebook social media platform'},
        {'name': 'tiktok', 'description': 'TikTok social media platform'},
        {'name': 'linkedin', 'description': 'LinkedIn professional network'},
    ]
    
    for platform_data in platforms_data:
        platform, created = Platform.objects.get_or_create(
            name=platform_data['name'],
            defaults={
                'description': platform_data['description'],
                'is_active': True
            }
        )
        if created:
            print(f"✅ Created Platform: {platform.name}")
        else:
            print(f"✅ Platform exists: {platform.name}")
    
    # 2. Create Services
    services_data = [
        {'name': 'posts', 'description': 'Post scraping service'},
        {'name': 'profiles', 'description': 'Profile scraping service'},
        {'name': 'hashtags', 'description': 'Hashtag scraping service'},
    ]
    
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            name=service_data['name'],
            defaults={
                'description': service_data['description'],
                'is_active': True
            }
        )
        if created:
            print(f"✅ Created Service: {service.name}")
        else:
            print(f"✅ Service exists: {service.name}")
    
    # 3. Create Platform Services (combinations)
    platform_service_combinations = [
        ('instagram', 'posts'),
        ('facebook', 'posts'),
        ('tiktok', 'posts'),
        ('linkedin', 'posts'),
    ]
    
    for platform_name, service_name in platform_service_combinations:
        try:
            platform = Platform.objects.get(name=platform_name)
            service = Service.objects.get(name=service_name)
            
            platform_service, created = PlatformService.objects.get_or_create(
                platform=platform,
                service=service,
                defaults={
                    'is_enabled': True,
                    'configuration': {}
                }
            )
            
            if created:
                print(f"✅ Created PlatformService: {platform_name} + {service_name}")
            else:
                print(f"✅ PlatformService exists: {platform_name} + {service_name}")
                
        except Exception as e:
            print(f"❌ Error creating PlatformService {platform_name}+{service_name}: {e}")
    
    # 4. Create BrightData Configurations
    brightdata_configs = [
        {
            'platform': 'instagram',
            'dataset_id': 'hl_f7614f18',  # Your actual scraper ID
            'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb'  # Your real token
        },
        {
            'platform': 'facebook',
            'dataset_id': 'hl_f7614f18',  # Same scraper for now
            'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb'
        }
    ]
    
    for config_data in brightdata_configs:
        config, created = BrightDataConfig.objects.get_or_create(
            platform=config_data['platform'],
            defaults={
                'dataset_id': config_data['dataset_id'],
                'api_token': config_data['api_token'],
                'is_active': True
            }
        )
        
        if not created:
            # Update existing config
            config.dataset_id = config_data['dataset_id']
            config.api_token = config_data['api_token']
            config.is_active = True
            config.save()
        
        print(f"✅ BrightData Config: {config.platform} -> {config.dataset_id}")
    
    # 5. Summary
    print("\n=== Setup Summary ===")
    print(f"Platforms: {Platform.objects.count()}")
    print(f"Services: {Service.objects.count()}")
    print(f"Platform Services: {PlatformService.objects.count()}")
    print(f"BrightData Configs: {BrightDataConfig.objects.count()}")
    
    return True

if __name__ == '__main__':
    print("🚀 Restoring complete BrightData setup...")
    success = restore_brightdata_setup()
    if success:
        print("✅ BrightData setup restoration complete!")
    else:
        print("❌ BrightData setup restoration failed!")
        sys.exit(1)