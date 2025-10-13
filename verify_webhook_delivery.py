#!/usr/bin/env python3
"""
🔍 VERIFY WEBHOOK DELIVERY METHOD
Check if the snapshot now shows proper webhook delivery
"""

import requests
import json
import time

def check_snapshot_delivery_method(snapshot_id):
    """Check if snapshot shows webhook delivery method"""
    
    print(f"🔍 CHECKING WEBHOOK DELIVERY FOR SNAPSHOT: {snapshot_id}")
    print("=" * 60)
    
    # BrightData snapshot info endpoint
    url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    
    headers = {
        "Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📡 Getting snapshot info from: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                print("✅ Snapshot data retrieved!")
                print("📄 Full snapshot info:")
                print(json.dumps(data, indent=2))
                
                # Look for delivery method information
                delivery_method = data.get('delivery_method')
                delivery_config = data.get('delivery_config', {})
                endpoint = data.get('endpoint')
                
                print("\n🔍 DELIVERY METHOD ANALYSIS:")
                print(f"   delivery_method: {delivery_method}")
                print(f"   endpoint: {endpoint}")
                print(f"   delivery_config: {delivery_config}")
                
                if delivery_method == 'webhook':
                    print("🎉 SUCCESS! Delivery method is now 'webhook'!")
                    return True
                elif delivery_method == 'not_specified':
                    print("❌ Still shows 'not_specified' - webhook config may not have taken effect")
                    return False
                else:
                    print(f"⚠️ Unexpected delivery method: {delivery_method}")
                    return False
                    
            except json.JSONDecodeError:
                print(f"📄 Non-JSON response: {response.text}")
                return False
        else:
            print(f"❌ Failed to get snapshot info: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_system_trigger_with_corrected_webhook():
    """Test the system trigger with corrected webhook configuration"""
    
    print("🚀 TESTING SYSTEM TRIGGER WITH CORRECTED WEBHOOK")
    print("=" * 60)
    
    try:
        # Import Django and set up
        import os
        import sys
        import django
        
        # Add the project directory to Python path
        project_root = os.path.dirname(os.path.abspath(__file__))
        backend_path = os.path.join(project_root, 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'track_futura_backend.settings')
        django.setup()
        
        # Now import the service
        from brightdata_integration.services import BrightDataAutomatedBatchScraper
        
        # Test with folder 4 (should have sources now)
        scraper = BrightDataAutomatedBatchScraper()
        
        print("🎯 Testing system trigger with folder 4...")
        result = scraper.trigger_scraper_from_system(
            folder_id=4,
            num_of_posts=5
        )
        
        print("📊 System trigger result:")
        print(json.dumps(result, indent=2, default=str))
        
        if result.get('success'):
            print("✅ System trigger successful!")
            
            # Get snapshot ID from results
            snapshot_ids = []
            for platform, platform_result in result.get('results', {}).items():
                snapshot_id = platform_result.get('snapshot_id')
                if snapshot_id:
                    snapshot_ids.append(snapshot_id)
                    print(f"📊 {platform} snapshot: {snapshot_id}")
            
            # Check webhook delivery for each snapshot
            for snapshot_id in snapshot_ids:
                print(f"\n🔍 Checking webhook delivery for {snapshot_id}...")
                time.sleep(2)  # Brief pause
                is_webhook = check_snapshot_delivery_method(snapshot_id)
                if is_webhook:
                    print(f"🎉 {snapshot_id}: WEBHOOK DELIVERY CONFIRMED!")
                else:
                    print(f"❌ {snapshot_id}: Still not using webhook delivery")
            
            return len(snapshot_ids) > 0
        else:
            print(f"❌ System trigger failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception in system test: {str(e)}")
        return False

if __name__ == "__main__":
    # First check the test snapshot
    print("STEP 1: Check test snapshot delivery method")
    test_snapshot_id = "s_mgp01jm81nghsq5pha"
    is_webhook = check_snapshot_delivery_method(test_snapshot_id)
    
    print("\n" + "=" * 60)
    
    # Then test with system trigger
    print("STEP 2: Test system trigger with corrected webhook")
    system_success = test_system_trigger_with_corrected_webhook()
    
    print("\n" + "=" * 60)
    print("🏁 FINAL RESULTS:")
    
    if is_webhook:
        print("✅ Test snapshot shows webhook delivery method!")
    else:
        print("❌ Test snapshot still shows incorrect delivery method")
        
    if system_success:
        print("✅ System trigger worked with corrected webhook!")
    else:
        print("❌ System trigger still has issues")
        
    if is_webhook and system_success:
        print("🎉 WEBHOOK DELIVERY COMPLETELY FIXED!")
        print("🚀 Deploy the updated services.py to production!")
    else:
        print("🔧 Still need to investigate remaining issues")