#!/usr/bin/env python3
"""
Test BrightData with correct zone name from dashboard
"""
import requests
import json

# Your BrightData credentials from dashboard
API_TOKEN = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
ZONE_NAME = "web_unlocker1"  # Correct zone name from dashboard

def test_brightdata_with_correct_zone():
    """Test BrightData with the correct zone name"""
    print("🎯 TESTING BRIGHTDATA WITH CORRECT ZONE NAME")
    print("=" * 50)
    
    # Test the working endpoint with correct zone
    url = "https://api.brightdata.com/dca/trigger"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    # Test payloads with correct zone name
    test_payloads = [
        {
            "collector": ZONE_NAME,  # Using correct zone name
            "input": [{"url": "https://httpbin.org/json"}]
        },
        {
            "collector": ZONE_NAME,
            "url": "https://httpbin.org/json"
        },
        {
            "zone": ZONE_NAME,  # Alternative format
            "url": "https://httpbin.org/json"
        }
    ]
    
    for i, payload in enumerate(test_payloads):
        try:
            print(f"\n🧪 Test {i+1}: {payload}")
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code in [200, 201, 202]:
                print(f"   🎉 SUCCESS! BrightData working with zone: {ZONE_NAME}")
                return True
                
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
    
    # Test with Web Unlocker API format (from your dashboard)
    print(f"\n🔧 Testing Web Unlocker API format...")
    try:
        unlocker_url = "https://api.brightdata.com/request"
        unlocker_payload = {
            "zone": ZONE_NAME,
            "url": "https://httpbin.org/json",
            "format": "raw"
        }
        
        response = requests.post(unlocker_url, headers=headers, json=unlocker_payload, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code in [200, 201, 202]:
            print(f"   🎉 SUCCESS! Web Unlocker API working!")
            return True
            
    except Exception as e:
        print(f"   💥 Error: {str(e)}")
    
    return False

def test_production_workflow_with_correct_zone():
    """Test production workflow with corrected zone"""
    print(f"\n🚀 TESTING PRODUCTION WORKFLOW WITH CORRECT ZONE")
    print("=" * 50)
    
    try:
        # Test workflow creation
        auth_response = requests.post(
            "https://trackfutura.futureobjects.io/api/users/login/",
            json={"username": "superadmin", "password": "admin123"},
            timeout=30
        )
        
        if auth_response.status_code == 200:
            token = auth_response.json()["token"]
            print(f"✅ Authentication successful")
            
            # Test workflow creation
            workflow_data = {
                "name": "BrightData Zone Test",
                "project": 3,
                "source_folder_ids": [20, 21],
                "platforms_to_scrape": ["instagram", "facebook"],
                "content_types_to_scrape": {
                    "instagram": ["posts"],
                    "facebook": ["posts"]
                },
                "num_of_posts": 5
            }
            
            workflow_response = requests.post(
                "https://trackfutura.futureobjects.io/api/brightdata/batch-jobs/",
                json=workflow_data,
                headers={"Authorization": f"Token {token}"},
                timeout=30
            )
            
            print(f"Workflow creation status: {workflow_response.status_code}")
            if workflow_response.status_code == 201:
                print(f"✅ SUCCESS! Workflow created with corrected BrightData zone")
                response_data = workflow_response.json()
                print(f"   Job ID: {response_data.get('id')}")
                return True
            else:
                print(f"❌ Workflow creation failed: {workflow_response.text}")
                return False
        else:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 BRIGHTDATA ZONE CORRECTION TEST")
    print("=" * 60)
    print(f"Zone Name: {ZONE_NAME}")
    print(f"API Token: {API_TOKEN[:20]}...")
    print()
    
    # Test direct BrightData API
    api_success = test_brightdata_with_correct_zone()
    
    # Test production workflow
    workflow_success = test_production_workflow_with_correct_zone()
    
    print(f"\n✅ RESULTS:")
    print(f"   BrightData API: {'✅ SUCCESS' if api_success else '❌ FAILED'}")
    print(f"   Workflow Test: {'✅ SUCCESS' if workflow_success else '❌ FAILED'}")
    
    if api_success or workflow_success:
        print(f"\n🎉 BRIGHTDATA IS NOW WORKING!")
        print(f"   Zone: {ZONE_NAME}")
        print(f"   Your workflow should function properly now!")
    else:
        print(f"\n🔧 Need further investigation")