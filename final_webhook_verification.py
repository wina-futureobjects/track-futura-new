#!/usr/bin/env python3
"""
🔍 CHECK NOTIFY SNAPSHOT DELIVERY METHOD
Verify if notify configuration produces webhook delivery
"""

import requests
import json
import time

def check_notify_snapshot_delivery():
    """Check the delivery method of the notify-created snapshot"""
    
    snapshot_id = "s_mgp1k8nz8zw0nqf4y"
    
    print(f"🔍 CHECKING NOTIFY SNAPSHOT DELIVERY METHOD")
    print(f"Snapshot ID: {snapshot_id}")
    print("=" * 60)
    
    url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    headers = {
        "Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            delivery_method = data.get('delivery_method')
            notify_url = data.get('notify_url')
            webhook_url = data.get('webhook_url') 
            endpoint = data.get('endpoint')
            status = data.get('status')
            
            print(f"📄 Snapshot Details:")
            print(f"   Status: {status}")
            print(f"   Delivery Method: {delivery_method}")
            print(f"   Notify URL: {notify_url}")
            print(f"   Webhook URL: {webhook_url}")
            print(f"   Endpoint: {endpoint}")
            
            if delivery_method == 'webhook':
                print(f"🎉 SUCCESS! NOTIFY configuration produces WEBHOOK delivery!")
                return True
            else:
                print(f"❌ Notify produces: {delivery_method}")
                
                # Show full data for analysis
                print(f"\n📄 Full snapshot data:")
                print(json.dumps(data, indent=2))
                return False
                
        elif response.status_code == 202:
            print(f"⏳ Snapshot still processing...")
            return None
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_correct_webhook_format():
    """Test the absolutely correct webhook format based on findings"""
    
    print(f"\n🔧 TESTING CORRECTED WEBHOOK FORMAT")
    print("=" * 60)
    
    url = "https://api.brightdata.com/datasets/v3/trigger"
    
    headers = {
        "Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
        "Content-Type": "application/json",
    }
    
    # Based on your original example - this should be the EXACT format
    params = {
        "dataset_id": "gd_lk5ns7kz21pck8jpis",
        "endpoint": "https://trackfutura.futureobjects.io/api/brightdata/webhook/",
        "auth_header": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb", 
        "format": "json",
        "uncompressed_webhook": "true",
        "include_errors": "true",
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
    
    print(f"🚀 Testing EXACT webhook format from your example...")
    
    try:
        response = requests.post(url, headers=headers, params=params, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            snapshot_id = result.get('snapshot_id')
            
            print(f"✅ Webhook format accepted!")
            print(f"🆔 Snapshot ID: {snapshot_id}")
            
            # Wait and check delivery method
            print(f"⏳ Waiting 15 seconds to check delivery method...")
            time.sleep(15)
            
            return check_snapshot_delivery_method(snapshot_id)
        else:
            print(f"❌ Webhook format rejected: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def check_snapshot_delivery_method(snapshot_id):
    """Check delivery method of a specific snapshot"""
    
    url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    headers = {
        "Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            delivery_method = data.get('delivery_method')
            
            print(f"📊 Snapshot {snapshot_id} delivery method: {delivery_method}")
            
            if delivery_method == 'webhook':
                print(f"🎉 WEBHOOK DELIVERY CONFIRMED!")
                return True
            else:
                print(f"❌ Not webhook: {delivery_method}")
                return False
        else:
            print(f"⚠️ Cannot check yet: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def update_services_with_notify():
    """Show how to update services.py to use notify for guaranteed delivery"""
    
    print(f"\n📝 BACKUP SOLUTION: USE NOTIFY CONFIGURATION")
    print("=" * 60)
    
    print(f"If webhook delivery continues to be problematic, update services.py:")
    print(f"")
    print(f"# WORKING NOTIFY CONFIGURATION:")
    print(f'params = {{')
    print(f'    "dataset_id": dataset_id,')
    print(f'    "notify": "https://trackfutura.futureobjects.io/api/brightdata/notify/",')
    print(f'    "format": "json",')
    print(f'    "type": "discover_new",')
    print(f'    "discover_by": "url",')
    print(f'}}')
    print(f"")
    print(f"This is CONFIRMED WORKING and creates snapshots successfully!")

if __name__ == "__main__":
    print("🔍 FINAL WEBHOOK DELIVERY METHOD VERIFICATION")
    print("=" * 80)
    
    # Check the notify snapshot delivery method
    notify_result = check_notify_snapshot_delivery()
    
    # Test the corrected webhook format one more time
    webhook_result = test_correct_webhook_format()
    
    # Show backup solution
    update_services_with_notify()
    
    print("\n" + "=" * 80)
    print("🏁 FINAL WEBHOOK DELIVERY ANALYSIS:")
    
    if notify_result is True:
        print("✅ NOTIFY configuration produces WEBHOOK delivery!")
        print("🎯 SOLUTION: Use notify parameter instead of endpoint")
    elif webhook_result is True:
        print("✅ ENDPOINT configuration produces WEBHOOK delivery!")
        print("🎯 SOLUTION: Webhook format is now correct")
    else:
        print("❌ Neither configuration produces webhook delivery")
        print("🔧 ISSUE: BrightData may not support webhook delivery for this account/dataset")
        
    print(f"\n💡 RECOMMENDATION:")
    if notify_result is True:
        print("Use the NOTIFY configuration in services.py - it works perfectly!")
        print("The 'notify' parameter delivers to your webhook endpoint successfully.")
    else:
        print("Continue troubleshooting webhook delivery with BrightData support")
        print("The notify endpoint works as a backup delivery method")