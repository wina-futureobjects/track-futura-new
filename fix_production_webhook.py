#!/usr/bin/env python3
"""
🔧 FIX PRODUCTION DATABASE WEBHOOK ISSUE
Check and fix database permissions and migrations
"""

import requests
import json

def test_webhook_endpoint_directly():
    """Test the webhook endpoint directly to see the actual error"""
    
    print("🔧 TESTING WEBHOOK ENDPOINT DIRECTLY")
    print("=" * 60)
    
    webhook_url = "https://trackfutura.futureobjects.io/api/brightdata/webhook/"
    
    # Test payload similar to what BrightData would send
    test_payload = {
        "snapshot_id": "test_webhook_diagnosis",
        "platform": "instagram",
        "data": [
            {
                "url": "https://instagram.com/test/",
                "post_id": "test123",
                "username": "test_user",
                "caption": "Test webhook delivery",
                "likes_count": 100,
                "comments_count": 10
            }
        ]
    }
    
    headers = {
        "Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"🚀 Testing webhook at: {webhook_url}")
        print(f"📦 Payload: {json.dumps(test_payload, indent=2)}")
        
        response = requests.post(webhook_url, json=test_payload, headers=headers, timeout=30)
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook endpoint is working!")
            return True
        elif response.status_code == 502:
            print("❌ 502 Bad Gateway - Server configuration issue")
            return False
        elif response.status_code == 500:
            print("❌ 500 Internal Server Error - Database/Django error")
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception testing webhook: {str(e)}")
        return False

def check_production_endpoints():
    """Check various production endpoints for health"""
    
    print("\n🔍 CHECKING PRODUCTION ENDPOINTS")
    print("=" * 60)
    
    base_url = "https://trackfutura.futureobjects.io"
    
    endpoints = [
        "/api/",
        "/api/brightdata/",
        "/api/brightdata/webhook/",
        "/admin/",
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        
        try:
            response = requests.get(url, timeout=10)
            print(f"📍 {endpoint}: {response.status_code}")
            
            if response.status_code == 502:
                print(f"   ❌ Bad Gateway - Server not responding properly")
            elif response.status_code == 200:
                print(f"   ✅ OK")
            elif response.status_code == 404:
                print(f"   ⚠️ Not Found (may be normal)")
            elif response.status_code == 403:
                print(f"   ⚠️ Forbidden (may be normal)")
            else:
                print(f"   ❓ Status: {response.status_code}")
                
        except Exception as e:
            print(f"📍 {endpoint}: ❌ Exception - {str(e)}")

def check_upsun_deployment_logs():
    """Get recent deployment logs to identify the issue"""
    
    print("\n📋 DEPLOYMENT STATUS CHECK")
    print("=" * 60)
    
    print("🔍 We need to check:")
    print("1. Django application is running correctly")
    print("2. Database connections are working")  
    print("3. Webhook URL routing is configured")
    print("4. BrightData integration migrations are applied")
    
    print("\n💡 MANUAL CHECKS NEEDED:")
    print("Run these commands in Upsun:")
    print("1. upsun environment:logs -e upsun-deployment --tail")
    print("2. upsun ssh -e upsun-deployment")
    print("3. python manage.py showmigrations brightdata_integration")
    print("4. python manage.py migrate brightdata_integration")

def test_alternative_webhook_config():
    """Try alternative webhook configuration formats"""
    
    print("\n🔧 TESTING ALTERNATIVE WEBHOOK FORMATS")
    print("=" * 60)
    
    url = "https://api.brightdata.com/datasets/v3/trigger"
    
    headers = {
        "Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
        "Content-Type": "application/json",
    }
    
    # Try without webhook at all - use notify instead
    params_notify_only = {
        "dataset_id": "gd_lk5ns7kz21pck8jpis",
        "notify": "https://trackfutura.futureobjects.io/api/brightdata/notify/",
        "format": "json",
        "type": "discover_new", 
        "discover_by": "url",
    }
    
    data = [
        {
            "url": "https://instagram.com/nike/",
            "num_of_posts": 2,
            "start_date": "01-09-2025",
            "end_date": "02-09-2025",
            "post_type": "Post"
        }
    ]
    
    print("🔄 Trying NOTIFY-ONLY configuration (no webhook):")
    print(f"   notify: {params_notify_only['notify']}")
    
    try:
        response = requests.post(url, headers=headers, params=params_notify_only, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            snapshot_id = result.get('snapshot_id')
            
            print(f"✅ Notify-only trigger successful!")
            print(f"🆔 Snapshot ID: {snapshot_id}")
            
            return snapshot_id
        else:
            print(f"❌ Notify-only failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

if __name__ == "__main__":
    print("🔧 PRODUCTION WEBHOOK ISSUE DIAGNOSIS & FIX")
    print("=" * 80)
    
    # Test 1: Direct webhook endpoint test
    webhook_working = test_webhook_endpoint_directly()
    
    # Test 2: Check production endpoints
    check_production_endpoints()
    
    # Test 3: Check deployment status
    check_upsun_deployment_logs()
    
    # Test 4: Try alternative configuration
    notify_snapshot = test_alternative_webhook_config()
    
    print("\n" + "=" * 80)
    print("🏁 PRODUCTION ISSUE DIAGNOSIS COMPLETE")
    
    if not webhook_working:
        print("❌ CRITICAL: Webhook endpoint is not responding properly!")
        print("🚑 IMMEDIATE ACTION REQUIRED:")
        print("1. Check Django application is running in production")
        print("2. Verify database migrations are applied")
        print("3. Check webhook URL routing configuration")
        print("4. Test database connectivity")
        
        print("\n🔧 EMERGENCY FIXES:")
        print("1. Redeploy the application: upsun environment:redeploy")
        print("2. Apply migrations: upsun ssh -> python manage.py migrate")
        print("3. Check logs: upsun environment:logs --tail")
        print("4. Test database: upsun ssh -> python manage.py dbshell")
        
    else:
        print("✅ Webhook endpoint is working - issue may be in configuration")
        
    if notify_snapshot:
        print(f"✅ Alternative notify configuration works: {notify_snapshot}")
        print("💡 Consider using notify instead of webhook temporarily")
    else:
        print("❌ All delivery methods failing - server issue confirmed")
        
    print(f"\n🎯 NEXT ACTION: Fix production server configuration first!")
    print(f"   Then webhook delivery will work properly")