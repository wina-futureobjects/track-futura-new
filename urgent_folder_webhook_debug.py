#!/usr/bin/env python3
"""
🔥 URGENT FOLDER 4 AND WEBHOOK DELIVERY DEBUG
===========================================

Tests both folder 4 issue and webhook delivery configuration in one script.
"""

import requests
import json
import time

def test_folder_4_sources():
    """Test folder 4 sources directly"""
    
    print("🔍 TESTING FOLDER 4 SOURCES")
    print("=" * 40)
    
    # Test 1: Direct API check
    response = requests.get("https://trackfutura.futureobjects.io/api/track-accounts/sources/?folder=4")
    if response.status_code == 200:
        data = response.json()
        count = data.get('count', 0)
        results = data.get('results', [])
        
        print(f"✅ API Response: {count} sources found")
        
        if count > 0:
            print(f"📋 Sources in folder 4:")
            for i, source in enumerate(results, 1):
                print(f"   {i}. {source.get('name')} ({source.get('platform')})")
                print(f"      ID: {source.get('id')}")
                print(f"      Instagram: {source.get('instagram_link', 'None')}")
                print(f"      Facebook: {source.get('facebook_link', 'None')}")
        
        return count > 0
    else:
        print(f"❌ API Error: {response.status_code}")
        return False

def test_scraper_trigger_debug():
    """Test scraper trigger with debug info"""
    
    print("\n🚀 TESTING SCRAPER TRIGGER")
    print("=" * 40)
    
    payload = {
        "folder_id": 4,
        "user_id": 1,
        "num_of_posts": 1,
        "date_range": {
            "start_date": "2025-09-01T00:00:00.000Z",
            "end_date": "2025-09-30T23:59:59.000Z"
        }
    }
    
    print(f"📤 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            "https://trackfutura.futureobjects.io/api/brightdata/trigger-scraper/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=60
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            success = result.get('success', False)
            error = result.get('error', 'No error')
            
            if success:
                print(f"✅ SCRAPER SUCCESS!")
                print(f"   Platforms: {result.get('platforms_scraped', [])}")
                print(f"   Results: {result.get('results', {})}")
                
                # Look for webhook delivery method in results
                for platform, platform_result in result.get('results', {}).items():
                    if platform_result.get('success'):
                        print(f"   📱 {platform.upper()} triggered successfully")
                        if 'job_id' in platform_result:
                            print(f"      Job ID: {platform_result['job_id']}")
                return True
            else:
                print(f"❌ SCRAPER FAILED: {error}")
                return False
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False

def check_webhook_configuration():
    """Check if webhook delivery method is being used"""
    
    print("\n🔗 CHECKING WEBHOOK CONFIGURATION")
    print("=" * 40)
    
    # The webhook configuration should be visible in the scraper trigger logs
    # Since we can't access the server logs directly, we'll check BrightData API
    
    brightdata_api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    # Check recent snapshots to see delivery method
    snapshots_url = "https://api.brightdata.com/datasets/v3/snapshots"
    
    try:
        response = requests.get(
            snapshots_url,
            headers={
                "Authorization": f"Bearer {brightdata_api_token}",
                "Content-Type": "application/json"
            },
            params={"limit": 3},
            timeout=30
        )
        
        if response.status_code == 200:
            snapshots = response.json()
            
            print(f"📊 Found {len(snapshots)} recent snapshots")
            
            for i, snapshot in enumerate(snapshots, 1):
                snapshot_id = snapshot.get('id', 'unknown')
                dataset_id = snapshot.get('dataset_id', 'unknown')
                status = snapshot.get('status', 'unknown')
                created_at = snapshot.get('created_at', 'unknown')
                
                # The key field we're looking for
                delivery_method = snapshot.get('delivery_method', 'not_specified')
                
                print(f"   Snapshot {i}: {snapshot_id}")
                print(f"      Dataset: {dataset_id}")
                print(f"      Status: {status}")
                print(f"      Created: {created_at}")
                print(f"      🎯 DELIVERY METHOD: {delivery_method}")
                
                if delivery_method == 'webhook':
                    print(f"      ✅ Using webhook delivery!")
                elif delivery_method == 'api_fetch':
                    print(f"      ❌ Using API fetch delivery (should be webhook)")
                elif delivery_method == 'not_specified':
                    print(f"      ⚠️ Delivery method not specified")
                else:
                    print(f"      ❓ Unknown delivery method: {delivery_method}")
        else:
            print(f"❌ BrightData API error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking BrightData: {str(e)}")

def main():
    """Run all tests"""
    
    print("🔥 URGENT FOLDER 4 AND WEBHOOK DELIVERY DEBUG")
    print("=" * 60)
    print("This will test both issues:")
    print("1. Folder 4 sources not found in BrightData trigger")
    print("2. Webhook delivery method configuration")
    print("=" * 60)
    
    # Test 1: Check folder 4 sources
    folder_4_ok = test_folder_4_sources()
    
    # Test 2: Trigger scraper
    scraper_ok = test_scraper_trigger_debug()
    
    # Test 3: Check webhook config
    check_webhook_configuration()
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    print(f"Folder 4 Sources Available: {'✅' if folder_4_ok else '❌'}")
    print(f"Scraper Trigger Success: {'✅' if scraper_ok else '❌'}")
    
    if folder_4_ok and not scraper_ok:
        print("\n🚨 DIAGNOSIS: Folder 4 has sources but scraper trigger fails!")
        print("LIKELY CAUSES:")
        print("- Field reference issue in BrightData service")
        print("- Django cache issue after deployment")
        print("- Foreign key relation problem")
        
        print("\nIMMEDIATE ACTIONS:")
        print("1. Check if service is using correct 'folder' field (not 'folder_id')")
        print("2. Restart Django service to clear cache")
        print("3. Check if there are any migration issues")
    
    if not folder_4_ok:
        print("\n🚨 DIAGNOSIS: Folder 4 has no sources!")
        print("IMMEDIATE ACTION: Run folder 4 fix endpoint")
    
    print("\nWEBHOOK DELIVERY METHOD:")
    print("- Check the 'DELIVERY METHOD' field in snapshots above")
    print("- Should be 'webhook', not 'api_fetch' or 'not_specified'")
    print("- If not 'webhook', the backend configuration needs verification")

if __name__ == "__main__":
    main()