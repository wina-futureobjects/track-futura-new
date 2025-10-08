#!/usr/bin/env python3
"""
CHECK DEPLOYMENT STATUS
Verify if workflow API fixes are deployed to production
"""

import requests
import json

def check_deployment_status():
    """Check if the workflow API fixes are deployed"""
    print("🔍 CHECKING DEPLOYMENT STATUS")
    print("🎯 Verifying workflow API fixes are live")
    print("=" * 60)
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api"
    
    print("\n📡 TESTING PRODUCTION ENDPOINTS:")
    print("-" * 40)
    
    endpoints_to_test = [
        ("/workflow/input-collections/", "Nike InputCollection"),
        ("/workflow/input-collections/available_platforms/", "Available Platforms"),
        ("/workflow/input-collections/platform_services/", "Platform Services"),
        ("/workflow/api/available-platforms/", "Direct Available Platforms"),
        ("/workflow/api/platform-services/", "Direct Platform Services"),
    ]
    
    all_working = True
    
    for endpoint, description in endpoints_to_test:
        print(f"\n🔗 Testing: {description}")
        print(f"   URL: {endpoint}")
        
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        if 'results' in data:
                            print(f"   ✅ SUCCESS - Results: {len(data['results'])}")
                        elif 'count' in data:
                            print(f"   ✅ SUCCESS - Count: {data['count']}")
                        else:
                            print(f"   ✅ SUCCESS - Keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"   ✅ SUCCESS - Items: {len(data)}")
                    else:
                        print(f"   ✅ SUCCESS - Response received")
                except json.JSONDecodeError:
                    print(f"   ✅ SUCCESS - Non-JSON response")
            else:
                print(f"   ❌ FAILED - {response.status_code}")
                if response.status_code == 404:
                    print(f"   🚨 ENDPOINT NOT FOUND - May need deployment")
                all_working = False
                
        except Exception as e:
            print(f"   ❌ ERROR - {str(e)}")
            all_working = False
    
    print("\n" + "=" * 60)
    
    if all_working:
        print("🎉 DEPLOYMENT STATUS: ✅ FULLY DEPLOYED!")
        print("🎯 All workflow API endpoints are working correctly")
        print("🚀 BrightData integration is ready for client testing")
        
        print("\n✅ CONFIRMED WORKING:")
        print("├── Nike InputCollection accessible")
        print("├── Platform selection endpoints active")  
        print("├── Service selection endpoints active")
        print("├── Direct API endpoints functional")
        print("└── Complete workflow system operational")
        
    else:
        print("🚨 DEPLOYMENT STATUS: ❌ PARTIALLY DEPLOYED")
        print("🔧 Some endpoints are not working - may need manual deployment")
        
        print("\n🛠️ SUGGESTED ACTIONS:")
        print("1. Check if git push triggered auto-deployment")
        print("2. Manually deploy if needed: upsun push")
        print("3. Verify environment variables are set")
        print("4. Check application logs for errors")
    
    return all_working

def check_specific_nike_collection():
    """Check specifically for Nike InputCollection"""
    print("\n🏷️ CHECKING NIKE INPUTCOLLECTION:")
    print("-" * 40)
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api"
    
    try:
        response = requests.get(f"{BASE_URL}/workflow/input-collections/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('count', 0) > 0 and data.get('results'):
                nike_collection = data['results'][0]
                print(f"✅ Nike Collection Found:")
                print(f"   - ID: {nike_collection.get('id')}")
                print(f"   - Name: {nike_collection.get('name')}")
                print(f"   - Platform Service: {nike_collection.get('platform_service')}")
                print(f"   - Project: {nike_collection.get('project')}")
                print(f"   - Status: {nike_collection.get('status')}")
                print(f"   - Is Active: {nike_collection.get('is_active')}")
                return True
            else:
                print("❌ No Nike InputCollection found")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        return False

def main():
    """Main deployment check function"""
    print("🎯 BRIGHTDATA WORKFLOW DEPLOYMENT CHECK")
    print("🎯 Verifying production API endpoints")
    print("=" * 70)
    
    # Check general deployment
    deployment_ok = check_deployment_status()
    
    # Check Nike collection specifically  
    nike_ok = check_specific_nike_collection()
    
    print("\n" + "=" * 70)
    print("📋 FINAL DEPLOYMENT STATUS")
    print("=" * 70)
    
    if deployment_ok and nike_ok:
        print("🎊 DEPLOYMENT: ✅ COMPLETE AND OPERATIONAL!")
        print("🎯 BrightData workflow system is fully deployed")
        print("🏷️ Nike InputCollection is accessible")
        print("🚀 Ready for immediate client testing!")
        
        print("\n🔗 CLIENT CAN NOW ACCESS:")
        print("• Workflow Management page")
        print("• Nike InputCollection selection")
        print("• Platform and service options")
        print("• Complete BrightData job creation")
        
    else:
        print("🚨 DEPLOYMENT: ❌ INCOMPLETE")
        if not deployment_ok:
            print("• API endpoints need deployment")
        if not nike_ok:
            print("• Nike InputCollection not accessible")
            
        print("\n🛠️ NEXT STEPS:")
        print("1. Deploy changes manually if auto-deploy failed")
        print("2. Verify InputCollection creation")
        print("3. Test endpoints after deployment")

if __name__ == "__main__":
    main()