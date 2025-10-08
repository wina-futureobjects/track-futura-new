#!/usr/bin/env python
"""
URGENT: Fix production BrightData config with correct zone
"""
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataConfig

def fix_production_config():
    print("🔧 FIXING PRODUCTION BRIGHTDATA CONFIG")
    print("="*50)
    
    try:
        # Get all configs and fix them
        configs = BrightDataConfig.objects.all()
        print(f"Found {len(configs)} BrightData configs")
        
        for config in configs:
            print(f"Config: {config.platform} - {config.dataset_id}")
            
            if config.dataset_id == 'hl_f7614f18':
                print(f"  ⚠️  Found incorrect dataset_id: {config.dataset_id}")
                config.dataset_id = 'web_unlocker1'
                config.save()
                print(f"  ✅ Updated to: {config.dataset_id}")
            else:
                print(f"  ✅ Already correct: {config.dataset_id}")
        
        print("\n🎉 All BrightData configs fixed!")
        print("Zone name 'web_unlocker1' is now set correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_production_config()