#!/usr/bin/env python
"""
URGENT: Test actual workflow creation in production
"""
import requests
import json

def test_production_workflow():
    print("🚨 TESTING PRODUCTION WORKFLOW CREATION")
    
    # First, let's get a proper auth token
    try:
        auth_response = requests.post(
            "https://trackfutura.futureobjects.io/api/users/login/",
            json={"username": "superadmin", "password": "admin123"},
            timeout=30
        )
        print(f"Auth status: {auth_response.status_code}")
        
        if auth_response.status_code == 200:
            data = auth_response.json()
            token = data.get('access_token', data.get('token', 'temp-token-for-testing'))
            print(f"Got token: {token[:20]}...")
        else:
            token = 'temp-token-for-testing'
            print("Using fallback token")
            
    except Exception as e:
        print(f"Auth failed: {e}")
        token = 'temp-token-for-testing'
    
    headers = {'Authorization': f'Token {token}'}
    
    # Test platform services endpoint
    try:
        ps_response = requests.get(
            "https://trackfutura.futureobjects.io/api/workflow/api/platform-services/",
            headers=headers,
            timeout=30
        )
        print(f"Platform services status: {ps_response.status_code}")
        if ps_response.status_code == 200:
            platform_services = ps_response.json()
            print(f"Platform services count: {len(platform_services)}")
            if platform_services:
                print("Available platform services:")
                for ps in platform_services[:3]:
                    print(f"  - {ps}")
        else:
            print(f"Platform services error: {ps_response.text[:200]}")
    except Exception as e:
        print(f"Platform services request failed: {e}")
    
    # Test workflow creation
    try:
        # First let's try the input-collections endpoint (which is the main workflow viewset)
        workflow_data = {
            "name": "Test Nike Search",
            "description": "Test workflow for Nike search",
            "project": 1,  # Project ID that exists now
            "urls": ["https://instagram.com/nike"],
            "platform_service": 1,  # Platform service ID that exists now
            "status": "active"
        }
        
        workflow_response = requests.post(
            "https://trackfutura.futureobjects.io/api/workflow/input-collections/",
            headers=headers,
            json=workflow_data,
            timeout=30
        )
        
        print(f"Workflow creation status: {workflow_response.status_code}")
        if workflow_response.status_code in [200, 201]:
            try:
                workflow = workflow_response.json()
                print(f"✅ Input Collection created! ID: {workflow.get('id', 'Unknown')}")
                print(f"Name: {workflow.get('name', 'Unknown')}")
                print(f"Status: {workflow.get('status', 'Unknown')}")
                print(f"Full response: {workflow}")
            except:
                print("✅ Input Collection created! (Response is not JSON)")
                print(f"Response content: {workflow_response.text[:200]}")
        else:
            print(f"❌ Input Collection creation failed: {workflow_response.text[:300]}")
            
    except Exception as e:
        print(f"Workflow creation request failed: {e}")

if __name__ == '__main__':
    test_production_workflow()