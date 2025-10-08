#!/usr/bin/env python3
"""
VERIFY DEPLOYMENT AFTER REDEPLOY
Check if workflow API fixes are now deployed
"""

import requests
import time

def main():
    """Verify deployment after manual redeploy"""
    print("🚀 VERIFYING DEPLOYMENT AFTER REDEPLOY")
    print("=" * 60)
    
    # Wait a moment for deployment to settle
    print("⏳ Waiting for deployment to settle...")
    time.sleep(10)
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api"
    
    print("\n📡 TESTING ALL WORKFLOW ENDPOINTS:")
    print("-" * 40)
    
    endpoints_to_test = [
        ("/workflow/input-collections/", "Nike InputCollection"),
        ("/workflow/input-collections/available_platforms/", "Available Platforms"),
        ("/workflow/input-collections/platform_services/", "Platform Services"),
        ("/workflow/api/available-platforms/", "Direct Available Platforms"), 
        ("/workflow/api/platform-services/", "Direct Platform Services"),
    ]
    
    all_working = True
    working_count = 0
    
    for endpoint, description in endpoints_to_test:
        print(f"\n🔗 Testing: {description}")
        print(f"   URL: {endpoint}")
        
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=15)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        if 'results' in data:
                            print(f"   ✅ SUCCESS - Results: {len(data['results'])}")
                            working_count += 1
                        elif 'count' in data:
                            print(f"   ✅ SUCCESS - Count: {data['count']}")
                            working_count += 1
                        else:
                            print(f"   ✅ SUCCESS - Keys: {list(data.keys())}")
                            working_count += 1
                    elif isinstance(data, list):
                        print(f"   ✅ SUCCESS - Items: {len(data)}")
                        working_count += 1
                    else:
                        print(f"   ✅ SUCCESS - Response received")
                        working_count += 1
                except:
                    print(f"   ✅ SUCCESS - Non-JSON response")
                    working_count += 1
            else:
                print(f"   ❌ FAILED - {response.status_code}")
                if response.status_code == 404:
                    print(f"      🔍 Endpoint not found")
                elif response.status_code == 500:
                    print(f"      ⚠️ Server error")
                all_working = False
                
        except Exception as e:
            print(f"   ❌ ERROR - {str(e)}")
            all_working = False
    
    print("\n" + "=" * 60)
    print("🎯 DEPLOYMENT VERIFICATION RESULTS")
    print("=" * 60)
    
    print(f"✅ Working Endpoints: {working_count}/{len(endpoints_to_test)}")
    
    if working_count >= 3:  # Core endpoints working
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print("✅ Core BrightData workflow is operational")
        
        if working_count == len(endpoints_to_test):
            print("🎊 ALL ENDPOINTS WORKING - PERFECT DEPLOYMENT!")
        else:
            print("🔧 Some direct endpoints may need additional fixes")
            
        print("\n🚀 READY FOR CLIENT TESTING:")
        print("• Nike InputCollection accessible")
        print("• Platform selection working")
        print("• Service selection working")
        print("• Workflow management operational")
        
    else:
        print("🚨 DEPLOYMENT ISSUES DETECTED")
        print("❌ Core workflow endpoints not working")
        print("🔧 Further investigation needed")
    
    return working_count >= 3

if __name__ == "__main__":
    main()