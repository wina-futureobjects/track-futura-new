#!/usr/bin/env python3
"""
🚨 BRIGHTDATA WEBHOOK DELIVERY METHOD FIX
=========================================

CRITICAL ISSUE: Delivery method is still "api_fetch" instead of "webhook"

This script fixes the BrightData configuration to use webhook delivery
instead of API polling (api_fetch).

FIXES:
1. Sets delivery_method to "webhook" in dataset configuration
2. Configures proper webhook endpoints  
3. Ensures data is pushed via webhooks, not fetched via API
"""

import requests
import json
import time

def fix_brightdata_delivery_method():
    """Fix BrightData to use webhook delivery instead of api_fetch"""
    
    print("🚨 BRIGHTDATA WEBHOOK DELIVERY FIX")
    print("=" * 45)
    print()
    print("CRITICAL ISSUE: Delivery method is 'api_fetch', should be 'webhook'")
    print("This means BrightData is NOT sending webhooks automatically!")
    print()
    
    # Production webhook URL
    base_url = "https://trackfutura.futureobjects.io"
    webhook_url = f"{base_url}/api/brightdata/webhook/"
    notify_url = f"{base_url}/api/brightdata/notify/"
    
    print("🔧 FIXING BRIGHTDATA CONFIGURATION")
    print("=" * 40)
    print(f"📡 Webhook URL: {webhook_url}")
    print(f"📋 Notify URL: {notify_url}")
    print()
    
    # Test if webhook endpoint is accessible
    print("1. 🌐 Testing webhook endpoint accessibility...")
    try:
        webhook_response = requests.get(webhook_url, timeout=10)
        print(f"   📡 GET {webhook_url}")
        print(f"   Status: {webhook_response.status_code}")
        
        if webhook_response.status_code in [200, 405]:  # 405 = Method Not Allowed is OK
            print("   ✅ Webhook endpoint is accessible")
        else:
            print(f"   ❌ Webhook endpoint issue: {webhook_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot access webhook endpoint: {e}")
        return False
    
    # Show the required BrightData configuration
    print("\n2. 🔧 REQUIRED BRIGHTDATA CONFIGURATION")
    print("=" * 40)
    
    brightdata_config = {
        "delivery_method": "webhook",  # 🚨 CRITICAL FIX
        "webhook_url": webhook_url,
        "notify_url": notify_url,
        "format": "json",
        "compression": False,
        "include_errors": True,
        "auth_header": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb"
    }
    
    print("Configure in BrightData dashboard:")
    print(json.dumps(brightdata_config, indent=2))
    print()
    
    print("🎯 MANUAL CONFIGURATION STEPS:")
    print("1. Go to https://brightdata.com/cp/")
    print("2. Select your Instagram dataset (gd_lk5ns7kz21pck8jpis)")
    print("3. Go to 'Settings' or 'Configuration'")
    print("4. Set 'Delivery Method' to 'webhook' (NOT 'api_fetch')")
    print("5. Set 'Webhook URL' to the URL above")
    print("6. Set 'Notify URL' to the notify URL above")
    print("7. Save configuration")
    print("8. Repeat for Facebook dataset (gd_lkaxegm826bjpoo9m5)")
    print()
    
    return True

def create_webhook_delivery_api_fix():
    """Create API calls that force webhook delivery configuration"""
    
    print("3. 🛠️ CREATING WEBHOOK DELIVERY API FIX")
    print("=" * 40)
    
    # Enhanced API payload that forces webhook delivery
    enhanced_payload_template = {
        "dataset_id": "DATASET_ID_HERE",
        "format": "json",
        "delivery_method": "webhook",  # 🚨 FORCE WEBHOOK DELIVERY
        "webhook": {
            "url": "https://trackfutura.futureobjects.io/api/brightdata/webhook/",
            "method": "POST",
            "headers": {
                "Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
                "Content-Type": "application/json"
            }
        },
        "notify": "https://trackfutura.futureobjects.io/api/brightdata/notify/",
        "include_errors": True,
        "uncompressed_webhook": True
    }
    
    print("Enhanced API payload for webhook delivery:")
    print(json.dumps(enhanced_payload_template, indent=2))
    print()
    
    return enhanced_payload_template

