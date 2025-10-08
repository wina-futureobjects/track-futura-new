#!/usr/bin/env python
"""
URGENT: Debug why scraper jobs are failing
"""
import requests
import json
import time

def debug_scraper_failure():
    print("🚨 DEBUGGING SCRAPER FAILURE")
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
    
    # Get the latest batch job details
    jobs_response = requests.get(
        f"{base_url}/brightdata/batch-jobs/",
        headers=headers,
        timeout=30
    )
    
    if jobs_response.status_code == 200:
        jobs_data = jobs_response.json()
        
        if isinstance(jobs_data, dict) and 'results' in jobs_data:
            jobs = jobs_data['results']
        else:
            jobs = jobs_data
            
        if jobs:
            latest_job = jobs[0]
            job_id = latest_job.get('id')
            
            print(f"🔍 Latest job details:")
            print(f"   ID: {job_id}")
            print(f"   Name: {latest_job.get('name')}")
            print(f"   Status: {latest_job.get('status')}")
            print(f"   Error: {latest_job.get('error_log', 'None')}")
            print(f"   Created: {latest_job.get('created_at', '')[:19]}")
            print(f"   Started: {latest_job.get('started_at', 'Not started')}")
            print(f"   Completed: {latest_job.get('completed_at', 'Not completed')}")
            print(f"   Total requests: {latest_job.get('total_requests', 0)}")
            print(f"   Successful: {latest_job.get('successful_requests', 0)}")
            print(f"   Failed: {latest_job.get('failed_requests', 0)}")
            
            # Check if the job has any scraper requests
            requests_response = requests.get(
                f"{base_url}/brightdata/scraper-requests/?batch_job={job_id}",
                headers=headers,
                timeout=30
            )
            
            if requests_response.status_code == 200:
                requests_data = requests_response.json()
                
                if isinstance(requests_data, dict) and 'results' in requests_data:
                    scraper_requests = requests_data['results']
                else:
                    scraper_requests = requests_data
                    
                print(f"\n📋 Scraper requests for job {job_id}: {len(scraper_requests)}")
                
                for req in scraper_requests:
                    print(f"   Request {req.get('id')}:")
                    print(f"     Platform: {req.get('platform')}")
                    print(f"     Status: {req.get('status')}")
                    print(f"     URL: {req.get('target_url', '')[:50]}...")
                    print(f"     BrightData ID: {req.get('request_id', 'None')}")
                    print(f"     Error: {req.get('error_message', 'None')}")
                    print()
            
            # If job is failed, let's see if we can get more details
            if latest_job.get('status') == 'failed':
                print(f"\n❌ Job {job_id} FAILED!")
                print(f"   Error log: {latest_job.get('error_log', 'No error log available')}")
                
                # Check if we can retry the job
                print(f"   🔄 Attempting to retry job...")
                retry_response = requests.post(
                    f"{base_url}/brightdata/batch-jobs/{job_id}/retry/",
                    headers=headers,
                    timeout=30
                )
                
                if retry_response.status_code in [200, 201]:
                    print(f"   ✅ Job retry triggered successfully!")
                else:
                    print(f"   ❌ Job retry failed: {retry_response.status_code}")
                    print(f"   Error: {retry_response.text[:200]}")
    
    print("\n🔧 NEXT STEPS:")
    print("   1. Check error logs for specific failure reasons")
    print("   2. Verify BrightData service is working properly")
    print("   3. Test BrightData API directly if needed")
    print("   4. Check if missing methods in backend service")

if __name__ == '__main__':
    debug_scraper_failure()