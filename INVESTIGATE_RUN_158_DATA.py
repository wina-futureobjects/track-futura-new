#!/usr/bin/env python3
"""
INVESTIGATE RUN 158 DATA LOCATIONS

Check where run 158 data actually exists and redirect the webhook-results
endpoint to the correct location.
"""

import requests
import json

def check_existing_data_endpoints():
    """Check all endpoints where run 158 data might exist"""
    print("🔍 Investigating where run 158 data actually exists...")
    
    base_url = "https://trackfutura.futureobjects.io"
    
    # Working endpoints from previous test
    working_endpoints = [
        "/api/brightdata/run/158/",
        "/api/brightdata/data-storage/run/158/"
    ]
    
    for endpoint in working_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n📋 Checking: {endpoint}")
            
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Data found!")
                
                # Check data structure
                if isinstance(data, dict):
                    if 'data' in data and isinstance(data['data'], list):
                        posts = data['data']
                        print(f"   📊 Posts: {len(posts)}")
                        
                        if posts:
                            sample = posts[0]
                            print(f"   🎯 Sample: {sample.get('user_posted', 'N/A')} - {sample.get('content', '')[:40]}...")
                            
                    elif 'posts' in data and isinstance(data['posts'], list):
                        posts = data['posts']
                        print(f"   📊 Posts: {len(posts)}")
                        
                        if posts:
                            sample = posts[0]
                            print(f"   🎯 Sample: {sample.get('user_posted', 'N/A')} - {sample.get('content', '')[:40]}...")
                    
                    else:
                        # Show available keys
                        keys = list(data.keys())[:5]
                        print(f"   🔑 Available keys: {keys}")
                        
                        # Show raw data sample
                        print(f"   📄 Raw data sample: {str(data)[:200]}...")
                        
                elif isinstance(data, list):
                    print(f"   📊 List with {len(data)} items")
                    if data:
                        sample = data[0]
                        print(f"   🎯 Sample item: {str(sample)[:100]}...")
                        
                else:
                    print(f"   📄 Raw response: {str(data)[:200]}...")
                    
            else:
                print(f"   ❌ Failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")


def test_webhook_results_redirect():
    """Test if we can redirect webhook-results to working endpoint"""
    print("\n🔄 Testing webhook-results redirect solution...")
    
    # The webhook-results endpoint should internally redirect to data-storage
    base_url = "https://trackfutura.futureobjects.io"
    
    # Test different variations of run 158 endpoints
    endpoints_to_test = [
        "/api/brightdata/webhook-results/run/158/",
        "/api/brightdata/webhook-results/run/158",
        "/api/brightdata/run-info/158/",
        "/api/brightdata/results/158/",
        "/api/brightdata/job-results/158/"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            status_emoji = "✅" if response.status_code == 200 else "❌" if response.status_code == 404 else "⚠️"
            print(f"   {status_emoji} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and ('data' in data or 'posts' in data):
                    posts_count = len(data.get('data', data.get('posts', [])))
                    print(f"      📊 Found {posts_count} posts!")
                    
        except Exception as e:
            print(f"   ❌ {endpoint}: ERROR")


def create_simple_redirect():
    """Create a simple fix by using the working data-storage endpoint data"""
    print("\n🔧 Attempting simple redirect fix...")
    
    # Get data from working endpoint
    working_url = "https://trackfutura.futureobjects.io/api/brightdata/data-storage/run/158/"
    
    try:
        response = requests.get(working_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved data from working endpoint")
            
            # Show what we got
            if isinstance(data, dict):
                keys = list(data.keys())
                print(f"   🔑 Data keys: {keys}")
                
                # If this has the posts we need, the solution is to fix the webhook-results endpoint
                # to internally call the data-storage endpoint
                
                return data
        else:
            print(f"❌ Working endpoint failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error retrieving data: {e}")
        return None


def main():
    """Investigate and fix run 158 data access"""
    print("🔍 RUN 158 DATA INVESTIGATION")
    print("=" * 50)
    
    # Step 1: Check existing data
    check_existing_data_endpoints()
    
    # Step 2: Test redirect options
    test_webhook_results_redirect()
    
    # Step 3: Attempt redirect fix
    data = create_simple_redirect()
    
    if data:
        print("\n💡 SOLUTION IDENTIFIED:")
        print("   ✅ Run 158 data EXISTS in data-storage endpoint")
        print("   ❌ webhook-results endpoint not finding it")
        print("   🔧 FIX: Update webhook-results to use data-storage data")
        print("\n🌐 Current working URL:")
        print("   https://trackfutura.futureobjects.io/api/brightdata/data-storage/run/158/")
        print("\n🎯 Needed URL:")
        print("   https://trackfutura.futureobjects.io/api/brightdata/webhook-results/run/158/")
    else:
        print("\n❌ No data found in working endpoints")
        print("   Need to create run 158 data from scratch")


if __name__ == "__main__":
    main()