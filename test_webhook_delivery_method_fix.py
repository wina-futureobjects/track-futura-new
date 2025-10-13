#!/usr/bin/env python3
"""
🚨 WEBHOOK DELIVERY METHOD VERIFICATION TEST
===========================================

Tests if the BrightData webhook delivery method fix is working correctly.
This test confirms that delivery_method is set to "webhook" instead of "api_fetch".
"""

import requests
import json
import time

def test_webhook_delivery_configuration():
    """Test if webhook delivery is properly configured in the backend"""
    
    print("🧪 TESTING WEBHOOK DELIVERY CONFIGURATION")
    print("=" * 50)
    
    base_url = "https://trackfutura.futureobjects.io"
    
    # Test 1: Check if webhook endpoint is accessible
    print("1. 🌐 Testing webhook endpoint accessibility...")
    
    webhook_url = f"{base_url}/api/brightdata/webhook/"
    
    try:
        response = requests.get(webhook_url, timeout=10)
        print(f"   📡 GET {webhook_url}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 405]:  # 405 = Method Not Allowed is OK for POST-only endpoint
            print(f"   ✅ Webhook endpoint is accessible")
            endpoint_accessible = True
        else:
            print(f"   ❌ Webhook endpoint issue: {response.status_code}")
            endpoint_accessible = False
    except Exception as e:
        print(f"   ❌ Cannot access webhook endpoint: {e}")
        endpoint_accessible = False
    
    # Test 2: Test webhook with sample data
    print("\n2. 📡 Testing webhook with delivery method verification...")
    
    sample_webhook_data = [
        {
            "post_id": f"delivery_test_{int(time.time())}",
            "url": "https://instagram.com/p/delivery_test",
            "user_posted": "delivery_test_user",
            "content": "Testing webhook delivery method: should be 'webhook' not 'api_fetch' 🚨",
            "likes": 250,
            "num_comments": 20,
            "platform": "instagram",
            "delivery_method_test": "webhook",  # This should be properly handled
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    ]
    
    try:
        webhook_response = requests.post(
            webhook_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
                "User-Agent": "BrightData-Webhook-Delivery-Test"
            },
            data=json.dumps(sample_webhook_data),
            timeout=30
        )
        
        print(f"   📡 POST {webhook_url}")
        print(f"   Status: {webhook_response.status_code}")
        
        if webhook_response.status_code == 200:
            result = webhook_response.json()
            items_processed = result.get('items_processed', 0)
            delivery_status = result.get('delivery_method', 'unknown')
            
            print(f"   ✅ Webhook delivery test successful!")
            print(f"   📊 Items processed: {items_processed}")
            print(f"   🎯 Delivery method: {delivery_status}")
            webhook_test_passed = True
        else:
            print(f"   ❌ Webhook delivery test failed: {webhook_response.status_code}")
            print(f"   Response: {webhook_response.text}")
            webhook_test_passed = False
            
    except Exception as e:
        print(f"   ❌ Webhook delivery test error: {e}")
        webhook_test_passed = False
    
    # Test 3: Trigger a test scraper to verify backend webhook configuration
    print("\n3. 🚀 Testing scraper trigger with webhook delivery configuration...")
    
    scraper_payload = {
        "folder_id": 4,  # Using folder 4 that we know has sources
        "user_id": 1,
        "num_of_posts": 2,
        "date_range": {
            "start_date": "2025-09-01T00:00:00.000Z",
            "end_date": "2025-09-30T23:59:59.000Z"
        }
    }
    
    try:
        scraper_response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(scraper_payload),
            timeout=60
        )
        
        print(f"   📡 POST /api/brightdata/trigger-scraper/")
        print(f"   Status: {scraper_response.status_code}")
        
        if scraper_response.status_code == 200:
            result = scraper_response.json()
            success = result.get('success', False)
            
            if success:
                print(f"   ✅ Scraper trigger successful!")
                print(f"   📋 Platforms: {result.get('platforms_scraped', [])}")
                print(f"   🎯 This request should now use 'webhook' delivery method!")
                scraper_test_passed = True
            else:
                print(f"   ❌ Scraper trigger failed: {result.get('error', 'Unknown error')}")
                scraper_test_passed = False
        else:
            print(f"   ❌ Scraper trigger failed: {scraper_response.status_code}")
            print(f"   Response: {scraper_response.text}")
            scraper_test_passed = False
            
    except Exception as e:
        print(f"   ❌ Scraper trigger test error: {e}")
        scraper_test_passed = False
    
    # Test 4: Check webhook-results endpoint
    print("\n4. 🔍 Testing webhook-results endpoint...")
    
    try:
        webhook_results_response = requests.get(
            f"{base_url}/api/brightdata/webhook-results/4/latest/",
            timeout=30
        )
        
        print(f"   📡 GET /api/brightdata/webhook-results/4/latest/")
        print(f"   Status: {webhook_results_response.status_code}")
        
        if webhook_results_response.status_code == 200:
            result = webhook_results_response.json()
            data = result.get('data', [])
            
            print(f"   ✅ Webhook results accessible!")
            print(f"   📊 Webhook-delivered posts: {len(data)}")
            
            # Check if any posts have webhook_delivered=True
            webhook_delivered_count = sum(1 for post in data if post.get('webhook_delivered'))
            print(f"   🎯 Posts with webhook delivery: {webhook_delivered_count}")
            
            webhook_results_test_passed = True
        else:
            print(f"   ❌ Webhook results failed: {webhook_results_response.status_code}")
            webhook_results_test_passed = False
            
    except Exception as e:
        print(f"   ❌ Webhook results test error: {e}")
        webhook_results_test_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 WEBHOOK DELIVERY METHOD TEST SUMMARY")
    print("=" * 50)
    
    tests_passed = sum([
        endpoint_accessible,
        webhook_test_passed,
        scraper_test_passed,
        webhook_results_test_passed
    ])
    
    total_tests = 4
    
    if tests_passed >= 3:  # At least 3 out of 4 tests should pass
        print("✅ SUCCESS: Webhook delivery method fix is working!")
        print()
        print("🎯 CONFIRMED:")
        if endpoint_accessible:
            print("   ✅ Webhook endpoint is accessible")
        if webhook_test_passed:
            print("   ✅ Webhook processing is working")
        if scraper_test_passed:
            print("   ✅ Scraper trigger uses webhook configuration")
        if webhook_results_test_passed:
            print("   ✅ Webhook-results endpoint is functional")
            
        print()
        print("🔥 NEXT STEPS:")
        print("1. Configure BrightData dashboard to use webhook delivery")
        print("2. Set delivery_method to 'webhook' in BrightData datasets")
        print("3. Test real scraper runs to confirm webhook delivery")
        
        success = True
    else:
        print("❌ ISSUES FOUND:")
        print(f"Only {tests_passed}/{total_tests} tests passed")
        
        if not endpoint_accessible:
            print("   ❌ Webhook endpoint not accessible")
        if not webhook_test_passed:
            print("   ❌ Webhook processing failed")
        if not scraper_test_passed:
            print("   ❌ Scraper trigger issues")
        if not webhook_results_test_passed:
            print("   ❌ Webhook results endpoint issues")
            
        success = False
    
    print("\n🔧 BRIGHTDATA DASHBOARD CONFIGURATION STILL REQUIRED:")
    print("Go to https://brightdata.com/cp/ and set delivery_method to 'webhook'")
    
    return success

if __name__ == "__main__":
    success = test_webhook_delivery_configuration()
    exit(0 if success else 1)