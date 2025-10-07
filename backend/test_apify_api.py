#!/usr/bin/env python
import os
import sys
import django
import requests

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def test_apify_api():
    """Test basic Apify API connectivity"""
    # Get API token from environment
    api_token = settings.APIFY_API_TOKEN or os.getenv('APIFY_API_TOKEN', '')
    
    if not api_token:
        print("❌ ERROR: APIFY_API_TOKEN not found in environment variables")
        return False
        
    base_url = 'https://api.apify.com/v2'
    headers = {'Authorization': f'Bearer {api_token}'}

    print('=== Testing Basic Apify API Access ===')
    print(f'Using API token: {api_token[:15]}...')  # Only show first 15 chars for security
    
    try:
        # Test 1: User info
        response = requests.get(f'{base_url}/users/me', headers=headers, timeout=10)
        print(f'User API Status: {response.status_code}')
        
        if response.status_code == 200:
            user_data = response.json()
            print('✅ API Token is valid!')
            print(f'User ID: {user_data.get("data", {}).get("id", "Unknown")}')
        else:
            print('❌ API Token test failed!')
            print(f'Response: {response.text[:200]}')
            return False
            
        # Test 2: List public actors (store)
        print('\n=== Testing Public Actors Access ===')
        store_url = f'{base_url}/store'
        store_response = requests.get(store_url, headers=headers, timeout=10)
        
        if store_response.status_code == 200:
            store_data = store_response.json()
            total_actors = store_data.get('total', 0)
            print(f'✅ Found {total_actors} public actors in store')
            
            # Show some actors that might be useful for social media
            actors = store_data.get('data', [])
            social_actors = []
            
            for actor in actors[:20]:  # Check first 20
                name = actor.get('name', '').lower()
                if any(platform in name for platform in ['instagram', 'facebook', 'tiktok', 'linkedin', 'social']):
                    social_actors.append({
                        'id': actor.get('id'),
                        'name': actor.get('name'),
                        'title': actor.get('title', 'No title')
                    })
            
            print(f'\nSocial Media Actors Found ({len(social_actors)}):')
            for actor in social_actors[:10]:  # Show first 10
                print(f'  - {actor["id"]}: {actor["name"]}')
                print(f'    {actor["title"]}')
                
        else:
            print(f'❌ Failed to access store: {store_response.status_code}')
            print(f'Response: {store_response.text[:200]}')
            
        return True
        
    except Exception as e:
        print(f'❌ Error testing API: {str(e)}')
        return False

def update_apify_configs_with_working_actors():
    """Update configurations with working actor IDs"""
    from apify_integration.models import ApifyConfig
    from django.utils import timezone
    
    print('\n=== Updating Apify Configurations ===')
    
    # These are generic/placeholder actor IDs - in production, replace with actual working ones
    working_actors = {
        'instagram_posts': 'dtrungtin/instagram-scraper',  # Popular Instagram scraper
        'facebook_posts': 'apify/facebook-pages-scraper',  # Facebook pages scraper
        'tiktok_posts': 'clockworks/free-tiktok-scraper',  # Free TikTok scraper
        'linkedin_posts': 'voyager/linkedin-company-scraper',  # LinkedIn scraper
    }
    
    # Get API key from environment
    api_key = settings.APIFY_API_TOKEN or os.getenv('APIFY_API_TOKEN', '')
    
    if not api_key:
        print("❌ ERROR: APIFY_API_TOKEN not found in environment variables")
        return False
    
    for platform, actor_id in working_actors.items():
        config = ApifyConfig.objects.filter(platform=platform).first()
        if config:
            old_actor = config.actor_id
            config.actor_id = actor_id
            config.api_token = api_key
            config.updated_at = timezone.now()
            config.save()
            print(f'✅ Updated {platform}:')
            print(f'   From: {old_actor}')
            print(f'   To: {actor_id}')
        else:
            print(f'❌ Config not found for {platform}')
        print()

if __name__ == '__main__':
    if test_apify_api():
        update_apify_configs_with_working_actors()
        print('\n🎉 Apify integration setup completed!')
    else:
        print('\n❌ Apify API test failed. Please check your API token.')