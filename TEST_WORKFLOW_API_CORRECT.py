#!/usr/bin/env python3
"""
Correct API test for workflow management functionality with proper endpoints
"""
import requests
import json
import sys

def test_workflow_api_correct():
    """Test the workflow management API endpoints with correct URLs"""
    
    # Base URL for the production API
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("🔍 Testing Workflow Management API (Correct Endpoints)...")
    print(f"Base URL: {base_url}")
    print("-" * 60)
    
    # Test 1: Check available platforms (correct URL)
    try:
        print("1. Testing available platforms endpoint...")
        platforms_url = f"{base_url}/api/workflow/input-collections/available_platforms/"
        
        response = requests.get(platforms_url, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            platforms_data = response.json()
            print(f"   ✅ Platforms available: {len(platforms_data)}")
            if platforms_data:
                print(f"   📋 Platform names: {[p.get('name', 'Unknown') for p in platforms_data]}")
                print(f"   📋 Platform displays: {[p.get('display_name', 'Unknown') for p in platforms_data]}")
            else:
                print("   ⚠️  No platforms found in response")
        else:
            print(f"   ❌ Failed: {response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    
    # Test 2: Check platform services (correct URL)
    try:
        print("2. Testing platform services endpoint...")
        services_url = f"{base_url}/api/workflow/input-collections/platform_services/"
        
        response = requests.get(services_url, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            services_data = response.json()
            print(f"   ✅ Platform services available: {len(services_data)}")
            if services_data:
                print(f"   📋 First platform-service combination:")
                first_service = services_data[0]
                print(f"       Platform: {first_service.get('platform', {}).get('display_name', 'Unknown')}")
                print(f"       Service: {first_service.get('service', {}).get('display_name', 'Unknown')}")
                print(f"   📊 Total combinations: {len(services_data)}")
            else:
                print("   ⚠️  No platform services found")
        else:
            print(f"   ❌ Failed: {response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    
    # Test 3: Check input collections endpoint
    try:
        print("3. Testing input collections endpoint...")
        collections_url = f"{base_url}/api/workflow/input-collections/"
        
        response = requests.get(collections_url, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            collections_data = response.json()
            if isinstance(collections_data, dict) and 'results' in collections_data:
                # Paginated response
                total_count = collections_data.get('count', 0)
                results = collections_data.get('results', [])
                print(f"   ✅ Input collections endpoint working - Total: {total_count}, Current page: {len(results)}")
            elif isinstance(collections_data, list):
                # Direct list response
                print(f"   ✅ Input collections endpoint working - Found: {len(collections_data)} collections")
            else:
                print("   ✅ Input collections endpoint accessible")
        else:
            print(f"   ❌ Failed: {response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    
    # Test 4: Check if the main page is accessible
    try:
        print("4. Testing main workflow page accessibility...")
        main_page_url = f"{base_url}/organizations/2/projects/3/workflow-management"
        
        response = requests.get(main_page_url, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Workflow management page is accessible")
            if "workflow" in response.text.lower() or "react" in response.text.lower():
                print("   ✅ Page contains expected content")
            else:
                print("   ⚠️  Page accessible but may be showing fallback content")
        elif response.status_code == 404:
            print("   ❌ Page not found - routing issue")
        else:
            print(f"   ❌ Page returned status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error accessing page: {str(e)}")
    
    print()
    print("-" * 60)
    print("🎯 WORKFLOW API TEST RESULTS:")
    print("✅ = Working   ⚠️ = Partial   ❌ = Failed")
    print("-" * 60)

if __name__ == "__main__":
    test_workflow_api_correct()