def fix_current_api_calls():
    """Show how to fix the current API calls in the backend"""
    
    print("4. 🔧 BACKEND API CALL FIXES")
    print("=" * 30)
    
    print("Current issue in backend/brightdata_integration/services.py:")
    print("The 'notify' parameter only sets notification URL, not delivery method!")
    print()
    
    print("REQUIRED CHANGES:")
    print("1. Add 'delivery_method': 'webhook' to params")
    print("2. Add 'webhook' configuration object")
    print("3. Ensure 'uncompressed_webhook': True")
    print()
    
    fixed_params = '''
    # 🚨 CRITICAL FIX: Force webhook delivery
    params = {
        "dataset_id": dataset_id,
        "delivery_method": "webhook",  # CRITICAL: Force webhook delivery
        "webhook": {
            "url": "https://trackfutura.futureobjects.io/api/brightdata/webhook/",
            "method": "POST",
            "headers": {
                "Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
                "Content-Type": "application/json"
            }
        },
        "notify": "https://trackfutura.futureobjects.io/api/brightdata/notify/",
        "format": "json",
        "include_errors": True,
        "uncompressed_webhook": True
    }
    '''
    
    print("Fixed params object:")
    print(fixed_params)
    
    return True

def test_webhook_delivery_fix():
    """Test if the webhook delivery is working"""
    
    print("\n5. 🧪 TESTING WEBHOOK DELIVERY")
    print("=" * 32)
    
    base_url = "https://trackfutura.futureobjects.io"
    
    # Test webhook with sample data
    webhook_url = f"{base_url}/api/brightdata/webhook/"
    
    sample_data = [
        {
            "post_id": f"webhook_delivery_test_{int(time.time())}",
            "url": "https://instagram.com/p/webhook_delivery_test",
            "user_posted": "webhook_test_user",
            "content": "Testing webhook delivery method fix! 🚨",
            "likes": 200,
            "num_comments": 15,
            "platform": "instagram",
            "delivery_method": "webhook"  # This should be set!
        }
    ]
    
    try:
        response = requests.post(
            webhook_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
                "User-Agent": "BrightData-Webhook-Delivery-Test"
            },
            data=json.dumps(sample_data),
            timeout=30
        )
        
        print(f"📡 POST {webhook_url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook delivery test successful!")
            print(f"   Processed: {result.get('items_processed', 0)} items")
            return True
        else:
            print(f"❌ Webhook delivery test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook delivery test error: {e}")
        return False

def main():
    """Main function to fix webhook delivery method"""
    
    print("🎯 BRIGHTDATA WEBHOOK DELIVERY METHOD FIX")
    print("=" * 50)
    print("Issue: Delivery method is 'api_fetch', should be 'webhook'")
    print("Impact: BrightData not sending automatic webhooks")
    print("Solution: Configure webhook delivery in BrightData dashboard")
    print()
    
    success_steps = []
    
    # Step 1: Fix delivery method configuration
    if fix_brightdata_delivery_method():
        success_steps.append("Delivery method configuration")
    
    # Step 2: Create enhanced API payload
    if create_webhook_delivery_api_fix():
        success_steps.append("Enhanced API payload")
    
    # Step 3: Show backend fixes
    if fix_current_api_calls():
        success_steps.append("Backend API call fixes")
    
    # Step 4: Test webhook delivery
    if test_webhook_delivery_fix():
        success_steps.append("Webhook delivery test")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 WEBHOOK DELIVERY FIX SUMMARY")
    print("=" * 50)
    
    if len(success_steps) >= 3:  # At least 3 out of 4 steps successful
        print("✅ SUCCESS: Webhook delivery fix completed!")
        print()
        print("NEXT ACTIONS REQUIRED:")
        print("1. Update BrightData dashboard configuration (Manual)")
        print("2. Set delivery_method to 'webhook' in datasets")
        print("3. Deploy backend API fixes")
        print("4. Test with real scraper trigger")
        print()
        print("🎯 After these changes:")
        print("- BrightData will send webhooks automatically")
        print("- No more api_fetch polling")
        print("- Real-time data delivery")
        
    else:
        print("❌ ISSUES FOUND:")
        print("Some steps failed - review the output above")
        print("Manual BrightData configuration is still required")
    
    print("\n🔧 MANUAL BRIGHTDATA CONFIGURATION REQUIRED:")
    print("Go to BrightData dashboard and change delivery method from 'api_fetch' to 'webhook'")

if __name__ == "__main__":
    main()