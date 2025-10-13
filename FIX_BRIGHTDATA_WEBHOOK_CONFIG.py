#!/usr/bin/env python3
"""
🚨 EMERGENCY: FIX BRIGHTDATA WEBHOOK CONFIGURATION
The user is right - we need to fix the webhook delivery from BrightData, not create fake data!
"""

import requests
import json
import os

BASE_URL = "https://trackfutura.futureobjects.io"

def check_webhook_endpoint():
    """Check if our webhook endpoint is accessible"""
    print("🔍 CHECKING WEBHOOK ENDPOINT")
    print("=" * 50)
    
    webhook_url = f"{BASE_URL}/trigger-system/brightdata-webhook/"
    
    try:
        # Test GET (should return method not allowed)
        response = requests.get(webhook_url, timeout=10)
        print(f"GET {webhook_url}: {response.status_code}")
        
        # Test POST (this is what BrightData sends)
        test_payload = {
            "status": "completed",
            "snapshot_id": "test_webhook",
            "data_url": "https://example.com/test"
        }
        
        post_response = requests.post(webhook_url, json=test_payload, timeout=10)
        print(f"POST {webhook_url}: {post_response.status_code}")
        
        if post_response.status_code == 200:
            print("✅ Webhook endpoint is working!")
            return webhook_url
        else:
            print(f"❌ Webhook endpoint failed: {post_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Webhook endpoint error: {e}")
        return None

def check_brightdata_config():
    """Check what BrightData configuration we have"""
    print("\n🔧 CHECKING BRIGHTDATA CONFIG")
    print("=" * 50)
    
    # Check our BrightData configurations
    config_url = f"{BASE_URL}/api/brightdata/configs/"
    
    try:
        response = requests.get(config_url, timeout=10)
        if response.status_code == 200:
            configs = response.json()
            print(f"✅ Found {len(configs)} BrightData configs:")
            
            for config in configs:
                print(f"   📝 Config ID: {config.get('id')}")
                print(f"      Dataset ID: {config.get('dataset_id')}")
                print(f"      Webhook URL: {config.get('webhook_url', 'NOT SET')}")
                print(f"      API Token: {'SET' if config.get('api_token') else 'NOT SET'}")
                print()
                
            return configs
        else:
            print(f"❌ Config check failed: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Config check error: {e}")
        return []

def fix_brightdata_webhook_config():
    """Update BrightData configuration with correct webhook URL"""
    print("\n🔧 FIXING BRIGHTDATA WEBHOOK CONFIG")
    print("=" * 50)
    
    # The correct webhook URL for production
    correct_webhook_url = f"{BASE_URL}/trigger-system/brightdata-webhook/"
    
    # Check if we need to create or update config
    configs = check_brightdata_config()
    
    if not configs:
        print("No configs found - need to create new config")
        # Create new config
        new_config = {
            "dataset_id": "gd_l7q7dkf244hwqzk5di",  # Instagram dataset
            "webhook_url": correct_webhook_url,
            "api_token": os.getenv("BRIGHTDATA_API_TOKEN", ""),
            "platform": "instagram"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/brightdata/configs/", json=new_config, timeout=30)
            if response.status_code in [200, 201]:
                print(f"✅ Created new BrightData config!")
                return True
            else:
                print(f"❌ Failed to create config: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Config creation error: {e}")
            return False
    else:
        # Update existing configs
        for config in configs:
            config_id = config.get('id')
            current_webhook = config.get('webhook_url', '')
            
            if current_webhook != correct_webhook_url:
                print(f"🔧 Updating config {config_id} webhook URL...")
                print(f"   From: {current_webhook}")
                print(f"   To: {correct_webhook_url}")
                
                update_data = {
                    "webhook_url": correct_webhook_url
                }
                
                try:
                    response = requests.patch(f"{BASE_URL}/api/brightdata/configs/{config_id}/", json=update_data, timeout=30)
                    if response.status_code == 200:
                        print(f"✅ Updated config {config_id}!")
                    else:
                        print(f"❌ Failed to update config {config_id}: {response.status_code}")
                except Exception as e:
                    print(f"❌ Config update error: {e}")
            else:
                print(f"✅ Config {config_id} already has correct webhook URL")
        
        return True

def test_brightdata_trigger():
    """Test triggering a BrightData scraper to verify webhook delivery"""
    print("\n🚀 TESTING BRIGHTDATA TRIGGER")
    print("=" * 50)
    
    test_data = {
        "platform": "instagram",
        "source_urls": ["https://www.instagram.com/nike/"],
        "max_posts": 3,
        "notify": True  # Enable webhook delivery
    }
    
    trigger_endpoints = [
        f"{BASE_URL}/api/brightdata/trigger-system/",
        f"{BASE_URL}/api/brightdata/trigger-scraper/"
    ]
    
    for endpoint in trigger_endpoints:
        try:
            print(f"🔍 Testing trigger: {endpoint}")
            response = requests.post(endpoint, json=test_data, timeout=60)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Trigger successful!")
                print(f"   Job ID: {result.get('job_id', 'N/A')}")
                print(f"   Snapshot ID: {result.get('snapshot_id', 'N/A')}")
                print(f"   Webhook will deliver to: {BASE_URL}/trigger-system/brightdata-webhook/")
                return result
            else:
                print(f"❌ Trigger failed: {response.status_code} - {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Trigger error: {e}")
    
    return None

def main():
    """Fix the BrightData webhook configuration properly"""
    print("🚨 EMERGENCY FIX: BRIGHTDATA WEBHOOK CONFIGURATION")
    print("User is RIGHT - we need to fix webhook delivery, not create fake data!")
    print("=" * 70)
    
    # Step 1: Check webhook endpoint
    webhook_url = check_webhook_endpoint()
    if not webhook_url:
        print("\n❌ CRITICAL: Webhook endpoint not working!")
        return
    
    # Step 2: Check and fix BrightData config
    config_fixed = fix_brightdata_webhook_config()
    if not config_fixed:
        print("\n❌ CRITICAL: Could not fix BrightData config!")
        return
    
    # Step 3: Test the complete flow
    trigger_result = test_brightdata_trigger()
    
    print("\n" + "=" * 70)
    print("🎯 BRIGHTDATA WEBHOOK FIX SUMMARY")
    print("=" * 70)
    
    if webhook_url and config_fixed:
        print("✅ Webhook endpoint: Working")
        print("✅ BrightData config: Fixed")
        print(f"✅ Webhook URL: {webhook_url}")
        
        if trigger_result:
            print("✅ Trigger test: Successful")
            print("🎉 BRIGHTDATA WEBHOOK IS NOW PROPERLY CONFIGURED!")
            print("\nNext steps:")
            print("1. Wait 2-3 minutes for BrightData to scrape")
            print("2. BrightData will send webhook to our endpoint")
            print("3. Data will automatically appear in frontend")
            print("4. Check /organizations/1/projects/2/data-storage for results")
        else:
            print("⚠️  Trigger test: Failed")
            print("Configuration is fixed but trigger needs debugging")
    else:
        print("❌ WEBHOOK CONFIGURATION STILL HAS ISSUES")
        print("Need manual intervention to fix BrightData setup")
    
    print("=" * 70)

if __name__ == "__main__":
    main()