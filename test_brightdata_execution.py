#!/usr/bin/env python
"""
URGENT: Test if BrightData is actually working in production
"""
import requests
import json
import time

def test_brightdata_execution():
    print("🚨 TESTING ACTUAL BRIGHTDATA EXECUTION")
    print("="*60)
    
    base_url = "https://trackfutura.futureobjects.io/api"
    
    # Login
    auth_response = requests.post(
        f"{base_url}/users/login/",
        json={"username": "superadmin", "password": "admin123"},
        timeout=30
    )
    
    token = auth_response.json().get('access_token', auth_response.json().get('token'))
    headers = {'Authorization': f'Token {token}'}
    
    print("🔍 STEP 1: Checking recent batch jobs...")
    try:
        # Check BrightData batch jobs
        jobs_response = requests.get(
            f"{base_url}/brightdata/batch-jobs/",
            headers=headers,
            timeout=30
        )
        
        print(f"   Batch jobs status: {jobs_response.status_code}")
        
        if jobs_response.status_code == 200:
            jobs_data = jobs_response.json()
            
            if isinstance(jobs_data, dict) and 'results' in jobs_data:
                jobs = jobs_data['results']
            else:
                jobs = jobs_data
                
            print(f"   ✅ Found {len(jobs)} batch jobs")
            
            # Show recent jobs
            for job in jobs[:3]:
                print(f"     - Job {job.get('id')}: {job.get('name')}")
                print(f"       Status: {job.get('status')}")
                print(f"       Created: {job.get('created_at', '')[:19]}")
                print(f"       Requests: {job.get('total_requests', 0)}")
                print()
        else:
            print(f"   ❌ Failed to get batch jobs: {jobs_response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error getting batch jobs: {e}")
    
    print("🔧 STEP 2: Checking BrightData configs...")
    try:
        configs_response = requests.get(
            f"{base_url}/brightdata/configs/",
            headers=headers,
            timeout=30
        )
        
        if configs_response.status_code == 200:
            configs_data = configs_response.json()
            
            if isinstance(configs_data, dict) and 'results' in configs_data:
                configs = configs_data['results']
            else:
                configs = configs_data
                
            print(f"   ✅ Found {len(configs)} configs")
            
            for config in configs:
                print(f"     - Platform: {config.get('platform')}")
                print(f"       Dataset ID: {config.get('dataset_id')}")
                print(f"       API Token: {config.get('api_token', '')[:20]}...")
                print(f"       Active: {config.get('is_active')}")
                
                # Check if it's using the wrong dataset_id
                if config.get('dataset_id') == 'hl_f7614f18':
                    print(f"       ⚠️  NEEDS FIX: Still using old dataset_id!")
                elif config.get('dataset_id') == 'web_unlocker1':
                    print(f"       ✅ CORRECT: Using proper zone name!")
                print()
        else:
            print(f"   ❌ Failed to get configs: {configs_response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error getting configs: {e}")
    
    print("🔍 STEP 3: Checking scraper requests...")
    try:
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
                
            print(f"   ✅ Found {len(scraper_requests)} scraper requests")
            
            # Show recent requests
            for req in scraper_requests[:3]:
                print(f"     - Request {req.get('id')}: {req.get('platform')}")
                print(f"       Status: {req.get('status')}")
                print(f"       URL: {req.get('target_url', '')[:50]}...")
                print(f"       Request ID: {req.get('request_id')}")
                print(f"       Error: {req.get('error_message', 'None')}")
                print()
        else:
            print(f"   ❌ Failed to get scraper requests: {requests_response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error getting scraper requests: {e}")
    
    print("\n" + "="*60)
    print("🎯 ANALYSIS:")
    print("   1. Check if batch jobs are being created")
    print("   2. Check if configs have correct zone (web_unlocker1)")
    print("   3. Check if scraper requests are executing")
    print("   4. If dataset_id is wrong, run fix script!")

if __name__ == '__main__':
    test_brightdata_execution()