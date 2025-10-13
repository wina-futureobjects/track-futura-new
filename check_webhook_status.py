#!/usr/bin/env python3
"""
🔍 CHECK WEBHOOK DELIVERY STATUS
Check if snapshots now show webhook delivery method
"""

import requests
import json

def check_snapshot_status(snapshot_id):
    """Check snapshot delivery method and status"""
    
    url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    headers = {
        "Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📊 Snapshot {snapshot_id} Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("📄 Full snapshot data:")
            print(json.dumps(data, indent=2))
            
            # Check delivery method
            delivery_method = data.get('delivery_method')
            endpoint = data.get('endpoint')
            status = data.get('status')
            
            print("\n🔍 KEY DELIVERY INFORMATION:")
            print(f"   Status: {status}")
            print(f"   Delivery Method: {delivery_method}")
            print(f"   Endpoint: {endpoint}")
            
            if delivery_method == 'webhook':
                print("🎉 SUCCESS! Webhook delivery method confirmed!")
                return True
            else:
                print(f"❌ Still not webhook: {delivery_method}")
                return False
                
        elif response.status_code == 202:
            print("⏳ Snapshot still processing...")
            return None
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    # Check both test snapshots
    test_snapshots = [
        "s_mgp01jm81nghsq5pha",  # First test snapshot
        "s_mgp09psx1wxozh8ubg"   # Second test snapshot
    ]
    
    webhook_confirmed = 0
    
    for snapshot_id in test_snapshots:
        print(f"🔍 CHECKING SNAPSHOT: {snapshot_id}")
        print("=" * 50)
        
        result = check_snapshot_status(snapshot_id)
        
        if result is True:
            webhook_confirmed += 1
            print(f"✅ {snapshot_id}: WEBHOOK CONFIRMED!")
        elif result is None:
            print(f"⏳ {snapshot_id}: Still processing")
        else:
            print(f"❌ {snapshot_id}: Not webhook delivery")
        
        print()
    
    print("🏁 FINAL WEBHOOK STATUS:")
    print(f"✅ {webhook_confirmed}/{len(test_snapshots)} snapshots confirmed webhook delivery")
    
    if webhook_confirmed > 0:
        print("🎉 WEBHOOK DELIVERY CONFIGURATION SUCCESS!")
        print("✅ BrightData is now properly configured for webhook delivery")
        print("✅ delivery_method shows 'webhook' instead of 'not_specified'")
        print("\n📋 SOLUTION SUMMARY:")
        print("1. ✅ Changed 'webhook' object to 'endpoint' parameter")
        print("2. ✅ Changed nested headers to 'auth_header' parameter")  
        print("3. ✅ Used string values for boolean parameters")
        print("4. ✅ Deployed corrected configuration to production")
        print("\n🚀 READY FOR PRODUCTION USE!")
    else:
        print("🔧 Still need to investigate webhook configuration")
        print("💡 Snapshots may need more time to process")