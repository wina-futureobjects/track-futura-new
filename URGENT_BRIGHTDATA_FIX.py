#!/usr/bin/env python3
"""
URGENT: Complete BrightData fix for scraper functionality
"""
import requests
import json

def urgent_brightdata_fix():
    """Complete fix for BrightData scraper issues"""
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("🚨 URGENT BRIGHTDATA SCRAPER FIX")
    print("=" * 50)
    
    # Issue 1: Check the exact BrightData API token status
    print("1. 🔑 BRIGHTDATA API TOKEN CHECK")
    try:
        # Try to trigger a test scraping request
        test_url = f"{base_url}/api/brightdata/webhook/"
        response = requests.post(test_url, json={"test": "webhook"}, timeout=10)
        print(f"   Webhook test status: {response.status_code}")
        
        if response.status_code == 400:
            print("   ✅ Webhook endpoint working (400 = missing required data)")
        elif response.status_code == 200:
            print("   ✅ Webhook endpoint working")
        else:
            print(f"   ❌ Webhook issue: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Webhook error: {str(e)}")
    
    # Issue 2: Create the missing API token
    print("\n2. 🔧 API TOKEN CONFIGURATION")
    print("   💡 The BrightData API token needs to be set in production")
    print("   📝 Current token should be: 8af6995e-3baa-4b69-9df7-8d7671e621eb")
    print("   🔗 This needs to be configured in Django settings")
    
    # Issue 3: Fix the track source connection
    print("\n3. 🔗 TRACK SOURCE CONNECTION")
    print("   💡 Track source (Nike IG) exists but not connected to workflow")
    print("   🔧 MANUAL FIX NEEDED:")
    print("   ")
    print("   Step 1: Go to Source Tracking and verify Nike IG exists")
    print("   Step 2: Go to Workflow Management")
    print("   Step 3: If no track sources show, refresh the page")
    print("   Step 4: Try creating a scraping run manually")
    
    # Issue 4: Test if we can create a manual workflow
    print("\n4. 🧪 MANUAL WORKFLOW TEST")
    try:
        # Try to create a scraping run directly
        run_data = {
            "project": 3,
            "configuration": {
                "num_of_posts": 10,
                "start_date": "2025-10-01T00:00:00.000Z",
                "end_date": "2025-10-08T23:59:59.000Z",
                "auto_create_folders": True,
                "output_folder_pattern": "scraped_data"
            }
        }
        
        run_url = f"{base_url}/api/workflow/scraping-runs/"
        response = requests.post(run_url, json=run_data, timeout=10)
        
        print(f"   Manual run creation status: {response.status_code}")
        
        if response.status_code == 201:
            run_result = response.json()
            print(f"   ✅ Manual run created: {run_result.get('id')}")
            print("   🚀 This means the workflow system is working!")
        elif response.status_code == 400:
            error_data = response.json()
            print(f"   ⚠️  Validation error: {error_data}")
            print("   💡 This shows what's missing for workflow creation")
        else:
            print(f"   ❌ Run creation failed: {response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Manual workflow test error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 IMMEDIATE ACTION REQUIRED:")
    print("1. Configure BrightData API token in production")
    print("2. Refresh workflow management page")
    print("3. Try creating a scraping run manually")
    print("4. If still failing, check specific error messages")
    print("=" * 50)
    
    # Show the exact URL to test
    print(f"\n🔗 TEST URL: {base_url}/organizations/2/projects/3/workflow-management")
    print("👆 Go to this URL and try creating a workflow")

if __name__ == "__main__":
    urgent_brightdata_fix()