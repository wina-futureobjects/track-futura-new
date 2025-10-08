#!/usr/bin/env python3
"""
DIRECT FIX: Check exactly what's happening on workflow page
"""
import requests
import json

def check_exact_workflow_issue():
    """Check the exact issue preventing scraping"""
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("🚨 DIRECT WORKFLOW PAGE DIAGNOSIS")
    print("=" * 60)
    
    # Check 1: What exactly shows on workflow page
    print("1. 🔍 CHECKING WORKFLOW PAGE DATA")
    
    # Check the TrackSourceCollections endpoint specifically
    try:
        # This is what the frontend calls
        track_sources_url = f"{base_url}/api/workflow/input-collections/?project=3"
        response = requests.get(track_sources_url, timeout=10)
        
        print(f"   Track sources API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                track_sources = data['results']
                count = data.get('count', 0)
            else:
                track_sources = data if isinstance(data, list) else []
                count = len(track_sources)
            
            print(f"   📊 Track sources returned: {count}")
            
            if count > 0:
                print("   ✅ TRACK SOURCES FOUND!")
                for i, source in enumerate(track_sources):
                    name = source.get('name', 'Unknown')
                    platform = source.get('platform_name', 'Unknown')
                    urls = source.get('urls', [])
                    print(f"      {i+1}. {name} ({platform}) - {len(urls)} URLs")
            else:
                print("   ❌ NO TRACK SOURCES - This is the problem!")
                
        else:
            print(f"   ❌ API Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Check 2: What's in the track_accounts table
    print("\n2. 🔍 CHECKING TRACK ACCOUNTS TABLE")
    
    try:
        # Check the source tracking API
        source_api_url = f"{base_url}/api/track-accounts/source-folders/?project=3"
        response = requests.get(source_api_url, timeout=10)
        
        print(f"   Source folders API status: {response.status_code}")
        
        if response.status_code == 200:
            folders_data = response.json()
            
            if isinstance(folders_data, dict) and 'results' in folders_data:
                folders = folders_data['results']
            else:
                folders = folders_data if isinstance(folders_data, list) else []
            
            print(f"   📁 Source folders: {len(folders)}")
            
            if len(folders) > 0:
                print("   ✅ SOURCE FOLDERS EXIST!")
                for folder in folders:
                    name = folder.get('name', 'Unknown')
                    accounts_count = folder.get('accounts_count', 0)
                    print(f"      📁 {name}: {accounts_count} accounts")
            else:
                print("   ❌ No source folders found")
                
        else:
            print(f"   ❌ Source folders API error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Check 3: Try to manually trigger the connection
    print("\n3. 🔧 MANUAL CONNECTION ATTEMPT")
    
    try:
        # Check if there's a sync endpoint
        sync_url = f"{base_url}/api/workflow/sync-track-sources/"
        response = requests.post(sync_url, json={"project": 3}, timeout=10)
        
        print(f"   Sync attempt status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Sync successful!")
        elif response.status_code == 404:
            print("   ⚠️  Sync endpoint doesn't exist (normal)")
        else:
            print(f"   Result: {response.text}")
            
    except Exception as e:
        print(f"   Sync error: {str(e)}")
    
    # Check 4: Test instant run creation
    print("\n4. 🚀 TEST INSTANT RUN CREATION")
    
    try:
        run_data = {
            "project": 3,
            "configuration": {
                "num_of_posts": 5,
                "start_date": "2025-10-07T00:00:00.000Z",
                "end_date": "2025-10-08T23:59:59.000Z",
                "auto_create_folders": True,
                "output_folder_pattern": "scraped_data_test"
            }
        }
        
        run_url = f"{base_url}/api/workflow/scraping-runs/"
        response = requests.post(run_url, json=run_data, timeout=15)
        
        print(f"   Instant run status: {response.status_code}")
        
        if response.status_code == 201:
            run_result = response.json()
            run_id = run_result.get('id')
            print(f"   ✅ INSTANT RUN CREATED: ID {run_id}")
            
            # Try to start it
            start_url = f"{base_url}/api/workflow/scraping-runs/{run_id}/start/"
            start_response = requests.post(start_url, timeout=10)
            print(f"   Start run status: {start_response.status_code}")
            
            if start_response.status_code == 200:
                print("   🚀 RUN STARTED SUCCESSFULLY!")
                print("   ✅ SCRAPING IS WORKING!")
            else:
                print(f"   ❌ Start failed: {start_response.text}")
                
        else:
            error_data = response.text
            print(f"   ❌ Run creation failed: {error_data}")
            
    except Exception as e:
        print(f"   ❌ Run test error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSIS RESULTS:")
    print("If track sources = 0 but source folders > 0:")
    print("  → Track sources need to be converted to InputCollections")
    print("If instant run works:")
    print("  → Scraping system is functional, just needs track sources")
    print("If instant run fails:")
    print("  → There's a deeper configuration issue")
    print("=" * 60)

if __name__ == "__main__":
    check_exact_workflow_issue()