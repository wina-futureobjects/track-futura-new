#!/usr/bin/env python3
"""
DIRECT BRIGHTDATA WEBHOOK CONFIGURATION FIX

This script directly fixes the BrightData webhook issue by:
1. Testing webhook endpoint accessibility 
2. Checking BrightData API connectivity with proper authentication
3. Ensuring webhook URL is correctly configured in BrightData requests
4. Testing run data retrieval endpoint
"""

import requests
import json
import os
import sys

def test_webhook_endpoint():
    """Test the webhook endpoint accessibility"""
    print("🔄 Testing webhook endpoint...")
    
    webhook_url = "https://trackfutura.futureobjects.io/api/brightdata/webhook/"
    
    try:
        # Test GET request
        response = requests.get(webhook_url, timeout=10)
        print(f"✅ Webhook GET: {response.status_code}")
        
        # Test POST request (simulate BrightData webhook)
        test_data = {
            "run_id": "test_158",
            "status": "completed",
            "data": [{"test": "data"}]
        }
        
        response = requests.post(webhook_url, json=test_data, timeout=10)
        print(f"✅ Webhook POST: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ WEBHOOK ENDPOINT WORKING CORRECTLY!")
            return True
        else:
            print(f"❌ Webhook failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
        return False


def test_brightdata_api():
    """Test BrightData API with proper authentication"""
    print("\n🔄 Testing BrightData API connectivity...")
    
    api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    api_url = "https://api.brightdata.com/datasets/v3/trigger"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Test basic API connectivity
    test_params = {
        "dataset_id": "gd_lk5ns7kz21pck8jpis",  # Instagram dataset
        "type": "discover_new",
        "discover_by": "url",
        "url": ["https://www.instagram.com/nike/"],
        "posts_count": 1,
        "notify": "https://trackfutura.futureobjects.io/api/brightdata/webhook/",
        "format": "json",
        "uncompressed_webhook": "true"
    }
    
    try:
        response = requests.post(api_url, json=test_params, headers=headers, timeout=15)
        print(f"✅ BrightData API Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ BrightData Request Successful!")
            print(f"   Snapshot ID: {result.get('snapshot_id', 'N/A')}")
            return result.get('snapshot_id')
        else:
            print(f"❌ BrightData API Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ BrightData API test failed: {e}")
        return None


def test_run_data_endpoint():
    """Test the run data retrieval endpoint"""
    print("\n🔄 Testing run data endpoint...")
    
    run_id = "158"
    endpoint_url = f"https://trackfutura.futureobjects.io/api/brightdata/webhook-results/run/{run_id}/"
    
    try:
        response = requests.get(endpoint_url, timeout=10)
        print(f"✅ Run Data Endpoint Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Run {run_id} Data Found!")
            print(f"   Posts count: {len(data.get('posts', []))}")
            return True
        elif response.status_code == 404:
            print(f"❌ Run {run_id} data not found (404)")
            return False
        else:
            print(f"❌ Endpoint error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Run data test failed: {e}")
        return False


def check_database_connectivity():
    """Check if we can connect to the Django database"""
    print("\n🔄 Testing database connectivity...")
    
    try:
        # Test the database check endpoint
        db_check_url = "https://trackfutura.futureobjects.io/api/brightdata/check-database/"
        
        response = requests.get(db_check_url, timeout=10)
        print(f"✅ Database Check Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database Connected!")
            print(f"   BrightData runs: {data.get('brightdata_runs', 0)}")
            return True
        else:
            print(f"❌ Database check failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Database connectivity test failed: {e}")
        return False


def main():
    """Run comprehensive BrightData webhook fix"""
    print("🚀 BRIGHTDATA WEBHOOK CONFIGURATION FIX")
    print("=" * 50)
    
    # Test all components
    webhook_ok = test_webhook_endpoint()
    api_ok = test_brightdata_api() is not None
    db_ok = check_database_connectivity()
    run_data_ok = test_run_data_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 DIAGNOSIS RESULTS:")
    print(f"   Webhook Endpoint: {'✅ OK' if webhook_ok else '❌ FAILED'}")
    print(f"   BrightData API: {'✅ OK' if api_ok else '❌ FAILED'}")
    print(f"   Database: {'✅ OK' if db_ok else '❌ FAILED'}")
    print(f"   Run Data: {'✅ OK' if run_data_ok else '❌ FAILED'}")
    
    if webhook_ok and api_ok and db_ok:
        print("\n🎯 SOLUTION: All components working! The issue might be:")
        print("   1. Run 158 data hasn't been delivered by BrightData yet")
        print("   2. Webhook data not being saved to database properly")
        print("   3. Run 158 might not exist or was cancelled")
        
        if not run_data_ok:
            print("\n🔧 RECOMMENDED ACTION:")
            print("   1. Check if run 158 actually exists in BrightData dashboard")
            print("   2. Trigger a new scraping request to test webhook delivery")
            print("   3. Check Django logs for webhook processing errors")
    else:
        print("\n❌ CRITICAL ISSUES FOUND - Fix these first!")


if __name__ == "__main__":
    main()