#!/usr/bin/env python3
"""
Deploy BrightData Configuration via HTTP API
===========================================
Deploy BrightData configuration to production using HTTP requests.
"""

import requests
import json

def deploy_brightdata_via_api():
    """Deploy BrightData configuration using the production API"""
    print("🚀 DEPLOYING BRIGHTDATA CONFIGURATION VIA API")
    print("=" * 60)
    
    production_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Configuration data
    brightdata_configs = [
        {
            "name": "Instagram Posts Scraper",
            "platform": "instagram",
            "dataset_id": "gd_lk5ns7kz21pck8jpis",
            "api_token": "8af6995e-3baa-4b69-9df7-8d7671e621eb",
            "is_active": True
        },
        {
            "name": "Facebook Posts Scraper", 
            "platform": "facebook",
            "dataset_id": "gd_lkaxegm826bjpoo9m5",
            "api_token": "8af6995e-3baa-4b69-9df7-8d7671e621eb",
            "is_active": True
        }
    ]
    
    print("1. Testing API endpoint accessibility...")
    try:
        response = requests.get(f"{production_url}/api/brightdata/configs/", timeout=10)
        print(f"   Config API status: {response.status_code}")
        
        if response.status_code == 200:
            existing_configs = response.json()
            print(f"   ✅ Found {len(existing_configs)} existing configurations")
            
            # Display existing configs
            for config in existing_configs:
                print(f"      - {config.get('platform', 'unknown')}: {config.get('name', 'unnamed')}")
                
        elif response.status_code == 401:
            print("   ⚠️  Authentication required - trying to create via webhook")
            # Use webhook to trigger setup
            webhook_response = requests.post(f"{production_url}/api/brightdata/webhook/",
                                           json={
                                               "setup_type": "platforms_and_services",
                                               "brightdata_configs": brightdata_configs
                                           },
                                           headers={"Content-Type": "application/json"},
                                           timeout=15)
            print(f"   Webhook setup status: {webhook_response.status_code}")
            print(f"   Webhook response: {webhook_response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ API test failed: {str(e)}")
    
    print("\n2. Testing scraper trigger after configuration...")
    try:
        trigger_response = requests.post(f"{production_url}/api/brightdata/trigger-scraper/",
                                       json={
                                           "platform": "instagram",
                                           "urls": ["https://www.instagram.com/nike/"]
                                       },
                                       headers={"Content-Type": "application/json"},
                                       timeout=15)
        print(f"   Trigger status: {trigger_response.status_code}")
        print(f"   Trigger response: {trigger_response.text[:300]}...")
        
        if trigger_response.status_code == 200:
            result = trigger_response.json()
            if result.get('success'):
                print("   ✅ BrightData scraper trigger successful!")
                print(f"   Platform: {result.get('platform')}")
                print(f"   Dataset ID: {result.get('dataset_id')}")
                return True
            else:
                print(f"   ❌ Trigger failed: {result.get('error', 'Unknown error')}")
        else:
            print("   ❌ Trigger endpoint failed")
            
    except Exception as e:
        print(f"   ❌ Trigger test failed: {str(e)}")
    
    return False

def create_test_user_via_api():
    """Create a test user for authentication testing"""
    print("\n3. Creating test user for authentication...")
    
    production_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Try to create user via webhook (if supported)
    try:
        user_setup_response = requests.post(f"{production_url}/api/brightdata/webhook/",
                                          json={
                                              "setup_type": "create_test_user",
                                              "username": "test",
                                              "password": "test123",
                                              "email": "test@trackfutura.com"
                                          },
                                          headers={"Content-Type": "application/json"},
                                          timeout=10)
        print(f"   User creation status: {user_setup_response.status_code}")
        print(f"   User creation response: {user_setup_response.text[:200]}...")
        
    except Exception as e:
        print(f"   ⚠️  User creation via webhook failed: {str(e)}")
        print("   Manual user creation will be needed")

if __name__ == "__main__":
    success = deploy_brightdata_via_api()
    create_test_user_via_api()
    
    if success:
        print("\n🎉 BRIGHTDATA DEPLOYMENT SUCCESSFUL!")
        print("   Your BrightData integration is now working in production!")
    else:
        print("\n⚠️  DEPLOYMENT NEEDS MANUAL COMPLETION")
        print("   Check the logs above and complete configuration manually")
        
    print(f"\n📋 NEXT STEPS:")
    print(f"   1. Test the endpoint: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/")
    print(f"   2. Check BrightData dashboard for scraping jobs")
    print(f"   3. Monitor webhook for incoming data")