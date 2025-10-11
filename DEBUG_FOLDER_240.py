#!/usr/bin/env python3
"""
Debug Folder 240 Data Issue

Let's investigate exactly where the post data is stored for folder 240
and why the frontend can't access it.
"""

import requests
import json
from datetime import datetime

PRODUCTION_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def investigate_folder_240():
    """Deep dive into folder 240's data structure"""
    print("🔍 Investigating Folder 240 Data Structure...")
    
    # Get folder details
    response = requests.get(f"{PRODUCTION_URL}/api/track-accounts/report-folders/240/")
    if response.status_code == 200:
        folder_data = response.json()
        print("📁 Folder 240 Details:")
        print(f"   Name: {folder_data['name']}")
        print(f"   Type: {folder_data['folder_type']}")  # Should be 'service'
        print(f"   Platform: {folder_data['platform']}")
        print(f"   Post Count: {folder_data['post_count']}")
        print(f"   Parent: {folder_data.get('parent_folder')}")
        print(f"   Subfolders: {len(folder_data.get('subfolders', []))}")
        
        # The frontend probably calls platform-specific endpoints
        # Let's check what it's trying to access
        print(f"\n🔍 Frontend Behavior Analysis:")
        print(f"   1. Folder 240 is type '{folder_data['folder_type']}'")
        print(f"   2. Platform: '{folder_data['platform']}'")
        
        if folder_data['folder_type'] == 'service':
            print(f"   3. Service folders should delegate to job subfolders")
            print(f"   4. But job subfolder 241 has 0 posts")
            print(f"   5. So where is the 1 post stored?")
        
        # Check subfolders
        for subfolder in folder_data.get('subfolders', []):
            print(f"\n   📂 Subfolder {subfolder['id']}: {subfolder['name']}")
            print(f"      Type: {subfolder['folder_type']}")
            print(f"      Posts: {subfolder['post_count']}")
    
    # Check if there are platform-specific posts
    print(f"\n🔍 Checking Platform-Specific Endpoints...")
    
    # Try different platform endpoints that frontend might call
    endpoints_to_try = [
        f"/api/facebook-data/folders/240/posts/?project=1",
        f"/api/facebook-data/folders/240/",
        f"/api/facebook-data/posts/?folder=240&project=1",
    ]
    
    for endpoint in endpoints_to_try:
        try:
            response = requests.get(f"{PRODUCTION_URL}{endpoint}")
            print(f"   📡 {endpoint}: Status {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'results' in data:
                    print(f"      → Found {len(data['results'])} posts")
                elif isinstance(data, dict) and 'count' in data:
                    print(f"      → Count: {data['count']}")
                elif isinstance(data, list):
                    print(f"      → Found {len(data)} items")
                else:
                    print(f"      → Data type: {type(data)}")
        except Exception as e:
            print(f"   📡 {endpoint}: Error - {e}")

def check_console_error():
    """Analyze the console error from the screenshot"""
    print(f"\n🚨 Console Error Analysis:")
    print(f"   Error: Failed to load resource: /api/facebook-data/f_/posts/?project=1")
    print(f"   Issue: The 'f_' suggests folder ID is undefined or null")
    print(f"   Root Cause: Frontend can't determine correct platform folder ID")
    print(f"   Expected: Should be /api/facebook-data/folders/[ID]/posts/?project=1")

def identify_data_location():
    """Try to find where the actual post data is stored"""
    print(f"\n🔍 Searching for the Missing Post Data...")
    
    # The folder claims to have 1 post, but BrightData says no data
    # This suggests the post is stored in a different system (legacy Facebook data?)
    
    print("   Possible locations:")
    print("   1. Legacy facebook_data_post table")
    print("   2. workflow_management_scrapingrun results")
    print("   3. Platform-specific tables")
    print("   4. Orphaned brightdata_integration_brightdatascrapedpost")
    
    # Check if this is a scraping run issue
    print(f"\n   🔍 Scraping Run 50 Analysis:")
    print(f"   - Folder 240 (service) has 1 post")
    print(f"   - Folder 241 (job) has 0 posts")
    print(f"   - Both linked to scraping_run: 50")
    print(f"   - Suggests data exists but linking is broken")

def main():
    """Run comprehensive folder 240 investigation"""
    print("🚨 FOLDER 240 DATA INVESTIGATION")
    print("=" * 60)
    print(f"Production URL: {PRODUCTION_URL}")
    print(f"Issue: Folder shows 1 post but frontend can't access it")
    print(f"Investigation time: {datetime.now()}")
    print()
    
    investigate_folder_240()
    check_console_error()
    identify_data_location()
    
    print("\n" + "=" * 60)
    print("🎯 FINDINGS:")
    print("1. Folder 240 is a SERVICE folder with 1 post")
    print("2. Subfolder 241 is a JOB folder with 0 posts")
    print("3. Frontend tries to access platform-specific endpoint")
    print("4. Endpoint construction fails (f_ instead of folder ID)")
    print("5. BrightData integration says no data found")
    print("6. Data exists somewhere but linking is broken")
    
    print("\n🔧 NEXT STEPS:")
    print("1. Fix frontend endpoint construction")
    print("2. Check data linking between systems")
    print("3. Verify scraping run 50 results")
    print("4. Update BrightData integration to find existing data")

if __name__ == "__main__":
    main()