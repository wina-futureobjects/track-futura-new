"""
🚨 EMERGENCY BRIGHTDATA FOLDER FIX
==================================

This script will test and fix the exact folder filtering issue in BrightData service.
"""

import requests
import json

def test_brightdata_service_directly():
    """Test the BrightData service directly with debug info"""
    
    print("🔥 DIRECT BRIGHTDATA SERVICE TEST")
    print("=" * 50)
    
    # Create a minimal test to bypass the BrightData service and call directly
    test_payload = {
        "folder_id": 4,
        "user_id": 1,
        "num_of_posts": 1,
        "date_range": {
            "start_date": "2025-09-01T00:00:00.000Z",
            "end_date": "2025-09-30T23:59:59.000Z"
        }
    }
    
    print(f"📤 Testing BrightData trigger with debug info...")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    # Test the exact endpoint with timeout
    try:
        response = requests.post(
            "https://trackfutura.futureobjects.io/api/brightdata/trigger-scraper/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_payload),
            timeout=60
        )
        
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            success = result.get('success', False)
            error = result.get('error', 'No error provided')
            
            if success:
                print(f"✅ SUCCESS! BrightData trigger worked!")
                return True
            else:
                print(f"❌ FAILED: {error}")
                
                # If it's still the folder issue, we need to check the deployment
                if "No sources found" in error:
                    print(f"🔍 Folder issue detected. Checking deployment status...")
                    return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def check_deployment_status():
    """Check if the latest deployment is active"""
    
    print(f"\n🔍 CHECKING DEPLOYMENT STATUS")
    print("=" * 30)
    
    # Test a simple API endpoint to see if our changes are deployed
    try:
        # Check the folder 4 fix endpoint to see if it's using new code
        response = requests.post("https://trackfutura.futureobjects.io/api/track-accounts/fix-folder-4/")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Deployment active - folder fix response: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Deployment issue - status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Deployment check failed: {e}")
        return False

def force_cache_refresh():
    """Force a cache refresh by hitting multiple endpoints"""
    
    print(f"\n🔄 FORCING CACHE REFRESH")
    print("=" * 25)
    
    endpoints_to_hit = [
        "/api/track-accounts/sources/?folder=4",
        "/api/track-accounts/fix-folder-4/", 
        "/api/brightdata/trigger-scraper/",
    ]
    
    for endpoint in endpoints_to_hit:
        try:
            url = f"https://trackfutura.futureobjects.io{endpoint}"
            
            if endpoint.endswith('trigger-scraper/'):
                # POST request with minimal payload
                response = requests.post(url, 
                    headers={"Content-Type": "application/json"},
                    data='{"folder_id":4,"user_id":1,"num_of_posts":1}',
                    timeout=10
                )
            else:
                # GET or POST request
                if endpoint.endswith('fix-folder-4/'):
                    response = requests.post(url, timeout=10)
                else:
                    response = requests.get(url, timeout=10)
            
            print(f"   {endpoint}: {response.status_code}")
            
        except Exception as e:
            print(f"   {endpoint}: ERROR - {str(e)}")
    
    print(f"✅ Cache refresh attempts completed")

def main():
    """Main diagnostic and fix routine"""
    
    print("🚨 EMERGENCY BRIGHTDATA FOLDER FIX")
    print("=" * 60)
    print("Diagnosing and fixing folder 4 + webhook delivery issues")
    print("=" * 60)
    
    # Step 1: Check deployment status
    deployment_ok = check_deployment_status()
    
    # Step 2: Force cache refresh
    force_cache_refresh()
    
    # Step 3: Test BrightData service directly 
    brightdata_ok = test_brightdata_service_directly()
    
    # Step 4: Final diagnosis
    print("\n" + "=" * 60)
    print("📋 EMERGENCY DIAGNOSIS RESULTS")
    print("=" * 60)
    
    print(f"Deployment Status: {'✅ OK' if deployment_ok else '❌ ISSUE'}")
    print(f"BrightData Service: {'✅ OK' if brightdata_ok else '❌ ISSUE'}")
    
    if not deployment_ok:
        print(f"\n🚨 DEPLOYMENT ISSUE DETECTED")
        print(f"The latest code changes may not be deployed properly.")
        print(f"ACTION: Check Upsun deployment logs and redeploy if necessary.")
        
    if not brightdata_ok:
        print(f"\n🚨 BRIGHTDATA SERVICE ISSUE DETECTED") 
        print(f"Even after deployment fixes, BrightData service still failing.")
        print(f"LIKELY CAUSES:")
        print(f"1. Django ORM caching - service still using old import")
        print(f"2. Field reference still incorrect in deployed code")
        print(f"3. Database migration issue with folder relationships")
        
        print(f"\nIMMEDIATE ACTIONS:")
        print(f"1. Restart Django application to clear ORM cache")
        print(f"2. Verify the exact field name in TrackSource model")
        print(f"3. Check if there are pending migrations")
        print(f"4. Test with a direct Django shell query")
    
    if deployment_ok and brightdata_ok:
        print(f"\n🎉 SUCCESS! Both issues appear to be resolved!")
        print(f"✅ Deployment is active")
        print(f"✅ BrightData service is working")
        print(f"✅ Folder 4 sources are accessible")
        print(f"\nNext: Test webhook delivery method in new scraper jobs")
    
    print(f"\n📞 IF ISSUES PERSIST:")
    print(f"- Manual Django shell debugging required") 
    print(f"- Check actual deployed code on server")
    print(f"- Verify BrightData API credentials and dataset IDs")
    print(f"- Contact BrightData support for webhook delivery configuration")

if __name__ == "__main__":
    main()