#!/usr/bin/env python
"""
Fix BrightData configuration with correct dataset IDs and API format
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataConfig

def fix_brightdata_config():
    print("=== Fixing BrightData Configuration ===")
    
    # Update Instagram configuration with your actual scraper ID
    instagram_config, created = BrightDataConfig.objects.get_or_create(
        platform='instagram',
        defaults={
            'dataset_id': 'hl_f7614f18',  # Your actual scraper ID from the URL
            'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb',  # Your real token
            'is_active': True,
        }
    )
    
    if not created:
        instagram_config.dataset_id = 'hl_f7614f18'
        instagram_config.api_token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
        instagram_config.is_active = True
        instagram_config.save()
    
    print(f"✅ Updated Instagram config: {instagram_config.dataset_id}")
    
    # Also update Facebook if needed
    facebook_config, created = BrightDataConfig.objects.get_or_create(
        platform='facebook',
        defaults={
            'dataset_id': 'hl_f7614f18',  # Same scraper for now
            'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb',
            'is_active': True,
        }
    )
    
    if not created:
        facebook_config.dataset_id = 'hl_f7614f18'
        facebook_config.api_token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
        facebook_config.is_active = True
        facebook_config.save()
    
    print(f"✅ Updated Facebook config: {facebook_config.dataset_id}")
    
    return True

if __name__ == '__main__':
    print("🚀 Fixing BrightData configuration...")
    fix_brightdata_config()
    print("✅ BrightData configuration updated!")