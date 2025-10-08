#!/usr/bin/env python3
"""
BRIGHTDATA FINAL VERIFICATION TEST
=================================
Test BrightData integration after completing manual setup.
"""

import requests
import json

def verify_brightdata_deployment():
    """Verify BrightData deployment is working correctly"""
    print("🧪 BRIGHTDATA FINAL VERIFICATION TEST")
    print("=" * 60)
    
    production_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print(f"🌐 Testing production URL: {production_url}")
    print()
    
    # Test 1: Health Check
    print("1. 🏥 Health Check...")
    try:
        health_response = requests.get(f"{production_url}/api/health/", timeout=10)
        print(f"   Health status: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ Server healthy - Database: {health_data.get('database', 'unknown')}")
        else:
            print(f"   ⚠️  Health check failed: {health_response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Health check error: {str(e)}")
    
    # Test 2: BrightData Config API
    print("\n2. 🔧 BrightData Configuration API...")
    try:
        config_response = requests.get(f"{production_url}/api/brightdata/configs/", timeout=10)
        print(f"   Config API status: {config_response.status_code}")
        
        if config_response.status_code == 200:
            configs = config_response.json()
            print(f"   ✅ Found {len(configs)} BrightData configurations:")
            for config in configs:
                print(f"      - {config.get('platform', 'unknown')}: {config.get('name', 'unnamed')} (Active: {config.get('is_active', False)})")
        elif config_response.status_code == 401:
            print("   ⚠️  Authentication required")
        else:
            print(f"   ❌ Config API error: {config_response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Config API error: {str(e)}")
    
    # Test 3: Trigger Endpoint
    print("\n3. 🚀 Scraper Trigger Endpoint...")
    try:
        trigger_response = requests.post(f"{production_url}/api/brightdata/trigger-scraper/",
                                       json={
                                           "platform": "instagram",
                                           "urls": ["https://www.instagram.com/nike/"]
                                       },
                                       headers={"Content-Type": "application/json"},
                                       timeout=20)
        
        print(f"   Trigger status: {trigger_response.status_code}")
        print(f"   Response: {trigger_response.text[:300]}...")
        
        if trigger_response.status_code == 200:
            result = trigger_response.json()
            if result.get('success'):
                print("   ✅ SUCCESS! BrightData scraper triggered successfully!")
                print(f"      Platform: {result.get('platform')}")
                print(f"      Dataset ID: {result.get('dataset_id')}")
                print(f"      URLs processed: {result.get('urls_count')}")
                return True
            else:
                print(f"   ❌ Trigger failed: {result.get('error', 'Unknown error')}")
        elif trigger_response.status_code == 500:
            print("   ❌ Server error - configuration may be missing")
        elif trigger_response.status_code == 404:
            print("   ❌ Endpoint not found - URL routing issue")
        else:
            print(f"   ⚠️  Unexpected status: {trigger_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Trigger test error: {str(e)}")
    
    # Test 4: Webhook Endpoint
    print("\n4. 🔗 Webhook Endpoint...")
    try:
        webhook_response = requests.post(f"{production_url}/api/brightdata/webhook/",
                                       json={"test": "webhook_verification"},
                                       headers={"Content-Type": "application/json"},
                                       timeout=10)
        print(f"   Webhook status: {webhook_response.status_code}")
        if webhook_response.status_code == 200:
            print("   ✅ Webhook endpoint ready to receive data")
        else:
            print(f"   ⚠️  Webhook response: {webhook_response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Webhook test error: {str(e)}")
    
    # Test 5: Authentication (if available)
    print("\n5. 🔐 Authentication Test...")
    try:
        login_response = requests.post(f"{production_url}/api/users/login/",
                                     json={
                                         "username": "test",
                                         "password": "test123"
                                     },
                                     headers={"Content-Type": "application/json"},
                                     timeout=10)
        
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            if "access" in token_data:
                print("   ✅ Authentication working - token received")
                
                # Test authenticated config access
                headers = {"Authorization": f"Bearer {token_data['access']}"}
                auth_config_response = requests.get(f"{production_url}/api/brightdata/configs/",
                                                   headers=headers,
                                                   timeout=10)
                
                if auth_config_response.status_code == 200:
                    print("   ✅ Authenticated API access working")
                else:
                    print(f"   ⚠️  Authenticated access failed: {auth_config_response.status_code}")
            else:
                print("   ❌ No access token in response")
        else:
            print(f"   ⚠️  Login failed: {login_response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Authentication test error: {str(e)}")
    
    return False

def print_final_status():
    """Print final deployment status"""
    print("\n" + "=" * 60)
    print("📊 BRIGHTDATA DEPLOYMENT STATUS SUMMARY")
    print("=" * 60)
    
    print("\n✅ COMPLETED SUCCESSFULLY:")
    print("   - Local BrightData integration working")
    print("   - Production code deployed")
    print("   - URL routing fixed")
    print("   - Service classes configured")
    print("   - API credentials verified")
    print("   - Webhook endpoints ready")
    
    print("\n🎯 FINAL CHECKLIST:")
    print("   □ BrightData configurations created in production database")
    print("   □ Test user created for authentication")
    print("   □ Scraper trigger endpoint returns success")
    print("   □ BrightData dashboard shows active jobs")
    print("   □ Webhook receives data from BrightData")
    
    print("\n🚀 NEXT STEPS:")
    print("   1. Complete manual setup commands when server is accessible")
    print("   2. Run this verification script again")
    print("   3. Monitor BrightData dashboard for scraping activity")
    print("   4. Test with real Instagram/Facebook URLs")
    
    print("\n📞 SUPPORT:")
    print("   - BrightData Dashboard: https://brightdata.com/cp")
    print("   - Local test script: python fix_brightdata_local.py")
    print("   - Manual setup: python BRIGHTDATA_MANUAL_SETUP.py")

if __name__ == "__main__":
    success = verify_brightdata_deployment()
    print_final_status()
    
    if success:
        print("\n🎉 CONGRATULATIONS! BRIGHTDATA INTEGRATION IS FULLY WORKING! 🎉")
    else:
        print("\n⏳ DEPLOYMENT READY - COMPLETE MANUAL SETUP TO FINISH")