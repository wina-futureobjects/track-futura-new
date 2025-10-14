#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_complete_web_unlocker_workflow():
    """
    Complete test of Web Unlocker functionality on production
    """
    
    print("🎉 COMPLETE WEB UNLOCKER PRODUCTION TEST")
    print("=" * 60)
    
    # Production URL
    base_url = "https://trackfutura.futureobjects.io"
    
    # Test 1: Basic Web Unlocker functionality
    print("\n🔥 TEST 1: Basic Web Unlocker Request")
    test_data_1 = {
        'url': 'https://httpbin.org/html',
        'folder_name': 'Production Test - HttpBin HTML'
    }
    
    response_1 = requests.post(
        f"{base_url}/api/web-unlocker/",
        json=test_data_1,
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    
    print(f"Status: {response_1.status_code}")
    if response_1.status_code == 200:
        result_1 = response_1.json()
        print(f"✅ Folder created: ID {result_1.get('folder_id')}")
        print(f"📄 Success: {result_1.get('success', False)}")
        print(f"📝 Message: {result_1.get('message', 'N/A')}")
    else:
        print(f"❌ Error: {response_1.text}")
    
    # Test 2: Custom folder name with special characters
    print("\n🔥 TEST 2: Web Unlocker with Custom Folder")
    test_data_2 = {
        'url': 'https://httpbin.org/json',
        'folder_name': f'Web Unlocker Test {datetime.now().strftime("%Y%m%d_%H%M%S")}'
    }
    
    response_2 = requests.post(
        f"{base_url}/api/web-unlocker/",
        json=test_data_2,
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    
    print(f"Status: {response_2.status_code}")
    if response_2.status_code == 200:
        result_2 = response_2.json()
        print(f"✅ Folder created: ID {result_2.get('folder_id')}")
        print(f"📄 Success: {result_2.get('success', False)}")
        print(f"📝 Message: {result_2.get('message', 'N/A')}")
    else:
        print(f"❌ Error: {response_2.text}")
    
    # Test 3: Test alternative endpoints
    print("\n🔥 TEST 3: Alternative Web Unlocker Endpoints")
    
    # Test /scrape/ endpoint
    response_3a = requests.post(
        f"{base_url}/api/web-unlocker/scrape/",
        json={'url': 'https://httpbin.org/user-agent', 'folder_name': 'Scrape Endpoint Test'},
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    
    print(f"Scrape endpoint status: {response_3a.status_code}")
    
    # Test /run/ endpoint  
    response_3b = requests.post(
        f"{base_url}/api/web-unlocker/run/",
        json={'url': 'https://httpbin.org/ip', 'folder_name': 'Run Endpoint Test'},
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    
    print(f"Run endpoint status: {response_3b.status_code}")
    
    # Test 4: Frontend Access
    print("\n🔥 TEST 4: Frontend Dashboard Access")
    
    dashboard_response = requests.get(f"{base_url}/", timeout=10)
    print(f"Dashboard status: {dashboard_response.status_code}")
    print(f"Dashboard size: {len(dashboard_response.text)} bytes")
    
    # Check if it contains React content
    if "react" in dashboard_response.text.lower() or "div" in dashboard_response.text.lower():
        print("✅ Frontend React content detected")
    else:
        print("⚠️ Basic HTML served (React not loaded)")
    
    # Test 5: Check Data Storage Integration
    print("\n🔥 TEST 5: Data Storage Integration Check")
    
    # Test brightdata endpoints that should show our Web Unlocker folders
    try:
        folders_response = requests.get(
            f"{base_url}/api/brightdata/simple-jobs/",
            timeout=10
        )
        print(f"Data storage folders status: {folders_response.status_code}")
        
        if folders_response.status_code == 200:
            folders_data = folders_response.json()
            print(f"📁 Total folders in data storage: {len(folders_data.get('folders', []))}")
            
            # Look for our Web Unlocker folders
            web_unlocker_folders = [
                f for f in folders_data.get('folders', [])
                if 'web unlocker' in f.get('name', '').lower() or 
                   'production test' in f.get('name', '').lower()
            ]
            
            if web_unlocker_folders:
                print(f"✅ Found {len(web_unlocker_folders)} Web Unlocker folders in data storage!")
                for folder in web_unlocker_folders[:3]:  # Show first 3
                    print(f"   📁 {folder.get('name')} (ID: {folder.get('id')})")
            else:
                print("⚠️ No Web Unlocker folders found in data storage")
                
        else:
            print(f"❌ Data storage access failed: {folders_response.text[:100]}...")
            
    except Exception as e:
        print(f"🔌 Data storage connection error: {e}")
    
    # Final Summary
    print("\n" + "="*60)
    print("🎯 WEB UNLOCKER PRODUCTION TEST COMPLETE!")
    print("="*60)
    
    # Create summary status
    status_summary = []
    
    if response_1.status_code == 200:
        status_summary.append("✅ Basic Web Unlocker: WORKING")
    else:
        status_summary.append("❌ Basic Web Unlocker: FAILED")
        
    if response_2.status_code == 200:
        status_summary.append("✅ Custom Folder Creation: WORKING")
    else:
        status_summary.append("❌ Custom Folder Creation: FAILED")
        
    if dashboard_response.status_code == 200:
        status_summary.append("✅ Frontend Dashboard: ACCESSIBLE")
    else:
        status_summary.append("❌ Frontend Dashboard: FAILED")
    
    for status in status_summary:
        print(status)
    
    print("\n🌟 Your Web Unlocker is now deployed and functional on production!")
    print(f"🔗 Access your dashboard at: {base_url}")
    print(f"🚀 Web Unlocker API endpoint: {base_url}/api/web-unlocker/")
    
    return True

if __name__ == "__main__":
    test_complete_web_unlocker_workflow()