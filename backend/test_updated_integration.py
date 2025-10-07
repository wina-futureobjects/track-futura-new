#!/usr/bin/env python3
"""
Test the updated BrightData integration
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataConfig
from brightdata_integration.services import BrightDataAutomatedBatchScraper

def test_updated_integration():
    print("=== TESTING UPDATED BRIGHTDATA INTEGRATION ===")
    print()
    
    # Test each platform configuration
    configs = BrightDataConfig.objects.filter(is_active=True)
    
    for config in configs:
        print(f"🧪 Testing {config.platform.upper()} configuration...")
        print(f"   Config: {config.name}")
        print(f"   Dataset ID: {config.dataset_id}")
        
        scraper = BrightDataAutomatedBatchScraper()
        result = scraper.test_brightdata_connection(config)
        
        print(f"   Success: {result.get('success', False)}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        if result.get('success'):
            snapshot_id = result.get('snapshot_id')
            if snapshot_id:
                print(f"   ✅ Snapshot ID: {snapshot_id}")
                print(f"   🎉 {config.platform.upper()} integration is working!")
            else:
                print(f"   ⚠️  No snapshot ID returned")
        else:
            print(f"   ❌ Test failed for {config.platform}")
            
        print()
    
    print("📋 INTEGRATION STATUS:")
    working_platforms = []
    
    for config in configs:
        scraper = BrightDataAutomatedBatchScraper()
        result = scraper.test_brightdata_connection(config)
        if result.get('success'):
            working_platforms.append(config.platform)
    
    if working_platforms:
        print(f"   ✅ Working platforms: {', '.join(working_platforms).upper()}")
        print("   🎉 BrightData integration is ready for scraping!")
        print()
        print("   📝 You can now:")
        print("   1. Create scraping jobs in TrackFutura")
        print("   2. Monitor jobs in your BrightData dashboard")
        print("   3. View results when scraping completes")
    else:
        print("   ❌ No working platforms found")
        print("   Please check your BrightData account configuration")

if __name__ == "__main__":
    test_updated_integration()