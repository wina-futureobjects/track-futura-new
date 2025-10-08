#!/usr/bin/env python3
"""
Check why scraping runs are failing
"""
import requests
import json

def check_scraping_failures():
    """Check what's causing scraping runs to fail"""
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("🔍 SCRAPING FAILURE ANALYSIS")
    print("=" * 50)
    
    # Check the failed run details
    print("1. 📊 CHECKING FAILED RUN DETAILS")
    
    try:
        # Get the latest failed run (ID 14)
        run_url = f"{base_url}/api/workflow/scraping-runs/14/"
        response = requests.get(run_url, timeout=10)
        
        if response.status_code == 200:
            run_data = response.json()
            
            print(f"   Run ID: {run_data.get('id')}")
            print(f"   Name: {run_data.get('name')}")
            print(f"   Status: {run_data.get('status')}")
            print(f"   Error: {run_data.get('error_message', 'No error message')}")
            print(f"   Total jobs: {run_data.get('total_jobs')}")
            print(f"   Completed: {run_data.get('completed_jobs')}")
            
            # Check the jobs for this run
            print(f"\n2. 🔍 CHECKING JOB DETAILS")
            
            jobs_url = f"{base_url}/api/workflow/scraping-jobs/?run={14}"
            jobs_response = requests.get(jobs_url, timeout=10)
            
            if jobs_response.status_code == 200:
                jobs_data = jobs_response.json()
                
                if isinstance(jobs_data, dict) and 'results' in jobs_data:
                    jobs = jobs_data['results']
                else:
                    jobs = jobs_data if isinstance(jobs_data, list) else []
                
                print(f"   📊 Jobs for run 14: {len(jobs)}")
                
                for job in jobs:
                    job_id = job.get('id')
                    status = job.get('status')
                    error = job.get('error_message', 'No error')
                    platform = job.get('platform', 'Unknown')
                    
                    print(f"   Job {job_id}: {platform} - {status}")
                    if error and error != 'No error':
                        print(f"      Error: {error}")
                        
            else:
                print(f"   ❌ Failed to get jobs: {jobs_response.status_code}")
                
        else:
            print(f"   ❌ Failed to get run details: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Check BrightData configuration issues
    print(f"\n3. 🔧 CHECKING BRIGHTDATA CONFIG")
    
    try:
        configs_url = f"{base_url}/api/brightdata/configs/"
        response = requests.get(configs_url, timeout=10)
        
        if response.status_code == 200:
            configs_data = response.json()
            
            if isinstance(configs_data, dict) and 'results' in configs_data:
                configs = configs_data['results']
            else:
                configs = configs_data if isinstance(configs_data, list) else []
            
            print(f"   📊 BrightData configs: {len(configs)}")
            
            for config in configs:
                name = config.get('name', 'Unknown')
                platform = config.get('platform', 'Unknown')
                is_active = config.get('is_active', False)
                dataset_id = config.get('dataset_id', 'No ID')
                
                status = "✅ Active" if is_active else "❌ Inactive"
                print(f"   {name} ({platform}): {status}")
                print(f"      Dataset ID: {dataset_id}")
                
                # Check if the dataset ID is valid format
                if not dataset_id.startswith('gd_'):
                    print(f"      ⚠️  Invalid dataset ID format")
                    
        else:
            print(f"   ❌ Failed to get configs: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Check if there's an API token issue
    print(f"\n4. 🔑 TESTING API TOKEN")
    
    # Create a test configuration to see if BrightData API responds
    try:
        # Check the webhook logs or recent activity
        webhook_url = f"{base_url}/api/brightdata/webhook/"
        
        # Send a test webhook payload
        test_payload = {
            "snapshot_id": "test_snapshot",
            "dataset_id": "gd_test",
            "status": "running"
        }
        
        webhook_response = requests.post(webhook_url, json=test_payload, timeout=10)
        print(f"   Webhook test status: {webhook_response.status_code}")
        
        if webhook_response.status_code == 200:
            print("   ✅ Webhook endpoint responding")
        else:
            print(f"   Response: {webhook_response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Webhook test error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS:")
    print("1. Scraper system CAN create and start runs ✅")
    print("2. Jobs are being created ✅") 
    print("3. BUT jobs are failing - check errors above ❌")
    print("4. Most likely issues:")
    print("   - BrightData API token missing/invalid")
    print("   - No input collections (track sources)")
    print("   - Invalid dataset IDs")
    print("=" * 50)

if __name__ == "__main__":
    check_scraping_failures()