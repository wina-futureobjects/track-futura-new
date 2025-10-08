#!/usr/bin/env python3
"""
Fix BrightData execution by using the correct workflow
"""
import requests
import json
import time

BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def fix_brightdata_execution():
    print("🔧 FIXING BRIGHTDATA EXECUTION - USING CORRECT WORKFLOW")
    print("=" * 60)
    
    # Step 1: Create a BrightData batch job (correct way)
    print("1️⃣ Creating BrightData batch job...")
    
    batch_job_data = {
        "name": f"Test BrightData Fix {int(time.time())}",
        "project": 1,
        "source_folder_ids": [],
        "platforms_to_scrape": ["instagram"],
        "content_types_to_scrape": {
            "instagram": ["posts"]
        },
        "num_of_posts": 5,
        "auto_create_folders": True,
        "output_folder_pattern": "instagram_data"
    }
    
    print(f"   Creating batch job: {json.dumps(batch_job_data, indent=2)}")
    
    # Create batch job
    batch_response = requests.post(
        f"{BASE_URL}/api/brightdata/batch-jobs/",
        json=batch_job_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   Batch job creation status: {batch_response.status_code}")
    print(f"   Response: {batch_response.text}")
    
    if batch_response.status_code == 201:
        batch_job = batch_response.json()
        batch_job_id = batch_job['id']
        print(f"   ✅ Batch job created successfully! ID: {batch_job_id}")
        
        # Step 2: Execute the batch job (this triggers BrightData API)
        print(f"\n2️⃣ Executing batch job {batch_job_id}...")
        
        execute_response = requests.post(
            f"{BASE_URL}/api/brightdata/batch-jobs/{batch_job_id}/execute/",
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Execute status: {execute_response.status_code}")
        print(f"   Execute response: {execute_response.text}")
        
        if execute_response.status_code == 200:
            print("   ✅ BATCH JOB EXECUTION STARTED!")
            print("   ✅ This should trigger BrightData API requests!")
            
            # Step 3: Check scraper requests
            print(f"\n3️⃣ Checking scraper requests...")
            time.sleep(5)  # Wait a bit for requests to be created
            
            scraper_response = requests.get(
                f"{BASE_URL}/api/brightdata/scraper-requests/?batch_job_id={batch_job_id}"
            )
            
            print(f"   Scraper requests status: {scraper_response.status_code}")
            
            if scraper_response.status_code == 200:
                scraper_data = scraper_response.json()
                requests_count = scraper_data.get('count', 0)
                print(f"   📋 Scraper requests created: {requests_count}")
                
                if requests_count > 0:
                    for req in scraper_data.get('results', []):
                        print(f"     - Request {req['id']}: {req['platform']} - {req['status']}")
                        if req.get('snapshot_id'):
                            print(f"       🎯 BrightData snapshot_id: {req['snapshot_id']}")
                            print("       ✅ THIS MEANS BRIGHTDATA WAS TRIGGERED!")
                else:
                    print("     ⚠️ No scraper requests found yet")
            else:
                print(f"   ❌ Failed to get scraper requests: {scraper_response.text}")
                
            # Step 4: Monitor job status
            print(f"\n4️⃣ Monitoring job status...")
            status_response = requests.get(f"{BASE_URL}/api/brightdata/batch-jobs/{batch_job_id}/")
            
            if status_response.status_code == 200:
                job_status = status_response.json()
                print(f"   Job status: {job_status['status']}")
                print(f"   Created at: {job_status['created_at']}")
                if job_status.get('started_at'):
                    print(f"   Started at: {job_status['started_at']}")
                    
                print(f"\n🎯 BRIGHTDATA EXECUTION FIX COMPLETE!")
                print(f"   ✅ Batch job ID: {batch_job_id}")
                print(f"   ✅ Check your BrightData dashboard for incoming requests!")
                
            return True
            
        else:
            print(f"   ❌ Failed to execute batch job: {execute_response.text}")
            return False
            
    else:
        print(f"   ❌ Failed to create batch job: {batch_response.text}")
        return False

if __name__ == "__main__":
    fix_brightdata_execution()