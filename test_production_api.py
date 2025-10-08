#!/usr/bin/env python
"""
Test production API to verify BrightData restoration worked
"""
import requests

def test_production_api():
    print("🚀 Testing Production API...")
    
    # Test authentication
    auth_response = requests.post(
        "https://trackfutura.upsun.app/api/auth/login/",
        json={"username": "superadmin", "password": "admin123"}
    )
    
    print(f"🔐 Auth status: {auth_response.status_code}")
    if auth_response.status_code == 200:
        token = auth_response.json().get('access_token', 'temp-token-for-testing')
        print(f"🔑 Token: {token[:20]}...")
    else:
        token = 'temp-token-for-testing'
        print("⚠️ Using fallback token")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test platform services
    print("\n📊 Testing platform services...")
    platforms_response = requests.get(
        "https://trackfutura.upsun.app/api/workflow/platform-services/",
        headers=headers
    )
    
    print(f"Platform services status: {platforms_response.status_code}")
    if platforms_response.status_code == 200:
        platform_services = platforms_response.json()
        print(f"Platform services count: {len(platform_services)}")
        for ps in platform_services[:3]:  # Show first 3
            print(f"  - {ps.get('platform_name', 'Unknown')} + {ps.get('service_name', 'Unknown')}")
    else:
        print(f"Error: {platforms_response.text[:200]}")
    
    # Test BrightData configs
    print("\n⚡ Testing BrightData configs...")
    brightdata_response = requests.get(
        "https://trackfutura.upsun.app/api/brightdata/configs/",
        headers=headers
    )
    
    print(f"BrightData configs status: {brightdata_response.status_code}")
    if brightdata_response.status_code == 200:
        configs = brightdata_response.json()
        if hasattr(configs, 'get'):
            results = configs.get('results', configs)
        else:
            results = configs
        print(f"BrightData configs count: {len(results) if isinstance(results, list) else 'N/A'}")
        if isinstance(results, list):
            for config in results[:2]:  # Show first 2
                print(f"  - {config.get('platform', 'Unknown')}: {config.get('dataset_id', 'Unknown')}")
    else:
        print(f"Error: {brightdata_response.text[:200]}")
    
    # Test workflow creation
    print("\n🏃 Testing workflow creation...")
    workflow_data = {
        "sources": ["nike"],
        "search_input": "test search",
        "platforms": ["instagram"],
        "services": ["posts"]
    }
    
    workflow_response = requests.post(
        "https://trackfutura.upsun.app/api/workflow/create/",
        headers=headers,
        json=workflow_data
    )
    
    print(f"Workflow creation status: {workflow_response.status_code}")
    if workflow_response.status_code in [200, 201]:
        workflow = workflow_response.json()
        print(f"✅ Workflow created: {workflow.get('id', 'Unknown ID')}")
        if 'brightdata_requests' in workflow:
            print(f"BrightData requests count: {len(workflow['brightdata_requests'])}")
    else:
        print(f"Error: {workflow_response.text[:300]}")

if __name__ == '__main__':
    test_production_api()