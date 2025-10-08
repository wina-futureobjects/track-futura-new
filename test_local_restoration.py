#!/usr/bin/env python
"""
Test local API to see BrightData restoration results
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

def test_local_data():
    print("=== Local Database Status ===")
    
    print(f"Platforms: {Platform.objects.count()}")
    for platform in Platform.objects.all():
        print(f"  - {platform.name}: {platform.display_name} (enabled: {platform.is_enabled})")
    
    print(f"\nServices: {Service.objects.count()}")
    for service in Service.objects.all():
        print(f"  - {service.name}: {service.display_name}")
    
    print(f"\nPlatform Services: {PlatformService.objects.count()}")
    for ps in PlatformService.objects.all():
        print(f"  - {ps.platform.name} + {ps.service.name} (enabled: {ps.is_enabled})")
    
    print(f"\nBrightData Configs: {BrightDataConfig.objects.count()}")
    for config in BrightDataConfig.objects.all():
        print(f"  - {config.platform}: {config.dataset_id} (active: {config.is_active})")

if __name__ == '__main__':
    test_local_data()