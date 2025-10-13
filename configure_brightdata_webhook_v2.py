#!/usr/bin/env python3
"""
Configure BrightData Webhook via Collector API
Uses the correct BrightData collector API structure
"""
import requests
import json

# BrightData configuration
BRIGHTDATA_API_TOKEN = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
WEBHOOK_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/"

# Collector IDs from your configuration
COLLECTORS = {
    "instagram": "c_lk5ns7kz21pck8jpis",
    "facebook": "c_lkaxegm826bjpoo9m5"
}

def configure_collector_webhook(collector_id, platform_name):
    """Configure webhook for a BrightData collector"""
    
    print(f"🔧 Configuring webhook for {platform_name} collector: {collector_id}")
    
    # BrightData Collector API endpoint
    collector_url = f"https://brightdata.com/api/collector/{collector_id}"
    
    # Get current collector configuration
    headers = {
        "Authorization": f"Bearer {BRIGHTDATA_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # First, get the current collector config
        get_response = requests.get(collector_url, headers=headers, timeout=30)
        print(f"📡 GET {collector_url}")
        print(f"Status: {get_response.status_code}")
        
        if get_response.status_code == 200:
            collector_config = get_response.json()
            
            # Update config with webhook
            collector_config['webhook_url'] = WEBHOOK_URL
            collector_config['webhook_method'] = 'POST'
            collector_config['webhook_headers'] = {
                'Authorization': f'Bearer {BRIGHTDATA_API_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            # Update the collector
            put_response = requests.put(
                collector_url,
                headers=headers,
                data=json.dumps(collector_config),
                timeout=30
            )
            
            print(f"📡 PUT {collector_url}")
            print(f"Status: {put_response.status_code}")
            print(f"Response: {put_response.text[:200]}...")
            
            if put_response.status_code == 200:
                print(f"✅ Webhook configured successfully for {platform_name}")
                return True
            else:
                print(f"❌ Failed to update collector for {platform_name}: {put_response.status_code}")
                return False
                
        else:
            print(f"❌ Failed to get collector config for {platform_name}: {get_response.status_code}")
            print(f"Response: {get_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error configuring webhook for {platform_name}: {e}")
        return False

def test_brightdata_api():
    """Test BrightData API access"""
    
    print("🧪 Testing BrightData API access...")
    
    headers = {
        "Authorization": f"Bearer {BRIGHTDATA_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Try different API endpoints to find the correct structure
    test_urls = [
        "https://brightdata.com/api/v1/account",
        "https://brightdata.com/api/account",
        "https://brightdata.com/api/collectors",
        "https://brightdata.com/api/v1/collectors"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"📡 GET {url}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ API endpoint working: {url}")
                data = response.json()
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return url
            else:
                print(f"❌ {response.status_code}: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ Error testing {url}: {e}")
    
    return None

def configure_via_trigger_api():
    """Configure webhook via the trigger API we know works"""
    
    print("🔧 Configuring webhook via trigger API...")
    
    # Use our existing trigger endpoint to configure webhook
    trigger_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/"
    
    # Test trigger with webhook configuration
    test_data = {
        "folder_id": 1,
        "user_id": 1,
        "num_of_posts": 1,
        "date_range": {
            "start_date": "2024-10-01T00:00:00.000Z",
            "end_date": "2024-10-13T23:59:59.000Z"
        },
        "configure_webhook": True,
        "webhook_url": WEBHOOK_URL,
        "webhook_auth": f"Bearer {BRIGHTDATA_API_TOKEN}"
    }
    
    try:
        response = requests.post(
            trigger_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_data),
            timeout=60
        )
        
        print(f"📡 POST {trigger_url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook configuration via trigger API successful")
            return True
        else:
            print(f"❌ Webhook configuration via trigger API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error configuring via trigger API: {e}")
        return False

def main():
    """Main webhook configuration function"""
    
    print("🌐 BRIGHTDATA WEBHOOK CONFIGURATION (V2)")
    print("=" * 50)
    
    # Step 1: Test BrightData API access
    working_api = test_brightdata_api()
    
    if working_api:
        print(f"✅ Found working API endpoint: {working_api}")
        
        # Step 2: Try to configure webhooks via collectors
        success_count = 0
        total_count = len(COLLECTORS)
        
        for platform, collector_id in COLLECTORS.items():
            if configure_collector_webhook(collector_id, platform):
                success_count += 1
        
        if success_count > 0:
            print(f"✅ Configured {success_count}/{total_count} collectors successfully")
            return True
    
    # Fallback: Configure via our trigger API
    print("🔄 Trying fallback configuration via trigger API...")
    if configure_via_trigger_api():
        print("✅ Webhook configured via trigger API fallback")
        return True
    
    print("❌ All webhook configuration methods failed")
    
    # Manual instructions
    print(f"\n📋 MANUAL CONFIGURATION REQUIRED:")
    print(f"   1. Go to: https://brightdata.com/cp/")
    print(f"   2. Navigate to your collectors/datasets:")
    print(f"      • Instagram: c_lk5ns7kz21pck8jpis or gd_lk5ns7kz21pck8jpis")
    print(f"      • Facebook: c_lkaxegm826bjpoo9m5 or gd_lkaxegm826bjpoo9m5")
    print(f"   3. In each collector/dataset settings, add:")
    print(f"      • Webhook URL: {WEBHOOK_URL}")
    print(f"      • Method: POST")
    print(f"      • Authorization: Bearer {BRIGHTDATA_API_TOKEN}")
    print(f"      • Content-Type: application/json")
    
    return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)