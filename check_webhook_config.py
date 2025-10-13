#!/usr/bin/env python
"""
Check BrightData webhook configuration and delivery method
"""

import requests
import json

def check_brightdata_webhook_config():
    """Check if BrightData is configured with webhooks"""
    
    print("🔍 CHECKING BRIGHTDATA WEBHOOK CONFIGURATION")
    print("=" * 60)
    
    base_url = "https://trackfutura.futureobjects.io"
    
    # Check BrightData configurations
    print("📊 Checking BrightData configs...")
    try:
        config_response = requests.get(f"{base_url}/api/brightdata/configs/", timeout=30)
        print(f"Config endpoint status: {config_response.status_code}")
        
        if config_response.status_code == 200:
            configs = config_response.json()
            print(f"📄 Response type: {type(configs)}")
            
            if isinstance(configs, dict) and 'results' in configs:
                configs = configs['results']
            
            if isinstance(configs, list):
                print(f"✅ Found {len(configs)} configurations")
                
                for i, config in enumerate(configs[:3]):  # Show first 3
                    print(f"\n📋 CONFIG {i+1}:")
                    print(f"  ID: {config.get('id')}")
                    print(f"  Zone: {config.get('zone_name')}")
                    print(f"  Zone ID: {config.get('zone_id')}")
                    print(f"  Webhook URL: {config.get('webhook_url', 'NOT SET')}")
                    print(f"  Delivery Method: {config.get('delivery_method', 'NOT SET')}")
                    print(f"  Active: {config.get('active', 'Unknown')}")
                    
                    # Check if webhook is properly configured
                    webhook_url = config.get('webhook_url')
                    delivery_method = config.get('delivery_method')
                    
                    if not webhook_url:
                        print(f"  ❌ No webhook URL configured!")
                    elif 'webhook' not in webhook_url.lower():
                        print(f"  ⚠️  Webhook URL doesn't contain 'webhook': {webhook_url}")
                    else:
                        print(f"  ✅ Webhook URL looks correct")
                    
                    if delivery_method != 'webhook':
                        print(f"  ❌ Delivery method is '{delivery_method}', should be 'webhook'")
                    else:
                        print(f"  ✅ Delivery method is correctly set to 'webhook'")
                        
            else:
                print(f"❌ Unexpected configs format: {configs}")
        else:
            print(f"❌ Failed to get configs: {config_response.text}")
            
    except Exception as e:
        print(f"💥 Error checking configs: {e}")
    
    # Check recent scraper requests to see their webhook configuration
    print(f"\n📊 Checking recent scraper requests...")
    try:
        requests_response = requests.get(f"{base_url}/api/brightdata/scraper-requests/?limit=5", timeout=30)
        print(f"Scraper requests status: {requests_response.status_code}")
        
        if requests_response.status_code == 200:
            scraper_data = requests_response.json()
            
            if isinstance(scraper_data, dict) and 'results' in scraper_data:
                requests_list = scraper_data['results']
            else:
                requests_list = scraper_data if isinstance(scraper_data, list) else []
            
            print(f"✅ Found {len(requests_list)} recent scraper requests")
            
            for i, req in enumerate(requests_list[:3]):
                print(f"\n📋 REQUEST {i+1}:")
                print(f"  ID: {req.get('id')}")
                print(f"  Job ID: {req.get('job_id')}")
                print(f"  Status: {req.get('status')}")
                print(f"  Target URL: {req.get('target_url')}")
                print(f"  Webhook Delivered: {req.get('webhook_delivered', 'Unknown')}")
                print(f"  Created: {req.get('created_at')}")
                
        else:
            print(f"❌ Failed to get scraper requests: {requests_response.text}")
            
    except Exception as e:
        print(f"💥 Error checking scraper requests: {e}")

def check_webhook_endpoints():
    """Check if webhook endpoints are working"""
    
    print(f"\n🔗 CHECKING WEBHOOK ENDPOINTS")
    print("=" * 40)
    
    base_url = "https://trackfutura.futureobjects.io"
    
    # Test webhook endpoint
    webhook_endpoints = [
        "/api/brightdata/webhook/",
        "/api/brightdata/notify/",
    ]
    
    for endpoint in webhook_endpoints:
        try:
            print(f"📡 Testing {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=30)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 405:  # Method not allowed is expected for POST-only webhooks
                print(f"  ✅ Webhook endpoint exists (405 = Method Not Allowed for GET)")
            elif response.status_code == 200:
                print(f"  ✅ Webhook endpoint accessible")
            else:
                print(f"  ❌ Unexpected status: {response.text[:100]}")
                
        except Exception as e:
            print(f"  💥 Error testing {endpoint}: {e}")

def check_webhook_url_format():
    """Check what the webhook URL should be"""
    
    print(f"\n🔧 WEBHOOK URL FORMAT CHECK")
    print("=" * 40)
    
    expected_webhook_url = "https://trackfutura.futureobjects.io/api/brightdata/webhook/"
    print(f"Expected webhook URL: {expected_webhook_url}")
    
    # Test if this URL is accessible
    try:
        response = requests.post(
            expected_webhook_url,
            json={"test": "webhook"},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        print(f"Webhook URL test status: {response.status_code}")
        if response.status_code in [200, 405]:
            print("✅ Webhook URL is accessible")
        else:
            print(f"❌ Webhook URL issue: {response.text}")
    except Exception as e:
        print(f"💥 Error testing webhook URL: {e}")

if __name__ == "__main__":
    check_brightdata_webhook_config()
    check_webhook_endpoints()
    check_webhook_url_format()
    
    print(f"\n🎯 SUMMARY")
    print("=" * 40)
    print("If delivery method is empty or not 'webhook', the BrightData")
    print("configurations need to be updated to use webhook delivery.")
    print("This will ensure data is pushed via webhooks instead of polling.")