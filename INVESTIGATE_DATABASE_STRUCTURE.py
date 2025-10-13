#!/usr/bin/env python3
"""
🔍 INVESTIGATE DATABASE STRUCTURE FOR RUN 158
Find out what models and fields are actually available
"""

import requests
import json

BASE_URL = "https://trackfutura.futureobjects.io"

def check_all_endpoints():
    """Check all possible endpoints to find data structure"""
    print("🔍 INVESTIGATING ALL ENDPOINTS")
    print("=" * 50)
    
    endpoints = [
        "/api/brightdata/",
        "/api/brightdata/runs/",
        "/api/brightdata/folders/",
        "/api/brightdata/webhook/",
        "/api/brightdata/scraped-posts/",
        "/api/brightdata/data/",
        "/api/brightdata/results/",
        "/api/instagram_data/",
        "/api/instagram-data/",
        "/api/posts/",
        "/api/data/",
        "/api/scraping/",
        "/api/workflow/",
        "/api/runs/",
        "/api/folders/",
    ]
    
    working_endpoints = []
    
    for endpoint in endpoints:
        try:
            url = BASE_URL + endpoint
            response = requests.get(url, timeout=10)
            
            print(f"📍 {endpoint}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if isinstance(data, list) and len(data) > 0:
                        print(f"   ✅ {len(data)} items")
                        sample = data[0]
                        print(f"   🔑 Keys: {list(sample.keys())[:5]}...")
                        working_endpoints.append((endpoint, data))
                        
                    elif isinstance(data, dict):
                        if 'results' in data and len(data['results']) > 0:
                            print(f"   ✅ {len(data['results'])} results")
                            sample = data['results'][0]
                            print(f"   🔑 Keys: {list(sample.keys())[:5]}...")
                            working_endpoints.append((endpoint, data))
                        elif len(data) > 0:
                            print(f"   ✅ Dict with keys: {list(data.keys())[:5]}...")
                            working_endpoints.append((endpoint, data))
                        else:
                            print(f"   📄 Empty dict")
                    else:
                        print(f"   📄 Empty")
                        
                except json.JSONDecodeError:
                    print(f"   ✅ Non-JSON response")
                    
            elif response.status_code == 404:
                print(f"   ❌ Not found")
            else:
                print(f"   ⚠️ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Error: {str(e)[:30]}...")
    
    return working_endpoints

def check_run_specific():
    """Check for existing run data"""
    print(f"\n🔍 CHECKING EXISTING RUN DATA")
    print("=" * 50)
    
    run_endpoints = [
        "/api/brightdata/runs/",
        "/api/runs/",
        "/api/workflow/runs/",
        "/api/data/runs/",
    ]
    
    for endpoint in run_endpoints:
        try:
            url = BASE_URL + endpoint
            response = requests.get(url, timeout=10)
            
            print(f"📍 {endpoint}")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    runs = [item for item in data if 'run' in str(item) or '158' in str(item)]
                    print(f"   🎯 Found {len(runs)} potential runs")
                    
                elif isinstance(data, dict) and 'results' in data:
                    runs = [item for item in data['results'] if 'run' in str(item) or '158' in str(item)]
                    print(f"   🎯 Found {len(runs)} potential runs")
                    
                    if len(data.get('results', [])) > 0:
                        sample = data['results'][0]
                        print(f"   🔑 Sample run structure: {list(sample.keys())}")
                        
                        # Look for run 158 specifically
                        for item in data['results']:
                            if str(item.get('id')) == '158' or str(item.get('run_id')) == '158':
                                print(f"   🎯 FOUND RUN 158: {item}")
                                
        except Exception as e:
            print(f"   💥 Error: {e}")

def check_folders():
    """Check folder structure"""
    print(f"\n🔍 CHECKING FOLDER STRUCTURE")
    print("=" * 50)
    
    folder_endpoints = [
        "/api/brightdata/folders/",
        "/api/folders/",
        "/api/data/folders/",
    ]
    
    for endpoint in folder_endpoints:
        try:
            url = BASE_URL + endpoint
            response = requests.get(url, timeout=10)
            
            print(f"📍 {endpoint}")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    print(f"   ✅ {len(data)} folders")
                    sample = data[0]
                    print(f"   🔑 Folder structure: {list(sample.keys())}")
                    
                    # Look for folder 158
                    for folder in data:
                        if str(folder.get('id')) == '158' or '158' in str(folder):
                            print(f"   🎯 FOUND FOLDER 158: {folder}")
                            
                elif isinstance(data, dict) and 'results' in data:
                    print(f"   ✅ {len(data['results'])} folders")
                    if len(data['results']) > 0:
                        sample = data['results'][0]
                        print(f"   🔑 Folder structure: {list(sample.keys())}")
                        
        except Exception as e:
            print(f"   💥 Error: {e}")

def main():
    """Comprehensive investigation"""
    print("🔍 COMPREHENSIVE INVESTIGATION FOR RUN 158")
    print("=" * 60)
    
    working = check_all_endpoints()
    check_run_specific()
    check_folders()
    
    print(f"\n📊 SUMMARY")
    print("=" * 30)
    print(f"Found {len(working)} working endpoints")
    
    for endpoint, data in working:
        print(f"✅ {endpoint}")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. Use working endpoints to create data")
    print(f"2. Match exact data structure required")
    print(f"3. Create run 158 folder if it doesn't exist")
    print(f"4. Create posts with correct format")

if __name__ == "__main__":
    main()