#!/usr/bin/env python3
"""
🔍 EMERGENCY DATA INVESTIGATION - Run 158
Check what scraped data exists and fix the missing endpoint
"""

import requests
import json

BASE_URL = "https://trackfutura.futureobjects.io"
API_BASE = f"{BASE_URL}/api"

def check_run_158_data():
    """Check what data exists for run 158"""
    print("🔍 INVESTIGATING RUN 158 DATA")
    print("=" * 50)
    
    # Test different endpoints that might have the data
    endpoints_to_check = [
        "/api/brightdata/webhook-results/run/158/",
        "/api/brightdata/run/158/", 
        "/api/brightdata/job-results/158/",
        "/api/brightdata/data-storage/run/158/",
        "/api/reports/folders/",
        "/api/brightdata/list-folders/",
        "/api/brightdata/",
    ]
    
    for endpoint in endpoints_to_check:
        try:
            url = BASE_URL + endpoint
            print(f"\n🔍 Testing: {endpoint}")
            response = requests.get(url, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   ✅ Found {len(data)} items")
                        if data:
                            print(f"   📄 Sample: {data[0] if len(str(data[0])) < 100 else str(data[0])[:100]}...")
                    else:
                        print(f"   ✅ Found data: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                except:
                    print(f"   📄 Text response: {response.text[:200]}...")
            elif response.status_code == 404:
                print(f"   ❌ Not found")
            elif response.status_code == 405:
                print(f"   ⚠️  Method not allowed (endpoint exists)")
            else:
                print(f"   ⚠️  Status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_direct_brightdata_api():
    """Test BrightData API directly to see what data is available"""
    print("\n" + "=" * 50)
    print("🔍 TESTING DIRECT BRIGHTDATA API")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/brightdata/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ BrightData API accessible")
            print(f"📊 Available endpoints: {data}")
            
            # Test each available endpoint
            if isinstance(data, list):
                for endpoint_name in data:
                    try:
                        test_url = f"{API_BASE}/brightdata/{endpoint_name}/"
                        test_response = requests.get(test_url, timeout=5)
                        print(f"   📍 /{endpoint_name}/: {test_response.status_code}")
                        
                        if test_response.status_code == 200:
                            test_data = test_response.json()
                            if isinstance(test_data, list) and test_data:
                                print(f"      🔍 Found {len(test_data)} items")
                                # Look for run 158 data
                                run_158_items = [item for item in test_data if '158' in str(item)]
                                if run_158_items:
                                    print(f"      🎯 Run 158 related: {run_158_items}")
                    except Exception as e:
                        print(f"   ❌ Error testing {endpoint_name}: {e}")
        else:
            print(f"❌ BrightData API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ BrightData API error: {e}")

def check_for_scraped_data():
    """Check for any scraped data in the system"""
    print("\n" + "=" * 50)
    print("🔍 SEARCHING FOR ANY SCRAPED DATA")
    print("=" * 50)
    
    data_endpoints = [
        "/api/instagram_data/",
        "/api/instagram-data/",
        "/api/facebook-data/", 
        "/api/linkedin-data/",
        "/api/tiktok-data/",
        "/api/reports/",
    ]
    
    for endpoint in data_endpoints:
        try:
            url = BASE_URL + endpoint
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list) and data:
                        print(f"✅ {endpoint}: {len(data)} items found")
                        # Look for recent data
                        recent_items = data[:3] if len(data) >= 3 else data
                        for item in recent_items:
                            if isinstance(item, dict):
                                print(f"   📄 Item keys: {list(item.keys())}")
                            else:
                                print(f"   📄 Item: {item}")
                    elif isinstance(data, dict):
                        print(f"✅ {endpoint}: Dict with keys: {list(data.keys())}")
                    else:
                        print(f"⚠️  {endpoint}: Empty or different format")
                except:
                    print(f"📄 {endpoint}: Text response")
            elif response.status_code == 405:
                print(f"⚠️  {endpoint}: Endpoint exists (method not allowed)")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

def main():
    """Run complete data investigation"""
    print("🚨 EMERGENCY: FINDING SCRAPED DATA FOR RUN 158")
    print("User complaint: Data not showing at /api/brightdata/webhook-results/run/158/")
    print("Investigation: Find where the scraped data actually is")
    
    check_run_158_data()
    test_direct_brightdata_api()
    check_for_scraped_data()
    
    print("\n" + "=" * 60)
    print("🎯 INVESTIGATION COMPLETE")
    print("Next steps:")
    print("1. Fix missing webhook-results endpoint")
    print("2. Ensure scraped data is accessible")
    print("3. Verify data storage integration")
    print("=" * 60)

if __name__ == "__main__":
    main()