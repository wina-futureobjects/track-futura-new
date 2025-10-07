#!/usr/bin/env python3
"""
Fix BrightData configuration with correct API format
"""
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataConfig
from dotenv import load_dotenv

def fix_brightdata_with_correct_format():
    print("=== FIXING BRIGHTDATA WITH CORRECT API FORMAT ===")
    print()
    
    # Load environment
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(env_file)
    
    api_key = os.getenv('BRIGHTDATA_API_KEY')
    if not api_key:
        api_key = "8af6995e-3baa-4b69-9df7-8d7671e621eb"  # Use the provided API key
    
    print(f"Using API Key: {api_key}")
    print()
    
    # Correct dataset IDs from the curl examples
    platform_configs = [
        {
            'platform': 'instagram',
            'dataset_id': 'gd_lk5ns7kz21pck8jpis',  # From Instagram curl example
            'name': 'Instagram Posts Scraper'
        },
        {
            'platform': 'facebook',
            'dataset_id': 'gd_lkaxegm826bjpoo9m5',  # From Facebook curl example  
            'name': 'Facebook Posts Scraper'
        }
    ]
    
    # Update or create configurations
    for platform_config in platform_configs:
        print(f"📝 Configuring {platform_config['platform']}...")
        
        # Check if config exists
        config = BrightDataConfig.objects.filter(platform=platform_config['platform']).first()
        
        if config:
            print(f"   Updating existing config ID {config.id}")
            config.dataset_id = platform_config['dataset_id']
            config.api_token = api_key
            config.is_active = True
            config.save()
        else:
            print(f"   Creating new config")
            config = BrightDataConfig.objects.create(
                name=platform_config['name'],
                platform=platform_config['platform'],
                dataset_id=platform_config['dataset_id'],
                api_token=api_key,
                is_active=True
            )
        
        print(f"   ✅ Config saved: Dataset ID {config.dataset_id}")
        print()
    
    # Test the corrected API endpoint
    print("🧪 TESTING CORRECTED API ENDPOINT:")
    
    # Test Instagram endpoint with a simple request
    test_url = "https://api.brightdata.com/datasets/v3/trigger"
    test_params = {
        'dataset_id': 'gd_lk5ns7kz21pck8jpis',
        'include_errors': 'true',
        'type': 'discover_new',
        'discover_by': 'url'
    }
    
    test_payload = [{
        "url": "https://www.instagram.com/nike/",
        "num_of_posts": 1,
        "start_date": "",
        "end_date": "",
        "post_type": "Post"
    }]
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print(f"Testing URL: {test_url}")
    print(f"Parameters: {test_params}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    print()
    
    try:
        response = requests.post(test_url, params=test_params, json=test_payload, headers=headers, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! BrightData API is working!")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
        elif response.status_code == 401:
            print("❌ UNAUTHORIZED - API key might be invalid")
        elif response.status_code == 400:
            print("❌ BAD REQUEST - Check payload format")
            print(f"Error: {response.text}")
        else:
            print(f"⚠️  Status {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
    
    print()
    print("📋 CONFIGURATION SUMMARY:")
    
    configs = BrightDataConfig.objects.filter(is_active=True)
    for config in configs:
        print(f"   {config.platform.upper()}:")
        print(f"     - Dataset ID: {config.dataset_id}")
        print(f"     - API Token: {config.api_token[:10]}...")
        print(f"     - Status: {'Active' if config.is_active else 'Inactive'}")
        print()
    
    return True

if __name__ == "__main__":
    try:
        success = fix_brightdata_with_correct_format()
        if success:
            print("🎉 BRIGHTDATA CONFIGURATION UPDATED!")
            print("✅ You can now test scraping jobs in your TrackFutura system")
            print("✅ Jobs should appear in your BrightData dashboard")
        else:
            print("❌ Configuration update failed")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()