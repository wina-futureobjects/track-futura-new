#!/usr/bin/env python3
"""
Diagnose Data Storage Issue

The frontend is showing loading spinners but no data. Let's check:
1. What scraping runs exist
2. What BrightData scraped posts exist
3. The connection between them
"""

import requests
import json
from datetime import datetime

PRODUCTION_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def check_scraping_runs():
    """Check what scraping runs exist"""
    print("🔍 Checking scraping runs...")
    
    response = requests.get(f"{PRODUCTION_URL}/api/workflow/scraping-runs/?limit=20")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} total scraping runs")
        
        if 'results' in data and data['results']:
            print("\nRecent runs:")
            for run in data['results'][:10]:
                run_id = run.get('id')
                status = run.get('status')
                created = run.get('created_at')
                folder_id = run.get('folder_id')
                print(f"   - ID: {run_id}, Status: {status}, Folder: {folder_id}, Created: {created}")
                
                # Check if this run has data
                try:
                    detail_response = requests.get(f"{PRODUCTION_URL}/api/workflow/scraping-runs/{run_id}/")
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        posts = detail_data.get('scraped_posts', [])
                        print(f"      → {len(posts)} scraped posts found")
                    else:
                        print(f"      → Could not get details (status: {detail_response.status_code})")
                except Exception as e:
                    print(f"      → Error getting details: {e}")
        else:
            print("   No results found")
    else:
        print(f"❌ Scraping runs failed: {response.status_code}")

def check_brightdata_posts():
    """Check BrightData scraped posts directly"""
    print("\n🔍 Checking BrightData scraped posts...")
    
    # This endpoint might require auth, but let's try
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/brightdata/batch-jobs/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ BrightData batch jobs accessible")
            print(f"   Response: {data}")
        else:
            print(f"❌ BrightData batch jobs failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking BrightData posts: {e}")

def check_specific_jobs():
    """Check the specific jobs from the screenshots"""
    print("\n🔍 Checking specific jobs from screenshots...")
    
    job_ids = [241, 238, 240, 239]  # Based on URLs in screenshots
    
    for job_id in job_ids:
        print(f"\nChecking Job {job_id}:")
        
        # Try scraping-runs endpoint
        try:
            response = requests.get(f"{PRODUCTION_URL}/api/workflow/scraping-runs/{job_id}/")
            if response.status_code == 200:
                data = response.json()
                posts = data.get('scraped_posts', [])
                status = data.get('status')
                print(f"   ✅ Job {job_id} exists - Status: {status}, Posts: {len(posts)}")
            else:
                print(f"   ❌ Job {job_id} not found in scraping-runs (status: {response.status_code})")
        except Exception as e:
            print(f"   ❌ Error checking Job {job_id}: {e}")

def main():
    """Run all diagnostics"""
    print("🚨 DATA STORAGE LOADING ISSUE DIAGNOSIS")
    print("=" * 60)
    print(f"Production URL: {PRODUCTION_URL}")
    print(f"Issue: Frontend showing loading spinners for Jobs 241, 238")
    print(f"Diagnosis time: {datetime.now()}")
    print()
    
    try:
        check_scraping_runs()
        check_brightdata_posts()
        check_specific_jobs()
        
        print("\n" + "=" * 60)
        print("🎯 LIKELY ISSUES:")
        print("1. Frontend trying to access non-existent job IDs")
        print("2. Data not properly linked to scraping runs")
        print("3. API endpoint mismatch between frontend and backend")
        print("4. Authentication issues preventing data access")
        print()
        print("📋 NEXT STEPS:")
        print("1. Check frontend code for correct API endpoints")
        print("2. Verify data is properly stored in database")
        print("3. Test API endpoints with proper authentication")
        print("4. Check URL routing in Django")
        
    except Exception as e:
        print(f"\n❌ Diagnosis failed with error: {e}")

if __name__ == "__main__":
    main()