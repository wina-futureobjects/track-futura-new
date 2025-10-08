#!/usr/bin/env python3
"""
Simple test to check BrightData status
"""

import requests
import json

def simple_test():
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("🧪 SIMPLE BRIGHTDATA STATUS CHECK")
    print("=" * 50)
    
    # Test 1: Check health
    print("\n1. Health Check...")
    try:
        response = requests.get(f"{base_url}/health/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Server is healthy")
        else:
            print(f"   ❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Raw scraper trigger
    print("\n2. Raw Scraper Trigger Test...")
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json={"platform": "instagram", "urls": ["https://www.instagram.com/nike/"]},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Raw response: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    print("   ✅ SUCCESS! BrightData trigger working!")
                    print(f"   Dataset ID: {data.get('dataset_id')}")
                    print(f"   Platform: {data.get('platform')}")
                else:
                    print(f"   ❌ Failed: {data.get('error')}")
            except json.JSONDecodeError:
                print("   ❌ Invalid JSON response")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Request error: {e}")
    
    # Test 3: Config endpoint
    print("\n3. Configuration Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/brightdata/configs/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Raw response: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Data type: {type(data)}")
                if isinstance(data, list):
                    print(f"   ✅ Found {len(data)} configurations")
                else:
                    print(f"   Data structure: {data}")
            except json.JSONDecodeError:
                print("   ❌ Invalid JSON in config response")
        
    except Exception as e:
        print(f"   ❌ Config check error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print("If you see 'SUCCESS! BrightData trigger working!' above,")
    print("then your integration is 100% complete! 🚀")
    print("\nIf not, the database configurations need to be created.")

if __name__ == "__main__":
    simple_test()