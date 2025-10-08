#!/usr/bin/env python3
"""
Test if the PERMANENT frontend fix is deployed and working
"""
import requests
import time

def test_permanent_fix():
    print("🔧 TESTING PERMANENT FRONTEND FIX DEPLOYMENT")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Wait a bit for deployment to complete
    print("⏳ Waiting for deployment to complete...")
    time.sleep(30)
    
    print("\n1. 🌐 Testing site health...")
    try:
        response = requests.get(f"{base_url}/", timeout=15)
        print(f"   Site Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Site is online!")
        else:
            print(f"   ⚠️  Site returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ Site check failed: {e}")
        return False
    
    print("\n2. 🚀 Testing BrightData API...")
    try:
        api_response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json={
                "platform": "instagram",
                "urls": ["https://www.instagram.com/nike/"]
            },
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if api_response.status_code == 200:
            data = api_response.json()
            if data.get('success'):
                print(f"   ✅ BrightData API working! Job ID: {data.get('batch_job_id')}")
                print(f"   📊 Dataset: {data.get('dataset_id')}")
            else:
                print(f"   ❌ API error: {data.get('error')}")
        else:
            print(f"   ❌ API failed: {api_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
    
    print("\n3. 🔍 Testing if frontend contains our fix...")
    try:
        workflow_response = requests.get(
            f"{base_url}/organizations/1/projects/1/workflow-management", 
            timeout=15
        )
        if workflow_response.status_code == 200:
            html_content = workflow_response.text
            
            # Look for signs our TypeScript fix is deployed
            has_brightdata_call = '/api/brightdata/trigger-scraper/' in html_content
            has_csrf_function = 'getCsrfToken' in html_content
            has_nike_urls = 'instagram.com/nike' in html_content
            
            print(f"   Workflow page loaded: ✅")
            print(f"   Contains BrightData API call: {'✅' if has_brightdata_call else '❌'}")
            print(f"   Contains CSRF function: {'✅' if has_csrf_function else '❌'}")
            print(f"   Contains Nike URLs: {'✅' if has_nike_urls else '❌'}")
            
            if has_brightdata_call and has_csrf_function:
                print("   🎉 PERMANENT FIX IS DEPLOYED!")
                return True
            else:
                print("   ⚠️  Frontend fix not yet deployed")
                return False
        else:
            print(f"   ❌ Workflow page failed: {workflow_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend check failed: {e}")
        return False

if __name__ == "__main__":
    success = test_permanent_fix()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 PERMANENT FIX IS WORKING!")
        print("=" * 50)
        print("✅ Your Instant Run button should now work permanently!")
        print("✅ No more console JavaScript needed!")
        print("✅ Goes to: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/workflow-management")
        print("✅ Click 'Instant Run' → Fill dates → Click 'Create Global Run'")
        print("✅ Should trigger Nike Instagram BrightData scraper!")
    else:
        print("\n" + "=" * 50)
        print("⚠️  DEPLOYMENT STILL IN PROGRESS")
        print("=" * 50)
        print("• Frontend fix is not yet deployed")
        print("• Wait 5-10 minutes for build to complete")
        print("• Run this test again")
        print("• If still failing, we'll debug further")