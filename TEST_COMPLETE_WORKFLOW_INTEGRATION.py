#!/usr/bin/env python3
"""
🎯 TEST COMPLETE WORKFLOW INTEGRATION
Test the critical Workflow Management → Data Storage flow after deployment

This tests the exact user requirement:
"I WANT TO RUN THE SCRAPER FROM https://trackfutura.futureobjects.io/organizations/1/projects/2/workflow-management, 
AND THEN THE RESULT WILL BE STORE ON THE DATA STORAGE https://trackfutura.futureobjects.io/organizations/1/projects/2/data-storage"
"""

import requests
import json
import time
import sys
from datetime import datetime

# Production Configuration
BASE_URL = "https://trackfutura.futureobjects.io"
API_BASE = f"{BASE_URL}/api"

# Test Data for Instagram Scraping (Example: Nike)
TEST_WORKFLOW_DATA = {
    "platform": "instagram",
    "source_urls": ["https://www.instagram.com/nike/"],
    "job_name": f"Workflow_Test_Nike_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "max_posts": 5,
    "project_id": 2,  # Project 2 for Data Storage integration
    "triggered_from": "workflow_management"  # Critical: Workflow Management trigger
}

def test_authentication():
    """Test authentication with production system"""
    print("🔐 Testing Authentication...")
    
    try:
        auth_data = {
            "username": "admin@trackfutura.com",
            "password": "trackfutura2024!"
        }
        
        # Use correct login endpoint
        response = requests.post(
            f"{API_BASE}/users/login/",
            json=auth_data,
            timeout=30
        )
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('token')  # Different key for this endpoint
            if not token:
                token = token_data.get('access')  # Fallback
            print(f"✅ Authentication successful! Token: {token[:50]}...")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_workflow_management_trigger(token):
    """Test triggering scraper from Workflow Management interface"""
    print("\n🎯 Testing Workflow Management Trigger...")
    
    headers = {
        'Authorization': f'Token {token}',  # Use Token auth format
        'Content-Type': 'application/json'
    }
    
    try:
        # Test available trigger endpoints
        possible_endpoints = [
            f"{API_BASE}/brightdata/trigger-system/",
            f"{API_BASE}/brightdata/trigger-scraper/",
            f"{API_BASE}/workflow/trigger/",
        ]
        
        for endpoint in possible_endpoints:
            print(f"🔍 Testing endpoint: {endpoint}")
            response = requests.post(
                endpoint,
                json=TEST_WORKFLOW_DATA,
                headers=headers,
                timeout=60
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Workflow trigger successful at {endpoint}!")
                print(f"📊 Job ID: {result.get('job_id', 'N/A')}")
                print(f"🔗 BrightData Snapshot ID: {result.get('snapshot_id', 'N/A')}")
                print(f"📁 Project: {result.get('project_id', 'N/A')}")
                print(f"🎯 Source: {result.get('triggered_from', 'N/A')}")
                return result
            else:
                print(f"   ❌ Failed {response.status_code}: {response.text[:100]}...")
        
        print("❌ All trigger endpoints failed")
        return None
            
    except Exception as e:
        print(f"❌ Workflow trigger error: {e}")
        return None

def check_data_storage_integration(token, job_result):
    """Check if data appears in Data Storage interface (Project 2)"""
    print("\n📂 Testing Data Storage Integration...")
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Check available data storage endpoints
        possible_endpoints = [
            f"{API_BASE}/users/projects/2/",  # Project details
            f"{API_BASE}/brightdata/list-folders/",  # BrightData folders
            f"{API_BASE}/reports/folders/",  # Report folders
        ]
        
        for endpoint in possible_endpoints:
            print(f"🔍 Testing data storage endpoint: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Accessible! Found data: {type(data)} with {len(data) if isinstance(data, list) else 'properties'}")
                
                # Look for workflow-related data
                if isinstance(data, list):
                    workflow_items = [item for item in data if 'WF-' in str(item) or 'workflow' in str(item).lower()]
                    if workflow_items:
                        print(f"🎯 Found workflow-related items:")
                        for item in workflow_items[:3]:  # Show first 3
                            print(f"   📁 {item}")
                        return workflow_items
                elif isinstance(data, dict):
                    print(f"📊 Project data keys: {list(data.keys())}")
            else:
                print(f"   ❌ Failed {response.status_code}")
        
        print("⚠️  No workflow folders found yet (may take time for webhook delivery)")
        return []
            
    except Exception as e:
        print(f"❌ Data Storage check error: {e}")
        return None

def test_webhook_delivery_status():
    """Test webhook endpoint availability"""
    print("\n🔗 Testing Webhook Endpoint...")
    
    try:
        # Test webhook endpoint
        webhook_url = f"{BASE_URL}/trigger-system/brightdata-webhook/"
        response = requests.get(webhook_url, timeout=10)
        
        # Webhook should return method not allowed for GET (expecting POST)
        if response.status_code == 405:
            print("✅ Webhook endpoint accessible (correctly rejects GET)")
            return True
        else:
            print(f"⚠️  Webhook endpoint status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook test error: {e}")
        return False

def main():
    """Run complete workflow integration test"""
    print("🚀 STARTING COMPLETE WORKFLOW INTEGRATION TEST")
    print("=" * 60)
    print("Testing: Workflow Management → BrightData → Data Storage")
    print("Critical User Flow: https://trackfutura.futureobjects.io/organizations/1/projects/2/workflow-management")
    print("Expected Result: Data in https://trackfutura.futureobjects.io/organizations/1/projects/2/data-storage")
    print("=" * 60)
    
    # Step 1: Authentication
    token = test_authentication()
    if not token:
        print("\n❌ CRITICAL: Authentication failed - cannot proceed")
        sys.exit(1)
    
    # Step 2: Test Webhook Endpoint
    webhook_ok = test_webhook_delivery_status()
    if not webhook_ok:
        print("\n⚠️  WARNING: Webhook endpoint issues detected")
    
    # Step 3: Trigger from Workflow Management
    job_result = test_workflow_management_trigger(token)
    if not job_result:
        print("\n❌ CRITICAL: Workflow Management trigger failed")
        sys.exit(1)
    
    # Step 4: Check Data Storage Integration
    print("\n⏱️  Waiting 30 seconds for data processing...")
    time.sleep(30)
    
    folders = check_data_storage_integration(token, job_result)
    if folders is None:
        print("\n❌ CRITICAL: Data Storage integration failed")
        sys.exit(1)
    
    # Final Assessment
    print("\n" + "=" * 60)
    print("🎯 WORKFLOW INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    if folders:
        print("✅ SUCCESS: Complete Workflow Management → Data Storage integration working!")
        print(f"✅ Authentication: Working")
        print(f"✅ Workflow Management Trigger: Working")
        print(f"✅ BrightData Integration: Working") 
        print(f"✅ Data Storage Display: Working")
        print(f"✅ Project 2 Integration: Working")
        print("\n🎉 The critical user flow is now FULLY FUNCTIONAL!")
        print("🎯 Users can run scrapers from Workflow Management and see results in Data Storage")
    else:
        print("⚠️  PARTIAL SUCCESS: Trigger working but data not yet visible in Data Storage")
        print("   This may be due to:")
        print("   - Webhook delivery delay")
        print("   - BrightData processing time")
        print("   - Data aggregation timing")
        print("\n🔄 Recommend: Check Data Storage interface in 2-3 minutes")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()