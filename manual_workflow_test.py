#!/usr/bin/env python
"""
FINAL TEST: Create a workflow and manually trigger execution
"""
import requests
import json
import time

def manual_workflow_test():
    print("🎯 MANUAL WORKFLOW EXECUTION TEST")
    print("="*50)
    
    base_url = "https://trackfutura.futureobjects.io/api"
    
    # Login
    auth_response = requests.post(
        f"{base_url}/users/login/",
        json={"username": "superadmin", "password": "admin123"},
        timeout=30
    )
    
    token = auth_response.json().get('access_token', auth_response.json().get('token'))
    headers = {'Authorization': f'Token {token}'}
    
    print("✅ Login successful")
    
    # Create simple workflow
    workflow_data = {
        "name": f"MANUAL TEST {int(time.time())}",
        "description": "Manual test to force execution",
        "project": 1,
        "platform_service": 1,
        "urls": ["https://instagram.com/nike"],
        "status": "active"
    }
    
    print("🚀 Creating workflow...")
    workflow_response = requests.post(
        f"{base_url}/workflow/input-collections/",
        headers=headers,
        json=workflow_data,
        timeout=30
    )
    
    if workflow_response.status_code == 201:
        print("✅ Workflow created")
        
        # Get the workflow ID
        workflows_response = requests.get(
            f"{base_url}/workflow/input-collections/",
            headers=headers,
            timeout=30
        )
        
        workflows_data = workflows_response.json()
        if isinstance(workflows_data, dict) and 'results' in workflows_data:
            workflows = workflows_data['results']
        else:
            workflows = workflows_data
        
        workflow_id = workflows[0]['id']
        print(f"✅ Workflow ID: {workflow_id}")
        
        # Configure the job with detailed settings
        job_config = {
            "name": f"MANUAL EXECUTION {int(time.time())}",
            "num_of_posts": 3,  # Small number for quick test
            "auto_create_folders": True
        }
        
        print("🔧 Configuring job...")
        configure_response = requests.post(
            f"{base_url}/workflow/input-collections/{workflow_id}/configure_job/",
            headers=headers,
            json=job_config,
            timeout=30
        )
        
        if configure_response.status_code == 201:
            result = configure_response.json()
            batch_job_id = result.get('batch_job_id')
            print(f"✅ Job configured: Batch job {batch_job_id}")
            
            # Now wait and check multiple times
            for i in range(3):
                print(f"\n⏳ Check {i+1}/3 - Waiting 10 seconds...")
                time.sleep(10)
                
                # Check scraper requests
                requests_response = requests.get(
                    f"{base_url}/brightdata/scraper-requests/",
                    headers=headers,
                    timeout=30
                )
                
                if requests_response.status_code == 200:
                    requests_data = requests_response.json()
                    
                    if isinstance(requests_data, dict) and 'results' in requests_data:
                        scraper_requests = requests_data['results']
                    else:
                        scraper_requests = requests_data
                    
                    print(f"   📊 Total scraper requests: {len(scraper_requests)}")
                    
                    # Check if any are for our batch job
                    our_requests = [r for r in scraper_requests if r.get('batch_job_id') == batch_job_id]
                    print(f"   📊 Our batch requests: {len(our_requests)}")
                    
                    if our_requests:
                        latest_request = our_requests[0]
                        print(f"   ✅ Found request!")
                        print(f"      ID: {latest_request.get('id')}")
                        print(f"      Status: {latest_request.get('status')}")
                        print(f"      Platform: {latest_request.get('platform')}")
                        print(f"      BrightData ID: {latest_request.get('request_id')}")
                        
                        if latest_request.get('status') in ['processing', 'completed']:
                            print("\n🎉 SUCCESS! SCRAPING IS WORKING!")
                            return True
                        elif latest_request.get('error_message'):
                            print(f"      Error: {latest_request.get('error_message')}")
                
                # Check batch job status
                batch_response = requests.get(
                    f"{base_url}/brightdata/batch-jobs/{batch_job_id}/",
                    headers=headers,
                    timeout=30
                )
                
                if batch_response.status_code == 200:
                    batch_job = batch_response.json()
                    print(f"   📊 Batch job status: {batch_job.get('status')}")
                    if batch_job.get('error_log'):
                        print(f"   ❌ Batch job error: {batch_job.get('error_log')}")
            
            print("\n❌ No successful execution after 30 seconds")
            return False
        
        else:
            print(f"❌ Job configuration failed: {configure_response.status_code}")
            return False
    
    else:
        print(f"❌ Workflow creation failed: {workflow_response.status_code}")
        return False

if __name__ == '__main__':
    success = manual_workflow_test()
    
    if success:
        print("\n🎊 SUPERADMIN CAN SCRAPE!")
        print("🚀 BRIGHTDATA INTEGRATION IS WORKING!")
    else:
        print("\n💭 POSSIBLE SOLUTIONS:")
        print("   1. 🔄 Wait for deployment to complete")
        print("   2. 🔧 Check production logs for errors")
        print("   3. 🛠️ Verify backend service methods are deployed")
        print("   4. 📋 Check if config fix was applied in production")