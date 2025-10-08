#!/usr/bin/env python3
"""
Test the frontend BrightData integration fix
"""
import time
import requests

def test_frontend_fix():
    print("🔧 TESTING FRONTEND BRIGHTDATA INTEGRATION FIX")
    print("=" * 60)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("1. 🌐 Checking deployment status...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Website Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Site is accessible")
        else:
            print("   ⚠️  Site might be deploying...")
    except Exception as e:
        print(f"   ❌ Site check failed: {e}")
    
    print("\n2. 🎯 Testing BrightData API (should still work)...")
    try:
        api_response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json={
                "platform": "instagram",
                "urls": ["https://www.instagram.com/nike/"]
            },
            headers={
                "Content-Type": "application/json",
                "Origin": base_url,
                "Referer": f"{base_url}/organizations/1/projects/1/workflow-management"
            },
            timeout=15
        )
        
        if api_response.status_code == 200:
            data = api_response.json()
            if data.get('success'):
                print(f"   ✅ BrightData API working! Job ID: {data.get('batch_job_id')}")
                print(f"   📊 Dataset: {data.get('dataset_id')}")
            else:
                print(f"   ❌ API returned error: {data.get('error')}")
        else:
            print(f"   ❌ API returned status {api_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
    
    print("\n3. 📱 Checking workflow management page...")
    try:
        workflow_url = f"{base_url}/organizations/1/projects/1/workflow-management"
        workflow_response = requests.get(workflow_url, timeout=10)
        print(f"   Workflow Page Status: {workflow_response.status_code}")
        if workflow_response.status_code == 200:
            print("   ✅ Workflow management page accessible")
        else:
            print("   ⚠️  Page might still be deploying")
    except Exception as e:
        print(f"   ❌ Workflow page check failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 FRONTEND FIX SUMMARY:")
    print("• Modified handleGlobalRun() in AutomatedBatchScraper.tsx")
    print("• Now calls /api/brightdata/trigger-scraper/ directly")
    print("• Added proper CSRF token handling")
    print("• Triggers both Instagram & Facebook scrapers")
    print("• Shows success messages with BrightData job IDs")
    print("")
    print("📋 TO TEST THE FIX:")
    print("1. Go to: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/workflow-management")
    print("2. Click the 'Instant Run' card")
    print("3. Fill in the date fields (required)")
    print("4. Click 'Create Global Run'")
    print("5. Should see success messages with BrightData Job IDs!")
    print("")
    print("⚡ The 'Instant Run' button should now work correctly!")

if __name__ == "__main__":
    test_frontend_fix()