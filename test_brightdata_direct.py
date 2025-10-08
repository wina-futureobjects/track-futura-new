#!/usr/bin/env python
"""
Test BrightData service directly with restored platform services
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.services import BrightDataAutomatedBatchScraper
from brightdata_integration.models import BrightDataConfig, BrightDataScraperRequest
from users.models import PlatformService

def test_brightdata_direct():
    print("🚀 Testing BrightData service directly...")
    
    # Check platform services
    instagram_posts = PlatformService.objects.filter(
        platform__name='instagram',
        service__name='posts',
        is_enabled=True
    ).first()
    
    if instagram_posts:
        print(f"✅ Found platform service: {instagram_posts.platform.name} + {instagram_posts.service.name}")
        
        # Check BrightData config
        config = BrightDataConfig.objects.filter(platform='instagram', is_active=True).first()
        if config:
            print(f"✅ Found BrightData config: {config.platform} -> {config.dataset_id}")
            
            # Test service
            service = BrightDataAutomatedBatchScraper()
            
            try:
                # Test the method directly
                result = service._execute_brightdata_request(
                    platform='instagram',
                    search_queries=['nike test'],
                    dataset_id=config.dataset_id,
                    api_token=config.api_token
                )
                print(f"✅ BrightData API call result: {result}")
                
            except Exception as e:
                print(f"❌ BrightData API call failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ No BrightData config found for Instagram")
    else:
        print("❌ No Instagram+Posts platform service found")
    
    print("\n=== Database Status ===")
    print(f"Platform Services: {PlatformService.objects.count()}")
    print(f"BrightData Configs: {BrightDataConfig.objects.count()}")
    print(f"BrightData Requests: {BrightDataScraperRequest.objects.count()}")

if __name__ == '__main__':
    test_brightdata_direct()