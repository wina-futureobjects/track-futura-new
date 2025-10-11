#!/usr/bin/env python3
"""
Fix Incorrect Post Counts

Update UnifiedRunFolder post_count to reflect actual accessible posts.
This will fix the "Job in Progress" issue for folders with incorrect counts.
"""

import requests
import json
from datetime import datetime

PRODUCTION_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def identify_folders_with_wrong_counts():
    """Find folders with incorrect post_count values"""
    print("🔍 Identifying folders with incorrect post counts...")
    
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/track-accounts/report-folders/?limit=50")
        if response.status_code != 200:
            print(f"❌ Failed to fetch folders: {response.status_code}")
            return []
        
        data = response.json()
        folders = data.get('results', [])
        
        folders_to_fix = []
        
        for folder in folders:
            folder_id = folder.get('id')
            claimed_count = folder.get('post_count', 0)
            folder_type = folder.get('folder_type')
            platform = folder.get('platform')
            
            if claimed_count > 0:
                # Check actual post count via API
                actual_count = 0
                
                # Try BrightData first
                try:
                    bd_response = requests.get(f"{PRODUCTION_URL}/api/brightdata/job-results/{folder_id}/")
                    if bd_response.status_code == 200:
                        bd_data = bd_response.json()
                        if bd_data.get('success'):
                            actual_count = bd_data.get('total_results', 0)
                except:
                    pass
                
                # If no BrightData posts, try platform API
                if actual_count == 0 and platform:
                    try:
                        platform_response = requests.get(f"{PRODUCTION_URL}/api/{platform}-data/posts/?folder={folder_id}&project=1")
                        if platform_response.status_code == 200:
                            platform_data = platform_response.json()
                            actual_count = platform_data.get('count', 0)
                    except:
                        pass
                
                # Check if counts don't match
                if claimed_count != actual_count:
                    folders_to_fix.append({
                        'id': folder_id,
                        'name': folder.get('name'),
                        'type': folder_type,
                        'platform': platform,
                        'claimed_count': claimed_count,
                        'actual_count': actual_count
                    })
        
        print(f"\n📊 Found {len(folders_to_fix)} folders with incorrect post counts:")
        for folder in folders_to_fix:
            print(f"   📁 ID {folder['id']}: {folder['name']}")
            print(f"      Claimed: {folder['claimed_count']}, Actual: {folder['actual_count']}")
            print(f"      Type: {folder['type']}, Platform: {folder['platform']}")
            print()
        
        return folders_to_fix
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def generate_database_fix_script(folders_to_fix):
    """Generate SQL script to fix the post counts"""
    if not folders_to_fix:
        print("✅ No folders need fixing!")
        return
    
    print("💾 Generating database fix script...")
    
    sql_commands = []
    sql_commands.append("-- Fix incorrect post_count values in UnifiedRunFolder")
    sql_commands.append("-- Generated on " + datetime.now().isoformat())
    sql_commands.append("")
    
    for folder in folders_to_fix:
        folder_id = folder['id']
        actual_count = folder['actual_count']
        sql_commands.append(f"-- Fix folder {folder_id}: {folder['name']}")
        sql_commands.append(f"UPDATE workflow_management_unifiedrunfolder SET post_count = {actual_count} WHERE id = {folder_id};")
        sql_commands.append("")
    
    sql_script = "\n".join(sql_commands)
    
    # Save to file
    with open("fix_post_counts.sql", "w") as f:
        f.write(sql_script)
    
    print(f"📝 SQL script saved to fix_post_counts.sql")
    print(f"\nTo apply the fixes, run:")
    print(f"upsun ssh -p inhoolfrqniuu -e upsun-deployment -A trackfutura 'psql < fix_post_counts.sql'")

def main():
    """Identify and fix incorrect post counts"""
    print("🚨 FIXING INCORRECT POST COUNTS")
    print("=" * 50)
    print(f"Production URL: {PRODUCTION_URL}")
    print(f"Goal: Fix folders showing wrong post counts")
    print(f"Analysis time: {datetime.now()}")
    print()
    
    folders_to_fix = identify_folders_with_wrong_counts()
    
    if folders_to_fix:
        generate_database_fix_script(folders_to_fix)
        
        print("\n🔧 IMMEDIATE IMPACT:")
        print("- Folders with post_count=0 will stop showing 'Job in Progress'")
        print("- Frontend will show appropriate 'No posts found' message")
        print("- Loading spinners will stop appearing for empty folders")
        
        print("\n📋 NEXT STEPS:")
        print("1. Apply the generated SQL script to fix database")
        print("2. Deploy frontend changes")
        print("3. Test the affected folder URLs")
    else:
        print("✅ All folder post counts are correct!")
    
    print("\n🎯 FOLDERS TO TEST AFTER FIX:")
    print("- https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/240")
    print("- https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/241")
    print("- https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/238")

if __name__ == "__main__":
    main()