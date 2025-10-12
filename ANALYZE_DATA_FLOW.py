#!/usr/bin/env python3
"""
Analyze Data Flow Linkage

Check the complete flow from workflow to data storage to understand
where the folder_id linking is breaking.
"""

import requests
import json
from datetime import datetime

PRODUCTION_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def analyze_folder_240_complete_flow():
    """Analyze the complete data flow for folder 240"""
    print("🔍 COMPLETE DATA FLOW ANALYSIS FOR FOLDER 240")
    print("=" * 60)
    
    folder_id = 240
    
    # Step 1: Check UnifiedRunFolder
    print(f"1️⃣ WORKFLOW MANAGEMENT → UnifiedRunFolder {folder_id}")
    response = requests.get(f"{PRODUCTION_URL}/api/track-accounts/report-folders/{folder_id}/")
    if response.status_code == 200:
        folder_data = response.json()
        print(f"   ✅ UnifiedRunFolder exists: {folder_data['name']}")
        print(f"   📊 Claimed post_count: {folder_data['post_count']}")
        print(f"   🏗️ Folder type: {folder_data['folder_type']}")
        print(f"   🔗 Scraping run: {folder_data.get('scraping_run')}")
    else:
        print(f"   ❌ UnifiedRunFolder not found: {response.status_code}")
        return
    
    # Step 2: Check BrightData Job Results (the endpoint that should work)
    print(f"\n2️⃣ DATA STORAGE ENDPOINT → /api/brightdata/job-results/{folder_id}/")
    response = requests.get(f"{PRODUCTION_URL}/api/brightdata/job-results/{folder_id}/")
    if response.status_code == 200:
        brightdata_result = response.json()
        print(f"   🎯 BrightData Success: {brightdata_result.get('success')}")
        print(f"   📊 Total Results: {brightdata_result.get('total_results', 0)}")
        print(f"   💾 Source: {brightdata_result.get('source', 'unknown')}")
        print(f"   📝 Message: {brightdata_result.get('message', 'No message')}")
        
        if brightdata_result.get('success') and brightdata_result.get('total_results', 0) > 0:
            print(f"   ✅ DATA FOUND! Flow is working correctly.")
            return True
        else:
            print(f"   ❌ NO DATA FOUND - This is the broken link!")
    else:
        print(f"   ❌ BrightData endpoint failed: {response.status_code}")
    
    # Step 3: Check if there are any BrightDataScrapedPost records for this folder
    print(f"\n3️⃣ DATABASE → Check for orphaned scraped posts")
    print(f"   (This would require direct database access)")
    print(f"   The issue is likely that BrightDataScrapedPost records:")
    print(f"   - Either don't exist for folder_id={folder_id}")
    print(f"   - Or exist but aren't linked to folder_id properly")
    
    # Step 4: Check scraper requests
    print(f"\n4️⃣ SCRAPER REQUESTS → Check BrightData scraper requests")
    print(f"   Need to check if scraper requests exist for folder_id={folder_id}")
    print(f"   And if they have correct snapshot_id values")
    
    return False

def identify_fix_needed():
    """Identify what needs to be fixed"""
    print(f"\n🔧 FIX NEEDED:")
    print(f"The issue is in the data linking chain:")
    print(f"")
    print(f"WORKFLOW → Creates scraper request with folder_id=240")
    print(f"WEBHOOK → Processes data but doesn't link to folder_id=240")  
    print(f"ENDPOINT → Queries for folder_id=240 but finds no data")
    print(f"")
    print(f"💡 SOLUTION:")
    print(f"1. Check if webhook processing is properly extracting folder_id")
    print(f"2. Ensure _create_brightdata_scraped_post gets correct folder_id")
    print(f"3. Verify scraper_request.folder_id is set when creating requests")
    print(f"4. Fix the linking between webhook data and folder_id")

def main():
    analyze_folder_240_complete_flow()
    identify_fix_needed()
    
    print(f"\n" + "=" * 60)
    print(f"🎯 CONCLUSION:")
    print(f"The data flow architecture is correct, but the folder_id linking")
    print(f"is broken somewhere between webhook processing and post creation.")
    print(f"")
    print(f"📋 NEXT STEPS:")
    print(f"1. Check webhook processing logs for folder_id extraction")
    print(f"2. Verify scraper request creation includes folder_id")
    print(f"3. Fix the _create_brightdata_scraped_post function")
    print(f"4. Test the complete flow with a new scraping job")

if __name__ == "__main__":
    main()