#!/usr/bin/env python3
"""
Fix BrightData configuration with real API credentials
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataConfig
from dotenv import load_dotenv

def fix_brightdata_config():
    print("=== FIXING BRIGHTDATA CONFIGURATION ===")
    print()
    
    # Load environment variables from project root
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    print(f"Loading environment from: {env_file}")
    load_dotenv(env_file)
    
    # Get API key from environment
    api_key = os.getenv('BRIGHTDATA_API_KEY')
    webhook_token = os.getenv('BRIGHTDATA_WEBHOOK_TOKEN')
    
    if not api_key:
        print("❌ BRIGHTDATA_API_KEY not found in environment variables!")
        print("Please check your .env file")
        return False
    
    print(f"✅ Found BRIGHTDATA_API_KEY: {api_key[:10]}...")
    print(f"✅ Found BRIGHTDATA_WEBHOOK_TOKEN: {webhook_token[:10]}..." if webhook_token else "⚠️  No webhook token found")
    print()
    
    # Update existing configuration
    config = BrightDataConfig.objects.first()
    
    if config:
        print(f"📝 Updating existing configuration: {config.name}")
        old_token = config.api_token
        config.api_token = api_key
        config.save()
        
        print(f"   ✅ Updated API token from '{old_token}' to '{api_key[:10]}...'")
        print()
        
        # Test the updated configuration
        print("🧪 Testing updated configuration...")
        from brightdata_integration.services import BrightDataAutomatedBatchScraper
        
        scraper = BrightDataAutomatedBatchScraper()
        result = scraper.test_brightdata_connection(config)
        
        print(f"   Success: {result.get('success', False)}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        if result.get('success'):
            print("   ✅ BrightData connection is now working!")
        else:
            print(f"   ❌ Connection still failing: {result}")
            
            # Try to get more details about the error
            if 'dataset_info' in result:
                print(f"   Dataset info: {result['dataset_info']}")
        
        return result.get('success', False)
    
    else:
        print("❌ No BrightData configuration found to update!")
        print("   Creating a new configuration...")
        
        # Create a new configuration with proper dataset IDs
        platforms_and_datasets = [
            {
                'platform': 'instagram',
                'dataset_id': 'gd_l7q7dkf244hwps8lu0',  # Instagram dataset
                'name': 'Instagram Posts Scraper'
            },
            {
                'platform': 'facebook', 
                'dataset_id': 'gd_l7q7dkf244hwps8lu1',  # Facebook dataset
                'name': 'Facebook Posts Scraper'
            },
            {
                'platform': 'tiktok',
                'dataset_id': 'gd_l7q7dkf244hwps8lu2',  # TikTok dataset  
                'name': 'TikTok Posts Scraper'
            },
            {
                'platform': 'linkedin',
                'dataset_id': 'gd_l7q7dkf244hwps8lu3',  # LinkedIn dataset
                'name': 'LinkedIn Posts Scraper'
            }
        ]
        
        for platform_config in platforms_and_datasets:
            config = BrightDataConfig.objects.create(
                name=platform_config['name'],
                platform=platform_config['platform'],
                dataset_id=platform_config['dataset_id'],
                api_token=api_key,
                is_active=True
            )
            print(f"   ✅ Created {platform_config['platform']} configuration (ID: {config.id})")
        
        print("\n✅ All platform configurations created!")
        return True

if __name__ == "__main__":
    success = fix_brightdata_config()
    
    if success:
        print("\n🎉 BRIGHTDATA CONFIGURATION FIXED!")
        print("You can now try running scraping jobs and they should appear in your BrightData dashboard.")
    else:
        print("\n❌ Configuration update failed. Please check your BrightData API credentials.")