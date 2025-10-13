#!/usr/bin/env python3
"""
🚀 TEST PRODUCTION WEBHOOK AFTER REDEPLOY
Test BrightData with corrected webhook configuration in production
"""

import requests
import json
import time

def test_production_brightdata_trigger():
    """Test production BrightData trigger with corrected webhook"""
    
    print("🚀 TESTING PRODUCTION BRIGHTDATA WITH CORRECTED WEBHOOK")
    print("=" * 60)
    
    # Production API endpoint
    base_url = "https://trackfutura.futureobjects.io"
    trigger_url = f"{base_url}/api/brightdata/trigger-system/"
    
    # Test trigger for folder 4
    payload = {
        "folder_id": 4,
        "num_of_posts": 5,
        "date_range": {
            "start_date": "01-09-2025",
            "end_date": "05-09-2025"
        }
    }
    
    print("📡 Production API Test:")
    print(f"   URL: {trigger_url}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        print("⏱️ Making production API request...")
        response = requests.post(trigger_url, json=payload, timeout=60)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Production trigger successful!")
                print("📊 Trigger result:")
                print(json.dumps(result, indent=2))
                
                # Extract snapshot IDs
                snapshot_ids = []
                if result.get('results'):
                    for platform, platform_result in result['results'].items():
                        snapshot_id = platform_result.get('snapshot_id') or platform_result.get('job_id')
                        if snapshot_id:
                            snapshot_ids.append((platform, snapshot_id))
                
                return True, snapshot_ids
                
            except json.JSONDecodeError:
                print("✅ Success but non-JSON response")
                return True, []
        else:
            print(f"❌ Production trigger failed: {response.status_code}")
            return False, []
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False, []

def check_snapshot_webhook_delivery(platform, snapshot_id):
    """Check if snapshot uses webhook delivery"""
    
    print(f"🔍 Checking webhook delivery for {platform} snapshot: {snapshot_id}")
    
    url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    headers = {
        "Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            delivery_method = data.get('delivery_method', 'unknown')
            endpoint = data.get('endpoint')
            
            print(f"   📊 {platform} snapshot {snapshot_id}:")
            print(f"      delivery_method: {delivery_method}")
            print(f"      endpoint: {endpoint}")
            
            if delivery_method == 'webhook':
                print(f"   ✅ {platform}: WEBHOOK DELIVERY CONFIRMED!")
                return True
            else:
                print(f"   ❌ {platform}: Still not webhook ({delivery_method})")
                return False
                
        elif response.status_code == 202:
            print(f"   ⏳ {platform} snapshot still running...")
            return None
        else:
            print(f"   ❌ {platform}: Error {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ {platform}: Exception {str(e)}")
        return False

def test_manual_brightdata_trigger():
    """Test direct BrightData trigger with corrected webhook format"""
    
    print("🔧 TESTING DIRECT BRIGHTDATA WITH CORRECTED FORMAT")
    print("=" * 60)
    
    url = "https://api.brightdata.com/datasets/v3/trigger"
    
    headers = {
        "Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
        "Content-Type": "application/json",
    }
    
    # CORRECTED webhook parameters format
    params = {
        "dataset_id": "gd_lk5ns7kz21pck8jpis",  # Instagram
        "endpoint": "https://trackfutura.futureobjects.io/api/brightdata/webhook/",
        "auth_header": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
        "format": "json",
        "uncompressed_webhook": "true",
        "include_errors": "true",
        "type": "discover_new",
        "discover_by": "url",
    }
    
    # Test with NIKE account
    data = [
        {
            "url": "https://instagram.com/nike/",
            "num_of_posts": 3,
            "start_date": "01-09-2025",
            "end_date": "03-09-2025",
            "post_type": "Post"
        }
    ]
    
    try:
        print("⏱️ Direct BrightData API call...")
        response = requests.post(url, headers=headers, params=params, json=data, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            snapshot_id = result.get('snapshot_id')
            
            print(f"✅ Direct trigger successful!")
            print(f"🆔 Snapshot ID: {snapshot_id}")
            
            return True, snapshot_id
        else:
            print(f"❌ Direct trigger failed: {response.status_code} - {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False, None

if __name__ == "__main__":
    print("🔥 COMPREHENSIVE WEBHOOK DELIVERY TEST")
    print("=" * 80)
    
    # Test 1: Production API
    print("\n📍 TEST 1: Production API with corrected webhook")
    prod_success, prod_snapshots = test_production_brightdata_trigger()
    
    # Test 2: Direct API
    print("\n📍 TEST 2: Direct BrightData API with corrected webhook")
    direct_success, direct_snapshot = test_manual_brightdata_trigger()
    
    # Collect all snapshots to check
    all_snapshots = []
    
    if prod_snapshots:
        all_snapshots.extend(prod_snapshots)
    
    if direct_snapshot:
        all_snapshots.append(('direct_instagram', direct_snapshot))
    
    # Wait a bit for snapshots to be processed
    if all_snapshots:
        print(f"\n⏳ Waiting 30 seconds for {len(all_snapshots)} snapshots to initialize...")
        time.sleep(30)
        
        print("\n📍 TEST 3: Verify webhook delivery method in snapshots")
        webhook_confirmed = 0
        
        for platform, snapshot_id in all_snapshots:
            result = check_snapshot_webhook_delivery(platform, snapshot_id)
            if result is True:
                webhook_confirmed += 1
    
    # Final summary
    print("\n" + "=" * 80)
    print("🏁 FINAL WEBHOOK DELIVERY TEST RESULTS:")
    
    if prod_success:
        print("✅ Production API trigger successful")
    else:
        print("❌ Production API trigger failed")
    
    if direct_success:
        print("✅ Direct BrightData API trigger successful")
    else:
        print("❌ Direct BrightData API trigger failed")
    
    if 'webhook_confirmed' in locals() and webhook_confirmed > 0:
        print(f"✅ {webhook_confirmed}/{len(all_snapshots)} snapshots confirmed webhook delivery!")
        print("🎉 WEBHOOK DELIVERY METHOD FIXED!")
        print("🚀 Ready for production use!")
    elif 'all_snapshots' in locals() and len(all_snapshots) > 0:
        print("❌ Snapshots created but webhook delivery not confirmed")
        print("🔧 May need to check snapshots later when they complete")
    else:
        print("❌ No snapshots created to verify")
        print("🔧 Need to investigate trigger issues")
        
    print("\n💡 Next steps:")
    print("1. ✅ Webhook configuration format corrected in services.py")
    print("2. ✅ Django application redeployed to production") 
    print("3. 🔍 Monitor snapshot delivery methods to confirm webhook delivery")
    print("4. 🎯 Test folder 4 sources to ensure they work with webhook delivery")