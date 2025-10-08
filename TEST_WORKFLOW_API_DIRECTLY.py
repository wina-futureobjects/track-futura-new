#!/usr/bin/env python3
"""
Direct API test for workflow management functionality
"""
import requests
import json
import sys

def test_workflow_api():
    """Test the workflow management API endpoints directly"""
    
    # Base URL for the production API
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("🔍 Testing Workflow Management API...")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    # Test 1: Check available platforms
    try:
        print("1. Testing available platforms endpoint...")
        platforms_url = f"{base_url}/api/workflow/available-platforms/"
        
        response = requests.get(platforms_url, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            platforms_data = response.json()
            print(f"   ✅ Platforms available: {len(platforms_data)}")
            if platforms_data:
                print(f"   📋 Platform names: {[p.get('name', 'Unknown') for p in platforms_data]}")
            else:
                print("   ⚠️  No platforms found in response")
        else:
            print(f"   ❌ Failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    
    # Test 2: Check platform services
    try:
        print("2. Testing platform services endpoint...")
        services_url = f"{base_url}/api/workflow/platform-services/"
        
        response = requests.get(services_url, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            services_data = response.json()
            print(f"   ✅ Platform services available: {len(services_data)}")
            if services_data:
                print(f"   📋 First few services: {services_data[:3]}")
            else:
                print("   ⚠️  No platform services found")
        else:
            print(f"   ❌ Failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    
    # Test 3: Check if the main page is accessible
    try:
        print("3. Testing main workflow page accessibility...")
        main_page_url = f"{base_url}/organizations/2/projects/3/workflow-management"
        
        response = requests.get(main_page_url, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Workflow management page is accessible")
            if "workflow" in response.text.lower():
                print("   ✅ Page contains workflow content")
            else:
                print("   ⚠️  Page accessible but may not contain expected content")
        elif response.status_code == 404:
            print("   ❌ Page not found - routing issue")
        else:
            print(f"   ❌ Page returned status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error accessing page: {str(e)}")
    
    print()
    print("-" * 50)
    print("🎯 API Test Summary Complete")

if __name__ == "__main__":
    test_workflow_api()