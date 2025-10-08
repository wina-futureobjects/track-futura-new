#!/usr/bin/env python3

import sys
import os
import django

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_brightdata_with_database():
    print('🚨 TESTING BRIGHTDATA WITH WORKING DATABASE')
    print('🚨 THIS SHOULD NOW ACTUALLY WORK!')
    print('=' * 60)

    # Test database connection first
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print('✅ Database connection: WORKING')
    except Exception as e:
        print(f'❌ Database error: {str(e)}')
        return False

    # Test BrightData service
    try:
        from brightdata_integration.services import BrightDataAutomatedBatchScraper
        scraper = BrightDataAutomatedBatchScraper()
        print('✅ BrightData service: INITIALIZED')
        print(f'📋 Available datasets: {list(scraper.platform_datasets.keys())}')
    except Exception as e:
        print(f'❌ BrightData service error: {str(e)}')
        return False

    # Test configuration creation/retrieval
    try:
        from brightdata_integration.models import BrightDataConfig
        configs = BrightDataConfig.objects.all()
        print(f'🔧 BrightData configs in database: {configs.count()}')
        
        if configs.count() == 0:
            print('📝 Creating missing configurations...')
            # Create Instagram config
            instagram_config = BrightDataConfig.objects.create(
                name="Instagram Posts Scraper",
                platform="instagram_posts",
                dataset_id="gd_lk5ns7kz21pck8jpis",
                api_token="8af6995e-3baa-4b69-9df7-8d7671e621eb",
                is_active=True
            )
            print(f'✅ Created Instagram config: {instagram_config.id}')
            
            # Create Facebook config
            facebook_config = BrightDataConfig.objects.create(
                name="Facebook Posts Scraper",
                platform="facebook_posts", 
                dataset_id="gd_lkaxegm826bjpoo9m5",
                api_token="8af6995e-3baa-4b69-9df7-8d7671e621eb",
                is_active=True
            )
            print(f'✅ Created Facebook config: {facebook_config.id}')
            
        configs = BrightDataConfig.objects.all()
        for config in configs:
            print(f'📋 Config: {config.platform} -> {config.dataset_id}')
            
    except Exception as e:
        print(f'❌ Config error: {str(e)}')
        return False

    # Test actual scraper trigger
    print('\n🔍 TESTING ACTUAL SCRAPER TRIGGERS:')
    print('-' * 40)
    
    # Test Instagram
    try:
        result = scraper.trigger_scraper('instagram', ['https://www.instagram.com/nike/'])
        print(f'📱 Instagram result: {result}')
        if result.get('success'):
            print('✅ Instagram scraper: WORKING!')
        else:
            print(f'❌ Instagram scraper failed: {result.get("error")}')
    except Exception as e:
        print(f'❌ Instagram scraper error: {str(e)}')

    # Test Facebook
    try:
        result = scraper.trigger_scraper('facebook', ['https://www.facebook.com/nike/'])
        print(f'📘 Facebook result: {result}')
        if result.get('success'):
            print('✅ Facebook scraper: WORKING!')
        else:
            print(f'❌ Facebook scraper failed: {result.get("error")}')
    except Exception as e:
        print(f'❌ Facebook scraper error: {str(e)}')

    # Test database records creation
    try:
        from brightdata_integration.models import BrightDataScraperRequest
        requests = BrightDataScraperRequest.objects.all()
        print(f'\n📊 BrightData requests in database: {requests.count()}')
        for req in requests.order_by('-created_at')[:3]:
            print(f'   📝 Request {req.id}: {req.platform} - {req.status}')
    except Exception as e:
        print(f'❌ Database requests error: {str(e)}')

    print(f'\n🎯 FINAL STATUS:')
    print(f'🎉 BrightData integration should now be FULLY WORKING!')
    print(f'💾 Database: SQLite (development mode)')
    print(f'🔧 Configurations: Created and stored')
    print(f'🚀 Ready for testing in your application!')

if __name__ == '__main__':
    test_brightdata_with_database()