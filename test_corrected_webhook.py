#!/usr/bin/env python3
"""
🚀 TEST CORRECTED WEBHOOK CONFIGURATION
Tests the updated BrightData webhook parameters format
"""

import requests
import json

def test_corrected_webhook():
    """Test the corrected webhook configuration format"""
    
    print("🚀 TESTING CORRECTED BRIGHTDATA WEBHOOK CONFIGURATION")
    print("=" * 60)
    
    # BrightData API configuration - CORRECTED FORMAT
    url = "https://api.brightdata.com/datasets/v3/trigger"
    
    headers = {
        "Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
        "Content-Type": "application/json",
    }
    
    # CORRECTED parameters format (matching your example)
    params = {
        "dataset_id": "gd_lk5ns7kz21pck8jpis",  # Instagram dataset
        "endpoint": "https://trackfutura.futureobjects.io/api/brightdata/webhook/",
        "auth_header": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
        "format": "json",
        "uncompressed_webhook": "true",
        "include_errors": "true",
        "type": "discover_new",
        "discover_by": "url",
    }
    
    # Test data (using NIKE Instagram as test)
    data = [
        {
            "url": "https://instagram.com/nike/",
            "num_of_posts": 5,
            "start_date": "01-09-2025",
            "end_date": "05-09-2025",
            "post_type": "Post"
        }
    ]
    
    print("🔧 CORRECTED WEBHOOK CONFIGURATION:")
    print(f"   Endpoint: {params['endpoint']}")
    print(f"   Auth Header: {params['auth_header']}")
    print(f"   Format: {params['format']}")
    print(f"   Uncompressed: {params['uncompressed_webhook']}")
    print()
    
    print("📋 REQUEST DETAILS:")
    print(f"   URL: {url}")
    print(f"   Headers: {headers}")
    print(f"   Params: {json.dumps(params, indent=2)}")
    print(f"   Data: {json.dumps(data, indent=2)}")
    print()
    
    try:
        print("⏱️ Making API request...")
        response = requests.post(url, headers=headers, params=params, json=data, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                snapshot_id = response_data.get('snapshot_id', 'No snapshot_id found')
                
                print("✅ SUCCESS! BrightData accepted the corrected webhook configuration!")
                print(f"🆔 Snapshot ID: {snapshot_id}")
                print()
                print("🔍 WEBHOOK DELIVERY TEST:")
                print("   The snapshot should now show delivery_method: 'webhook'")
                print("   Instead of delivery_method: 'not_specified'")
                print()
                print(f"📊 Monitor progress: https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}")
                
                return True, snapshot_id
                
            except json.JSONDecodeError:
                print("✅ SUCCESS! (Non-JSON response but accepted)")
                return True, None
                
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False, None

if __name__ == "__main__":
    success, snapshot_id = test_corrected_webhook()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 WEBHOOK CONFIGURATION CORRECTED!")
        print("✅ BrightData should now deliver results via webhook")
        print("✅ delivery_method should show 'webhook' instead of 'not_specified'")
        
        if snapshot_id:
            print(f"🔍 Check snapshot {snapshot_id} for webhook delivery method")
    else:
        print("\n" + "=" * 60)
        print("❌ Still issues with webhook configuration")
        print("🔧 May need further adjustments")