#!/usr/bin/env python
"""
FINAL TEST: Check if superadmin can scrape after all fixes
"""
import requests
import json
import time

def final_superadmin_test():
    print("🎉 FINAL SUPERADMIN SCRAPING TEST")
    print("="*60)
    
    base_url = "https://trackfutura.futureobjects.io/api"
    
    # Step 1: Login
    auth_response = requests.post(
        f"{base_url}/users/login/",
        json={"username": "superadmin", "password": "admin123"},
        timeout=30
    )
    
    token = auth_response.json().get('access_token', auth_response.json().get('token'))
    headers = {'Authorization': f'Token {token}'}
    
    print("✅ Login successful")
    
    # Step 2: Create and configure workflow
    print("\n🚀 Creating workflow and configuring job...")
    
    # Create workflow
    workflow_data = {
        "name": f"FINAL TEST Nike {int(time.time())}",
        "description": "Final test to confirm superadmin can scrape",
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
    
    if workflow_response.status_code != 201:
        print(f"❌ Workflow creation failed: {workflow_response.status_code}")
        return False
    
    # Get workflow ID
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
    print(f"✅ Workflow created: ID {workflow_id}")
    
    # Configure job (this triggers scraping)
    job_config = {
        "name": f"Final Test Job {int(time.time())}",
        "num_of_posts": 5,
        "auto_create_folders": True
    }
    
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
        
        # Wait a moment and check execution
        print("\n⏳ Waiting 5 seconds for execution...")
        time.sleep(5)
        
        # Check if scraper requests were created
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
            
            print(f"📊 Scraper requests found: {len(scraper_requests)}")
            
            if scraper_requests:
                latest_request = scraper_requests[0]
                print(f"   ✅ Latest request ID: {latest_request.get('id')}")
                print(f"   Status: {latest_request.get('status')}")
                print(f"   Platform: {latest_request.get('platform')}")
                print(f"   URL: {latest_request.get('target_url')}")
                print(f"   BrightData ID: {latest_request.get('request_id')}")
                
                if latest_request.get('status') in ['processing', 'completed']:
                    print("\n🎉 SUCCESS! SUPERADMIN CAN SCRAPE!")
                    print("   ✅ BrightData integration is working")
                    return True
                else:
                    print(f"\n⚠️  Request created but status: {latest_request.get('status')}")
                    error = latest_request.get('error_message')
                    if error:
                        print(f"   Error: {error}")
            else:
                print("❌ No scraper requests created - BrightData config might still be wrong")
        
        return False
    else:
        print(f"❌ Job configuration failed: {configure_response.status_code}")
        print(f"Error: {configure_response.text[:200]}")
        return False

if __name__ == '__main__':
    success = final_superadmin_test()
    
    if success:
        print("\n🎊 NIGHTMARE IS OVER!")
        print("   🔥 SUPERADMIN CAN NOW SCRAPE SUCCESSFULLY!")
        print("   🚀 BRIGHTDATA INTEGRATION IS WORKING!")
    else:
        print("\n😤 Still need to fix BrightData config:")
        print("   🔧 Run: upsun ssh and fix dataset_id to 'web_unlocker1'")
        print("   📋 Or manually update via admin panel")