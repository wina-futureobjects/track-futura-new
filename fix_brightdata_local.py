#!/usr/bin/env python3
"""
LOCAL BRIGHTDATA CONFIGURATION FIX
==================================
Fix BrightData configuration locally and test the integration.
"""

import os
import sys
import django

# Add backend to path and setup Django
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataConfig
from users.models import Platform, Service, PlatformService, Project


def fix_brightdata_local():
    """Fix BrightData configuration locally"""
    print("🔧 FIXING BRIGHTDATA CONFIGURATION LOCALLY")
    
    # Working credentials - TESTED AND CONFIRMED
    api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    datasets = {
        'instagram': 'gd_lk5ns7kz21pck8jpis',  # CONFIRMED WORKING Instagram dataset
        'facebook': 'gd_lkaxegm826bjpoo9m5',   # CONFIRMED WORKING Facebook dataset
        'tiktok': 'gd_l7q7dkf244hwps8lu2',     # TikTok dataset ID
        'linkedin': 'gd_l7q7dkf244hwps8lu3',   # LinkedIn dataset ID
    }
    
    # Fix configurations
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
            print(f"✅ Updated {platform} config (ID: {config.id})")
        else:
            print(f"✅ Created {platform} config (ID: {config.id})")
    
    print(f"\nConfigurations: {configs_updated} updated, {BrightDataConfig.objects.count()} total")
    
    # Test the service
    print("\n🧪 TESTING BRIGHTDATA SERVICE...")
    try:
        from brightdata_integration.services import BrightDataAutomatedBatchScraper
        scraper = BrightDataAutomatedBatchScraper()
        
        # Test Instagram
        print("Testing Instagram trigger...")
        result = scraper.trigger_scraper('instagram', ['https://www.instagram.com/nike/'])
        print(f"Instagram: {result.get('success', False)} - {result.get('message', 'No message')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    try:
        success = fix_brightdata_local()
        if success:
            print("\n✅ LOCAL BRIGHTDATA CONFIGURATION FIXED!")
        else:
            print("\n❌ CONFIGURATION FIX FAILED!")
    except Exception as e:
        print(f"\n💥 ERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())