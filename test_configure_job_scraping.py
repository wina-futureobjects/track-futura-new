#!/usr/bin/env python
"""
URGENT: Test superadmin scraping using configure_job endpoint
"""
import requests
import json
import time

def test_configure_job_workflow():
    print("🚨 TESTING SUPERADMIN SCRAPING VIA CONFIGURE_JOB")
    print("="*60)
    
    base_url = "https://trackfutura.futureobjects.io/api"
    
    # Step 1: Login as superadmin
    print("🔑 STEP 1: Logging in as superadmin...")
    try:
        auth_response = requests.post(
            f"{base_url}/users/login/",
            json={"username": "superadmin", "password": "admin123"},
            timeout=30
        )
        
        if auth_response.status_code == 200:
            data = auth_response.json()
            token = data.get('access_token', data.get('token'))
            print(f"   ✅ Login successful")
        else:
            print(f"   ❌ Login failed")
            return
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    headers = {'Authorization': f'Token {token}'}
    
    # Step 2: Create workflow
    print("\n🚀 STEP 2: Creating workflow...")
    try:
        workflow_data = {
            "name": f"Superadmin Configure Test {int(time.time())}",
            "description": "Test workflow using configure_job endpoint",
            "project": 1,
            "platform_service": 1,
            "urls": ["https://instagram.com/nike"],
            "status": "active"
        }
        
        workflow_response = requests.post(
            f"{base_url}/workflow/input-collections/",
            headers=headers,
            json=workflow_data,
            timeout=30
        )
        
        print(f"   Workflow creation status: {workflow_response.status_code}")
        
        if workflow_response.status_code in [200, 201]:
            print("   ✅ Workflow created successfully!")
        else:
            print(f"   ❌ Workflow creation failed")
            return
            
    except Exception as e:
        print(f"   ❌ Workflow creation error: {e}")
        return
    
    # Step 3: Get latest workflow
    print("\n📋 STEP 3: Getting latest workflow...")
    try:
        workflows_response = requests.get(
            f"{base_url}/workflow/input-collections/",
            headers=headers,
            timeout=30
        )
        
        if workflows_response.status_code == 200:
            workflows_data = workflows_response.json()
            
            if isinstance(workflows_data, dict) and 'results' in workflows_data:
                workflows = workflows_data['results']
            else:
                workflows = workflows_data
                
            if workflows:
                latest_workflow = workflows[0]
                workflow_id = latest_workflow.get('id')
                print(f"   ✅ Latest workflow ID: {workflow_id}")
            else:
                print("   ❌ No workflows found!")
                return
        else:
            print(f"   ❌ Failed to get workflows")
            return
            
    except Exception as e:
        print(f"   ❌ Error getting workflows: {e}")
        return
    
    # Step 4: Configure job (this triggers scraping)
    print("\n🎯 STEP 4: Configuring job to trigger scraping...")
    try:
        job_config = {
            "name": f"Auto Job for Nike {int(time.time())}",
            "num_of_posts": 10,
            "auto_create_folders": True
        }
        
        configure_response = requests.post(
            f"{base_url}/workflow/input-collections/{workflow_id}/configure_job/",
            headers=headers,
            json=job_config,
            timeout=30
        )
        
        print(f"   Configure job status: {configure_response.status_code}")
        
        if configure_response.status_code in [200, 201]:
            print("   ✅ Job configured successfully!")
            try:
                result = configure_response.json()
                print(f"   Response: {result}")
                batch_job_id = result.get('batch_job_id')
                if batch_job_id:
                    print(f"   🎉 Batch job created: {batch_job_id}")
            except:
                print(f"   Response: {configure_response.text[:200]}")
        else:
            print(f"   ❌ Job configuration failed: {configure_response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Job configuration error: {e}")
    
    print("\n" + "="*60)
    print("🎯 SUMMARY:")
    print("   This tests the existing configure_job endpoint")
    print("   which should trigger BrightData scraping")
    print("   ✅ If successful, superadmin can scrape!")

if __name__ == '__main__':
    test_configure_job_workflow()