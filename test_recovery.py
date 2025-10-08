#!/usr/bin/env python3
"""
Test if the site is back up and BrightData API is working
"""
import requests

def test_site_recovery():
    print("🔧 TESTING SITE RECOVERY AFTER DEPLOYMENT")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test 1: Basic site health
    print("1. 🌐 Testing site health...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Site Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Site is back online!")
        else:
            print(f"   ⚠️  Site returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ Site still down: {e}")
        return
    
    # Test 2: BrightData API
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
        
        print(f"   API Status: {api_response.status_code}")
        
        if api_response.status_code == 200:
            data = api_response.json()
            if data.get('success'):
                print(f"   ✅ BrightData API is working!")
                print(f"   📊 Job ID: {data.get('batch_job_id')}")
                print(f"   📊 Dataset: {data.get('dataset_id')}")
            else:
                print(f"   ❌ API error: {data.get('error')}")
        elif api_response.status_code == 502:
            print("   ⚠️  502 Bad Gateway - Server still restarting")
        else:
            print(f"   ❌ API failed: {api_response.status_code}")
            print(f"   Response: {api_response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
    
    # Test 3: Workflow page
    print("\n3. 📱 Testing workflow management page...")
    try:
        workflow_response = requests.get(
            f"{base_url}/organizations/1/projects/1/workflow-management", 
            timeout=10
        )
        print(f"   Workflow Status: {workflow_response.status_code}")
        if workflow_response.status_code == 200:
            print("   ✅ Workflow page accessible")
        else:
            print(f"   ⚠️  Workflow page: {workflow_response.status_code}")
    except Exception as e:
        print(f"   ❌ Workflow test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 CURRENT STATUS:")
    print("• The 502 error was temporary during deployment")
    print("• Site should be back online now")
    print("• Try the console JavaScript fix again")
    print("• If still 502, wait 2-3 minutes for full restart")

if __name__ == "__main__":
    test_site_recovery()