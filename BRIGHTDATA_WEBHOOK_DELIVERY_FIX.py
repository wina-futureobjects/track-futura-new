#!/usr/bin/env python3
"""
🎯 BRIGHTDATA WEBHOOK DELIVERY METHOD FIX
=========================================

This script helps you properly configure BrightData webhook delivery method
so it shows "WEBHOOK" instead of "-" in your dashboard.

The issue: Delivery method shows "-" instead of "WEBHOOK"
The solution: Proper webhook configuration in scraper settings
"""

import requests
import json

def check_brightdata_webhook_config():
    """Check and fix BrightData webhook configuration"""
    
    print("🔍 BRIGHTDATA WEBHOOK DELIVERY METHOD FIX")
    print("=" * 50)
    
    print("\n❌ PROBLEM IDENTIFIED:")
    print("   Delivery method shows '-' instead of 'WEBHOOK'")
    print("   This means webhook is not properly configured in scraper settings")
    
    print("\n🎯 SOLUTION STEPS:")
    print("=" * 30)
    
    print("\n1. 🌐 GO TO BRIGHTDATA SCRAPER SETTINGS (Not Account Settings)")
    print("   - Login to BrightData dashboard")
    print("   - Select your SCRAPER PROJECT (not account settings)")
    print("   - Look for 'Settings' or 'Configuration' tab")
    
    print("\n2. 📡 FIND WEBHOOK/DELIVERY SETTINGS")
    print("   - Look for 'Delivery method' or 'Output settings'")
    print("   - Find 'Webhook' or 'HTTP callback' option")
    print("   - This is DIFFERENT from account notifications!")
    
    print("\n3. ⚙️ CONFIGURE SCRAPER WEBHOOK")
    print("   - Set delivery method to: WEBHOOK")
    print("   - Set webhook URL to: https://trackfutura.futureobjects.io/api/brightdata/webhook/")
    print("   - Set method to: POST")
    print("   - Set format to: JSON")
    
    print("\n4. ✅ ENABLE WEBHOOK DELIVERY")
    print("   - Toggle ON webhook delivery")
    print("   - Save scraper settings")
    print("   - Status should change from '-' to 'WEBHOOK'")
    
    print("\n🚨 IMPORTANT DISTINCTION:")
    print("=" * 30)
    print("   Account Settings > Notifications = Email/SMS alerts")
    print("   Scraper Settings > Delivery = Data output method")
    print("   You need SCRAPER DELIVERY settings, not account notifications!")
    
    print("\n📋 EXACT SCRAPER WEBHOOK CONFIGURATION:")
    print("=" * 40)
    print("   Delivery Method: WEBHOOK")
    print("   Webhook URL: https://trackfutura.futureobjects.io/api/brightdata/webhook/")
    print("   Method: POST")
    print("   Content-Type: application/json")
    print("   Trigger: Job completion")
    
    # Test the webhook endpoint
    print("\n🧪 TESTING WEBHOOK ENDPOINT:")
    try:
        response = requests.post(
            "https://trackfutura.futureobjects.io/api/brightdata/webhook/",
            json={"test": "webhook_delivery_fix"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"   ✅ Webhook endpoint working: {response.json()}")
        else:
            print(f"   ❌ Webhook issue: Status {response.status_code}")
            
    except Exception as e:
        print(f"   ⚠️ Webhook test error: {e}")
    
    print("\n🎯 NEXT STEPS:")
    print("=" * 20)
    print("1. Go to your BrightData SCRAPER project settings")
    print("2. Set delivery method to WEBHOOK (not just notifications)")
    print("3. Configure webhook URL in scraper delivery settings")
    print("4. Verify delivery method changes from '-' to 'WEBHOOK'")
    print("5. Run a test scraper to confirm automatic delivery")
    
    print("\n🎉 RESULT:")
    print("   Delivery method will show 'WEBHOOK' ✅")
    print("   Data will automatically flow to your dashboard 🚀")

if __name__ == "__main__":
    check_brightdata_webhook_config()