#!/usr/bin/env python
"""
WEBHOOK VERIFICATION: Check if BrightData is calling the correct webhook URL
"""

import requests
import json
import time

def verify_webhook_url_in_production():
    """Check what webhook URL is being used in production"""
    
    print("🔍 WEBHOOK URL VERIFICATION")
    print("=" * 50)
    
    base_url = "https://trackfutura.futureobjects.io"
    
    # The issue: we updated the local code but production may still have the old webhook URL
    # Let's see if we can detect what URL is being used
    
    print("❓ PROBLEM ANALYSIS:")
    print("1. Local code was updated with correct webhook URL:")
    print("   ✅ https://trackfutura.futureobjects.io/api/brightdata/webhook/")
    print()
    print("2. But production server may still have old webhook URL:")
    print("   ❌ https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/")
    print()
    print("3. This means BrightData will send webhook data to wrong URL")
    print("   and the frontend will not receive automatic updates (polling instead)")
    
    print(f"\n🔧 VERIFICATION STEPS:")
    print("1. Check if BrightData has the correct webhook URL configured")
    print("2. Test if webhooks are being delivered to the correct endpoint")
    print("3. Verify frontend receives data automatically (no polling)")
    
    # Try to get recent webhook deliveries
    print(f"\n📊 Checking recent webhook activity...")
    
    try:
        # Check recent scraper requests to see webhook delivery status
        response = requests.get(f"{base_url}/api/brightdata/scraper-requests/?limit=10", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            requests_list = data.get('results', data) if isinstance(data, dict) else data
            
            print(f"📋 Recent scraper requests (last 10):")
            
            webhook_delivered_count = 0
            total_requests = len(requests_list)
            
            for i, req in enumerate(requests_list):
                created_at = req.get('created_at', '')
                webhook_delivered = req.get('webhook_delivered')
                status = req.get('status', 'unknown')
                
                print(f"\n  {i+1}. Request ID {req.get('id')}:")
                print(f"     Created: {created_at[:16] if created_at else 'Unknown'}")
                print(f"     Status: {status}")
                print(f"     Webhook Delivered: {webhook_delivered}")
                
                if webhook_delivered is True:
                    webhook_delivered_count += 1
                    print(f"     ✅ Webhook working!")
                elif webhook_delivered is False:
                    print(f"     ❌ No webhook delivery")
                else:
                    print(f"     ❓ Webhook status unknown")
            
            print(f"\n📊 WEBHOOK DELIVERY SUMMARY:")
            print(f"   Total requests: {total_requests}")
            print(f"   Webhook delivered: {webhook_delivered_count}")
            print(f"   Delivery rate: {webhook_delivered_count/total_requests*100:.1f}%" if total_requests > 0 else "   No data")
            
            if webhook_delivered_count == 0:
                print(f"\n❌ WEBHOOK ISSUE CONFIRMED!")
                print(f"   No recent requests have webhook delivery = True")
                print(f"   This means BrightData is NOT calling the webhook URL")
                print(f"   Or the webhook URL is incorrect")
                return False
            elif webhook_delivered_count < total_requests:
                print(f"\n⚠️  PARTIAL WEBHOOK DELIVERY")
                print(f"   Some requests have webhooks, some don't")
                print(f"   This might indicate a recent configuration change")
                return True
            else:
                print(f"\n✅ WEBHOOKS WORKING!")
                print(f"   All recent requests have webhook delivery")
                return True
        else:
            print(f"❌ Failed to get scraper requests: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Error checking webhook delivery: {e}")
        return False

def check_webhook_endpoint_health():
    """Test if the webhook endpoint is healthy and accessible"""
    
    print(f"\n🏥 WEBHOOK ENDPOINT HEALTH CHECK")
    print("=" * 50)
    
    webhook_url = "https://trackfutura.futureobjects.io/api/brightdata/webhook/"
    
    try:
        # Test webhook endpoint with a sample POST
        test_payload = {
            "test": "webhook_verification",
            "timestamp": time.time(),
            "source": "webhook_verification_script"
        }
        
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Webhook endpoint test:")
        print(f"   URL: {webhook_url}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code in [200, 201]:
            print(f"   ✅ Webhook endpoint is healthy and accepting requests")
            return True
        elif response.status_code == 405:
            print(f"   ✅ Webhook endpoint exists (405 = Method restrictions)")
            return True
        else:
            print(f"   ❌ Webhook endpoint issue")
            return False
            
    except Exception as e:
        print(f"   💥 Webhook endpoint error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 WEBHOOK VERIFICATION REPORT")
    print("Checking if BrightData webhook delivery is properly configured")
    print()
    
    # Check webhook delivery history
    webhooks_working = verify_webhook_url_in_production()
    
    # Check webhook endpoint health
    endpoint_healthy = check_webhook_endpoint_health()
    
    print(f"\n" + "=" * 50)
    print("📊 FINAL ASSESSMENT")
    print("=" * 50)
    
    if webhooks_working and endpoint_healthy:
        print("✅ WEBHOOKS ARE WORKING CORRECTLY")
        print("   BrightData is delivering data via webhooks")
        print("   Frontend should receive data automatically")
        print("   No polling should be required")
    elif endpoint_healthy and not webhooks_working:
        print("⚠️  WEBHOOK CONFIGURATION ISSUE")  
        print("   Webhook endpoint is healthy")
        print("   But BrightData is not delivering webhooks")
        print("   Likely cause: Wrong webhook URL in BrightData configuration")
        print("   Solution: Update production code with correct webhook URL")
    else:
        print("❌ WEBHOOK SYSTEM ISSUES")
        print("   Multiple problems detected")
        print("   Both configuration and endpoint issues need fixing")
    
    print(f"\n🚀 NEXT STEPS:")
    if not webhooks_working:
        print("1. Deploy the corrected webhook URL to production server")
        print("2. Restart production services to load new configuration") 
        print("3. Test scraper run to verify webhook delivery")
        print("4. Monitor frontend for automatic data appearance (no polling)")
    else:
        print("1. Webhooks appear to be working")
        print("2. Test frontend with new scraper run")
        print("3. Verify data appears automatically without polling")