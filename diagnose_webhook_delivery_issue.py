#!/usr/bin/env python3
"""
🚨 BRIGHTDATA DELIVERY METHOD DIAGNOSTIC
========================================

Diagnoses why delivery method is still not "webhook" after adding webhook in BrightData dashboard.
This will check the actual API calls and BrightData responses.
"""

import requests
import json
import time

def diagnose_delivery_method_issue():
    """Diagnose why delivery method is still not webhook"""
    
    print("🚨 BRIGHTDATA DELIVERY METHOD DIAGNOSTIC")
    print("=" * 50)
    print("ISSUE: Webhook added in dashboard but delivery method still not 'webhook'")
    print("=" * 50)
    
    base_url = "https://trackfutura.futureobjects.io"
    
    # Test 1: Trigger scraper and check the actual BrightData API call
    print("\n1. 🔍 DIAGNOSING SCRAPER TRIGGER API CALL...")
    
    # First ensure folder 4 has sources
    print("   Checking folder 4 sources...")
    try:
        sources_response = requests.get(f"{base_url}/api/track-accounts/sources/?folder=4")
        if sources_response.status_code == 200:
            sources_data = sources_response.json()
            source_count = sources_data.get('count', 0)
            print(f"   ✅ Folder 4 has {source_count} sources")
            
            if source_count == 0:
                print("   🔧 Adding sources to folder 4...")
                fix_response = requests.post(f"{base_url}/api/track-accounts/fix-folder-4/")
                if fix_response.status_code == 200:
                    print("   ✅ Sources added to folder 4")
                else:
                    print(f"   ❌ Failed to add sources: {fix_response.status_code}")
                    return False
        else:
            print(f"   ❌ Failed to check folder 4: {sources_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error checking folder 4: {e}")
        return False
    
    # Test 2: Trigger scraper with debug logging
    print("\n2. 🚀 TRIGGERING SCRAPER WITH DIAGNOSTIC LOGGING...")
    
    scraper_payload = {
        "folder_id": 4,
        "user_id": 1,
        "num_of_posts": 1,  # Minimal for testing
        "date_range": {
            "start_date": "2025-09-01T00:00:00.000Z",
            "end_date": "2025-09-30T23:59:59.000Z"
        }
    }
    
    try:
        print("   Making scraper trigger request...")
        scraper_response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(scraper_payload),
            timeout=120  # Longer timeout to see full logs
        )
        
        print(f"   📡 POST /api/brightdata/trigger-scraper/")
        print(f"   Status: {scraper_response.status_code}")
        print(f"   Response Headers: {dict(list(scraper_response.headers.items())[:3])}")
        
        if scraper_response.status_code == 200:
            result = scraper_response.json()
            success = result.get('success', False)
            
            print(f"   📊 Response Summary:")
            print(f"      Success: {success}")
            print(f"      Platforms: {result.get('platforms_scraped', [])}")
            print(f"      Total Platforms: {result.get('total_platforms', 0)}")
            print(f"      Message: {result.get('message', 'No message')}")
            
            if success:
                print(f"   ✅ Scraper trigger successful!")
                
                # Check individual platform results
                platform_results = result.get('results', {})
                for platform, platform_result in platform_results.items():
                    print(f"   📱 {platform.upper()}:")
                    print(f"      Success: {platform_result.get('success', False)}")
                    if platform_result.get('job_id'):
                        print(f"      Job ID: {platform_result.get('job_id')}")
                    if platform_result.get('snapshot_id'):
                        print(f"      Snapshot ID: {platform_result.get('snapshot_id')}")
                    if platform_result.get('dataset_id'):
                        print(f"      Dataset ID: {platform_result.get('dataset_id')}")
                
                return True
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"   ❌ Scraper trigger failed: {error_msg}")
                return False
        else:
            print(f"   ❌ Scraper trigger HTTP error: {scraper_response.status_code}")
            print(f"   Response: {scraper_response.text[:500]}...")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ Scraper trigger timed out (this might be normal for long API calls)")
        print(f"   The API call logs should show the webhook configuration details")
        return True  # Timeout doesn't mean failure
    except Exception as e:
        print(f"   ❌ Scraper trigger error: {e}")
        return False
    
