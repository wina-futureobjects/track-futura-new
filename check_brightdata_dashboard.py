#!/usr/bin/env python
"""
URGENT: Check BrightData job execution status
"""
import requests
import json

def check_brightdata_dashboard():
    print("🔍 CHECKING BRIGHTDATA DASHBOARD DIRECTLY...")
    
    # Your actual BrightData credentials
    api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    scraper_id = "hl_f7614f18"
    
    # Test different BrightData API endpoints to see jobs
    endpoints_to_test = [
        f"https://api.brightdata.com/datasets/v3/{scraper_id}/runs",
        f"https://api.brightdata.com/datasets/v3/{scraper_id}/trigger",
        f"https://api.brightdata.com/datasets/v3/{scraper_id}/status",
        f"https://api.brightdata.com/datasets/v3/{scraper_id}",
        f"https://api.brightdata.com/datasets/{scraper_id}/runs",
        f"https://api.brightdata.com/scrapers/{scraper_id}/runs",
    ]
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    for endpoint in endpoints_to_test:
        try:
            print(f"\n🧪 Testing: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ SUCCESS! Response: {json.dumps(data, indent=2)[:500]}...")
                    
                    # Check for runs or jobs
                    if isinstance(data, dict):
                        if 'runs' in data:
                            print(f"🏃 Found {len(data['runs'])} runs")
                        if 'jobs' in data:
                            print(f"💼 Found {len(data['jobs'])} jobs")
                        if 'status' in data:
                            print(f"📊 Status: {data['status']}")
                    elif isinstance(data, list):
                        print(f"📋 Found {len(data)} items")
                        
                except json.JSONDecodeError:
                    print(f"✅ SUCCESS! Response (non-JSON): {response.text[:200]}...")
            else:
                print(f"❌ Error: {response.text[:200]}...")
                
        except Exception as e:
            print(f"💥 Exception: {e}")

def test_manual_trigger():
    print("\n🚀 TESTING MANUAL BRIGHTDATA TRIGGER...")
    
    api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    scraper_id = "hl_f7614f18"
    
    # Try to manually trigger a job
    trigger_endpoints = [
        f"https://api.brightdata.com/datasets/v3/{scraper_id}/trigger",
        f"https://api.brightdata.com/datasets/{scraper_id}/trigger",
    ]
    
    payload = {
        "url": "https://instagram.com/nike",
        "posts_limit": 5
    }
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    for endpoint in trigger_endpoints:
        try:
            print(f"\n🎯 Triggering: {endpoint}")
            response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:300]}...")
            
            if response.status_code in [200, 201, 202]:
                print("✅ JOB TRIGGERED SUCCESSFULLY!")
                return True
                
        except Exception as e:
            print(f"💥 Exception: {e}")
    
    return False

if __name__ == '__main__':
    print("🚨 URGENTLY CHECKING BRIGHTDATA STATUS...")
    check_brightdata_dashboard()
    
    print("\n" + "="*50)
    test_manual_trigger()
    
    print("\n🔗 Check your dashboard: https://brightdata.com/cp/scrapers/api/logs?id=hl_f7614f18")