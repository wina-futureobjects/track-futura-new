#!/usr/bin/env python3

import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

def debug_brightdata_execution():
    print('🔍 DEBUGGING BRIGHTDATA EXECUTION')
    print('=' * 60)
    
    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata'
    
    # 1. Test trigger endpoint
    print('\n1. TESTING TRIGGER ENDPOINT...')
    trigger_url = f'{base_url}/trigger-scraper/'
    
    response = requests.post(trigger_url, json={
        'platform': 'instagram',
        'data_type': 'posts',
        'urls': ['https://instagram.com/test']
    }, headers={'Content-Type': 'application/json'})
    
    print(f'   Status: {response.status_code}')
    print(f'   Response: {response.text}')
    
    if response.status_code != 200:
        print('❌ Trigger failed!')
        return
    
    # Get batch job ID
    batch_job_data = response.json()
    batch_job_id = batch_job_data.get('batch_job_id')
    print(f'   Created batch job: {batch_job_id}')
    
    # 2. Check batch job details
    print('\n2. CHECKING BATCH JOB DETAILS...')
    job_url = f'{base_url}/batch-jobs/{batch_job_id}/'
    
    response = requests.get(job_url)
    print(f'   Status: {response.status_code}')
    
    if response.status_code == 200:
        job_data = response.json()
        print(f'   Job status: {job_data.get("status")}')
        print(f'   Job progress: {job_data.get("progress", 0)}%')
        print(f'   Created at: {job_data.get("created_at")}')
    
    # 3. Check scraper requests for this job
    print('\n3. CHECKING SCRAPER REQUESTS...')
    requests_url = f'{base_url}/scraper-requests/?batch_job_id={batch_job_id}'
    
    response = requests.get(requests_url)
    print(f'   Status: {response.status_code}')
    
    if response.status_code == 200:
        requests_data = response.json()
        print(f'   Found {len(requests_data)} scraper requests')
        
        for req in requests_data:
            print(f'     Request {req.get("id")}: {req.get("status")} - {req.get("platform")}')
            if req.get('snapshot_id'):
                print(f'       Snapshot ID: {req.get("snapshot_id")}')
            if req.get('error_message'):
                print(f'       Error: {req.get("error_message")}')
    
    # 4. Test direct BrightData API
    print('\n4. TESTING DIRECT BRIGHTDATA API...')
    brightdata_token = os.getenv('BRIGHTDATA_API_TOKEN')
    
    if brightdata_token:
        headers = {
            'Authorization': f'Bearer {brightdata_token}',
            'Content-Type': 'application/json'
        }
        
        # Test dataset status
        try:
            collection_url = 'https://api.brightdata.com/dca/datasets/hl_f7614f18'
            response = requests.get(collection_url, headers=headers, timeout=10)
            print(f'   Dataset status: {response.status_code}')
            
            if response.status_code == 200:
                dataset_info = response.json()
                print(f'   Dataset name: {dataset_info.get("name", "Unknown")}')
                print(f'   Dataset status: {dataset_info.get("status", "Unknown")}')
                
                # Try to trigger a collection
                print('\n   Triggering test collection...')
                trigger_url = 'https://api.brightdata.com/dca/trigger_immediate?collector=hl_f7614f18'
                
                test_data = {
                    "url": "https://instagram.com/futureobjects",
                    "country": "US"
                }
                
                trigger_response = requests.post(trigger_url, json=test_data, headers=headers, timeout=30)
                print(f'   Trigger status: {trigger_response.status_code}')
                print(f'   Trigger response: {trigger_response.text[:200]}')
                
                if trigger_response.status_code == 200:
                    print('   ✅ BrightData is working! Data should appear in dashboard soon.')
                else:
                    print('   ❌ BrightData trigger failed!')
                    
            else:
                print(f'   ❌ Dataset not accessible: {response.text}')
                
        except Exception as e:
            print(f'   ❌ Error: {str(e)}')
    else:
        print('   ❌ No BrightData token found!')
    
    # 5. Monitor for a bit
    print('\n5. MONITORING FOR UPDATES...')
    for i in range(3):
        time.sleep(10)
        print(f'   Checking after {(i+1)*10} seconds...')
        
        # Check job status again
        response = requests.get(job_url)
        if response.status_code == 200:
            job_data = response.json()
            print(f'     Job status: {job_data.get("status")} ({job_data.get("progress", 0)}%)')
        
        # Check for webhook events
        webhook_url = f'{base_url}/webhook-events/'
        try:
            response = requests.get(webhook_url)
            if response.status_code == 200:
                events = response.json()
                recent_events = [e for e in events if e.get('platform') == 'instagram'][-3:]
                if recent_events:
                    print(f'     Recent webhook events: {len(recent_events)}')
                    for event in recent_events:
                        print(f'       Event {event.get("id")}: {event.get("status")}')
        except:
            pass
    
    print('\n📋 SUMMARY:')
    print('   - If trigger returns 200 but no data appears in BrightData dashboard:')
    print('     * Check BrightData dataset configuration')
    print('     * Verify API token has correct permissions')
    print('     * Check if dataset is active and not paused')
    print('   - If BrightData API returns success but webhook never fires:')
    print('     * Verify webhook URL is configured in BrightData dataset')
    print('     * Check if webhook URL is publicly accessible')
    print('   - Data may take a few minutes to appear in dashboard')

if __name__ == '__main__':
    debug_brightdata_execution()