def check_brightdata_webhook_status():
    """Check BrightData webhook status and configuration"""
    
    print("\n3. 🔍 CHECKING BRIGHTDATA WEBHOOK STATUS...")
    
    # These are the actual BrightData API endpoints for checking webhook status
    brightdata_api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    datasets = {
        "instagram": "gd_lk5ns7kz21pck8jpis",
        "facebook": "gd_lkaxegm826bjpoo9m5"
    }
    
    for platform, dataset_id in datasets.items():
        print(f"\n   📱 Checking {platform.upper()} dataset: {dataset_id}")
        
        # Check dataset configuration
        config_url = f"https://api.brightdata.com/datasets/v3/dataset/{dataset_id}"
        
        try:
            config_response = requests.get(
                config_url,
                headers={
                    "Authorization": f"Bearer {brightdata_api_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            print(f"   📡 GET {config_url}")
            print(f"   Status: {config_response.status_code}")
            
            if config_response.status_code == 200:
                config_data = config_response.json()
                
                # Look for webhook configuration
                delivery_method = config_data.get('delivery_method', 'not_set')
                webhook_url = config_data.get('webhook_url', 'not_set')
                notify_url = config_data.get('notify_url', 'not_set')
                
                print(f"   📋 Configuration:")
                print(f"      Delivery Method: {delivery_method}")
                print(f"      Webhook URL: {webhook_url}")
                print(f"      Notify URL: {notify_url}")
                
                if delivery_method == 'webhook':
                    print(f"   ✅ Delivery method correctly set to 'webhook'!")
                else:
                    print(f"   ❌ Delivery method is '{delivery_method}', should be 'webhook'!")
                    
                if 'trackfutura.futureobjects.io' in str(webhook_url):
                    print(f"   ✅ Webhook URL correctly configured!")
                else:
                    print(f"   ❌ Webhook URL not correctly configured!")
                    
            elif config_response.status_code == 401:
                print(f"   ❌ Authentication failed - check API token")
            elif config_response.status_code == 404:
                print(f"   ❌ Dataset not found - check dataset ID")
            else:
                print(f"   ❌ Failed to get configuration: {config_response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Error checking {platform} dataset: {e}")

def check_recent_brightdata_jobs():
    """Check recent BrightData jobs to see their delivery method"""
    
    print("\n4. 📊 CHECKING RECENT BRIGHTDATA JOBS...")
    
    brightdata_api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    # Check recent snapshots/jobs
    snapshots_url = "https://api.brightdata.com/datasets/v3/snapshots"
    
    try:
        snapshots_response = requests.get(
            snapshots_url,
            headers={
                "Authorization": f"Bearer {brightdata_api_token}",
                "Content-Type": "application/json"
            },
            params={"limit": 5},  # Get last 5 jobs
            timeout=30
        )
        
        print(f"   📡 GET {snapshots_url}?limit=5")
        print(f"   Status: {snapshots_response.status_code}")
        
        if snapshots_response.status_code == 200:
            snapshots_data = snapshots_response.json()
            
            if isinstance(snapshots_data, list) and len(snapshots_data) > 0:
                print(f"   📊 Found {len(snapshots_data)} recent jobs:")
                
                for i, snapshot in enumerate(snapshots_data[:3]):  # Show first 3
                    snapshot_id = snapshot.get('id', 'unknown')
                    status = snapshot.get('status', 'unknown')
                    dataset_id = snapshot.get('dataset_id', 'unknown')
                    delivery_method = snapshot.get('delivery_method', 'not_specified')
                    created_at = snapshot.get('created_at', 'unknown')
                    
                    print(f"   🔍 Job {i+1}:")
                    print(f"      Snapshot ID: {snapshot_id}")
                    print(f"      Dataset ID: {dataset_id}")
                    print(f"      Status: {status}")
                    print(f"      Delivery Method: {delivery_method}")
                    print(f"      Created: {created_at}")
                    
                    if delivery_method == 'webhook':
                        print(f"      ✅ This job uses webhook delivery!")
                    elif delivery_method in ['api_fetch', 'api']:
                        print(f"      ❌ This job uses API fetch delivery!")
                    else:
                        print(f"      ⚠️ Delivery method unclear: {delivery_method}")
                    print()
                    
            else:
                print(f"   ⚠️ No recent jobs found")
                
        else:
            print(f"   ❌ Failed to get recent jobs: {snapshots_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error checking recent jobs: {e}")

def main():
    """Main diagnostic function"""
    
    print("🎯 BRIGHTDATA WEBHOOK DELIVERY METHOD DIAGNOSTIC")
    print("=" * 60)
    print("Investigating why delivery method is not 'webhook' after dashboard configuration")
    print("=" * 60)
    
    # Step 1: Test scraper trigger
    scraper_success = diagnose_delivery_method_issue()
    
    # Step 2: Check BrightData webhook configuration
    check_brightdata_webhook_status()
    
    # Step 3: Check recent job delivery methods
    check_recent_brightdata_jobs()
    
    # Summary and recommendations
    print("\n" + "=" * 60)
    print("📋 DIAGNOSTIC SUMMARY AND RECOMMENDATIONS")
    print("=" * 60)
    
    print("\n🔍 POSSIBLE CAUSES FOR DELIVERY METHOD NOT BEING 'WEBHOOK':")
    print("1. 📱 BrightData dashboard configuration not saved properly")
    print("2. 🕐 Configuration changes take time to propagate")
    print("3. 📝 Webhook URL format might be incorrect in dashboard")
    print("4. 🔑 Authentication headers might be missing")
    print("5. 📊 Old jobs still show old delivery method")
    
    print("\n🔧 IMMEDIATE ACTIONS TO TAKE:")
    print("1. Double-check BrightData dashboard configuration")
    print("2. Ensure webhook URL is exactly: https://trackfutura.futureobjects.io/api/brightdata/webhook/")
    print("3. Verify authentication header is set")
    print("4. Try creating a new test job to see if it uses webhook delivery")
    print("5. Check if there are any error messages in BrightData dashboard")
    
    print("\n📞 IF ISSUE PERSISTS:")
    print("- Contact BrightData support to verify webhook configuration")
    print("- Ask them to confirm delivery method is set to 'webhook' for your datasets")
    print("- Request they check if there are any validation errors")

if __name__ == "__main__":
    main()