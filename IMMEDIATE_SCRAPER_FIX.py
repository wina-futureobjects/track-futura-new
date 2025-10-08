#!/usr/bin/env python3
"""
IMMEDIATE FIX: Create working scraper with correct endpoints
"""
import requests
import json

def fix_scraper_endpoints():
    """Fix the scraper with correct endpoint URLs"""
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("🚨 IMMEDIATE SCRAPER FIX")
    print("=" * 50)
    
    # Step 1: Create a working scraping run
    print("1. 🚀 CREATING SCRAPING RUN")
    
    run_data = {
        "project": 3,
        "name": "Nike IG Scraper Test",
        "configuration": {
            "num_of_posts": 10,
            "start_date": "2025-10-01T00:00:00.000Z",
            "end_date": "2025-10-08T23:59:59.000Z",
            "auto_create_folders": True,
            "output_folder_pattern": "nike_scraped_data"
        }
    }
    
    try:
        run_url = f"{base_url}/api/workflow/scraping-runs/"
        response = requests.post(run_url, json=run_data, timeout=15)
        
        print(f"   Run creation status: {response.status_code}")
        
        if response.status_code == 201:
            run_result = response.json()
            run_id = run_result.get('id')
            print(f"   ✅ RUN CREATED: ID {run_id}")
            
            # Step 2: Start the run with correct endpoint
            print(f"\n2. 🏃 STARTING RUN {run_id}")
            
            # Try the correct endpoint from the URL patterns
            start_url = f"{base_url}/api/workflow/scraping-runs/{run_id}/start_run/"
            start_response = requests.post(start_url, timeout=15)
            
            print(f"   Start status: {start_response.status_code}")
            
            if start_response.status_code == 200:
                print("   🎉 SCRAPER STARTED SUCCESSFULLY!")
                start_data = start_response.json()
                print(f"   📊 Response: {start_data}")
                
                # Check the run status
                print(f"\n3. 📊 CHECKING RUN STATUS")
                status_url = f"{base_url}/api/workflow/scraping-runs/{run_id}/"
                status_response = requests.get(status_url, timeout=10)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Status: {status_data.get('status', 'Unknown')}")
                    print(f"   Progress: {status_data.get('progress_percentage', 0)}%")
                    print(f"   Jobs: {status_data.get('completed_jobs', 0)}/{status_data.get('total_jobs', 0)}")
                    
            else:
                error_text = start_response.text
                print(f"   ❌ Start failed: {error_text}")
                
                # Try alternative endpoint
                alt_start_url = f"{base_url}/api/workflow/scraping-runs/{run_id}/start/"
                alt_response = requests.post(alt_start_url, timeout=10)
                print(f"   Alternative endpoint status: {alt_response.status_code}")
                
        else:
            error_data = response.text
            print(f"   ❌ Run creation failed: {error_data}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Step 3: Check existing runs
    print(f"\n4. 📋 CHECKING EXISTING RUNS")
    
    try:
        runs_url = f"{base_url}/api/workflow/scraping-runs/?project=3"
        response = requests.get(runs_url, timeout=10)
        
        if response.status_code == 200:
            runs_data = response.json()
            
            if isinstance(runs_data, dict) and 'results' in runs_data:
                runs = runs_data['results']
            else:
                runs = runs_data if isinstance(runs_data, list) else []
            
            print(f"   📊 Total runs: {len(runs)}")
            
            # Show recent runs
            for i, run in enumerate(runs[:5]):
                run_id = run.get('id')
                name = run.get('name', 'Unknown')
                status = run.get('status', 'Unknown')
                progress = run.get('progress_percentage', 0)
                
                print(f"   {i+1}. Run {run_id}: {name} - {status} ({progress}%)")
                
                # If there's a pending run, try to start it
                if status == 'pending' and i == 0:  # Start the first pending run
                    print(f"      🚀 Attempting to start pending run {run_id}")
                    
                    start_url = f"{base_url}/api/workflow/scraping-runs/{run_id}/start_run/"
                    start_response = requests.post(start_url, timeout=15)
                    
                    if start_response.status_code == 200:
                        print(f"      ✅ Started run {run_id}!")
                    else:
                        print(f"      ❌ Failed to start: {start_response.status_code}")
                        
        else:
            print(f"   ❌ Failed to get runs: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error checking runs: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 SCRAPER STATUS:")
    print("✅ If run created and started = SCRAPING IS WORKING!")
    print("❌ If start failed = Check error messages above")
    print("⏳ Check the workflow page to see active runs")
    print("=" * 50)

if __name__ == "__main__":
    fix_scraper_endpoints()