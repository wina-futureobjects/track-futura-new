#!/usr/bin/env python3
"""
Check Production UnifiedRunFolder Status

This will help us understand what folder IDs actually exist
vs what the frontend is trying to access.
"""

import requests
import json
from datetime import datetime

PRODUCTION_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def check_specific_folder_ids():
    """Check the specific folder IDs from the screenshots"""
    print("🔍 Checking specific folder IDs from screenshots...")
    
    # The URLs in screenshots were job/241 and job/238
    problem_ids = [241, 238, 240, 239]
    working_ids = [103, 104]  # We know these worked historically
    
    print("\n❌ Problem IDs (from screenshots):")
    for folder_id in problem_ids:
        try:
            # Try to access the job folder API endpoint that the frontend calls
            response = requests.get(f"{PRODUCTION_URL}/api/workflow/unified-run-folders/{folder_id}/")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Folder {folder_id}: {data.get('name', 'Unknown')} - {data.get('folder_type', 'Unknown')} type")
            elif response.status_code == 404:
                print(f"   ❌ Folder {folder_id}: NOT FOUND (404)")
            else:
                print(f"   ⚠️ Folder {folder_id}: Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ Folder {folder_id}: Error - {e}")
    
    print("\n✅ Known working IDs:")
    for folder_id in working_ids:
        try:
            response = requests.get(f"{PRODUCTION_URL}/api/workflow/unified-run-folders/{folder_id}/")
            if response.status_code == 200:
                data = response.json()
                posts_count = len(data.get('scraped_posts', []))
                print(f"   ✅ Folder {folder_id}: {data.get('name', 'Unknown')} - {posts_count} posts")
            else:
                print(f"   ⚠️ Folder {folder_id}: Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ Folder {folder_id}: Error - {e}")

def check_recent_folders():
    """Check what folders actually exist"""
    print("\n🔍 Checking what folders actually exist...")
    
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/workflow/unified-run-folders/?limit=10")
        if response.status_code == 200:
            data = response.json()
            print(f"Total folders: {data.get('count', 'Unknown')}")
            
            if 'results' in data and data['results']:
                print("\nRecent folders:")
                for folder in data['results'][:10]:
                    folder_id = folder.get('id')
                    name = folder.get('name', 'Unknown')
                    folder_type = folder.get('folder_type', 'Unknown')
                    posts_count = len(folder.get('scraped_posts', []))
                    print(f"   ID: {folder_id}, Name: {name}, Type: {folder_type}, Posts: {posts_count}")
            else:
                print("   No folders found")
        else:
            print(f"❌ Could not fetch folders: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching folders: {e}")

def identify_issue():
    """Try to identify what's causing the frontend to look for wrong IDs"""
    print("\n🔍 Analyzing the issue...")
    
    print("ISSUE ANALYSIS:")
    print("1. Frontend is trying to access /data-storage/job/241, /data-storage/job/238")
    print("2. These IDs (241, 238) are much higher than existing folders")
    print("3. This suggests either:")
    print("   a) Frontend is generating wrong URLs")
    print("   b) URL routing is broken")
    print("   c) Database IDs are out of sync")
    print("   d) Navigation system is passing wrong parameters")
    
    print("\n🔧 DEBUGGING STEPS:")
    print("1. Check if folders 241, 238 exist in database")
    print("2. Check how frontend generates these URLs")
    print("3. Check URL routing in React components")
    print("4. Verify navigation parameters")

def main():
    """Run all checks"""
    print("🚨 DATA STORAGE LOADING ISSUE - FOLDER ID ANALYSIS")
    print("=" * 65)
    print(f"Production URL: {PRODUCTION_URL}")
    print(f"Issue: Frontend accessing non-existent folder IDs")
    print(f"Analysis time: {datetime.now()}")
    print()
    
    try:
        check_specific_folder_ids()
        check_recent_folders()
        identify_issue()
        
        print("\n" + "=" * 65)
        print("🎯 CONCLUSION:")
        print("The frontend is trying to access folder IDs that don't exist.")
        print("Need to investigate why URLs contain these high ID numbers.")
        
    except Exception as e:
        print(f"\n❌ Analysis failed with error: {e}")

if __name__ == "__main__":
    main()