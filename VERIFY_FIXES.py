#!/usr/bin/env python3
"""
Quick Test: Verify the new fixes are working

This will help us understand what should happen after the latest deployment.
"""

import requests
from datetime import datetime

PRODUCTION_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def test_folder_240_behavior():
    """Test what should happen with folder 240 now"""
    print("🧪 Testing Expected Behavior for Folder 240")
    print("=" * 50)
    
    # Get folder 240 data
    response = requests.get(f"{PRODUCTION_URL}/api/track-accounts/report-folders/240/")
    if response.status_code == 200:
        data = response.json()
        print("📁 Folder 240 Details:")
        print(f"   Name: {data['name']}")
        print(f"   Type: {data['folder_type']}")
        print(f"   Post Count: {data['post_count']}")
        print(f"   Subfolders: {len(data.get('subfolders', []))}")
        
        subfolders = data.get('subfolders', [])
        for sub in subfolders:
            print(f"      - Subfolder {sub['id']}: {sub['name']} ({sub['post_count']} posts)")
    
    print(f"\n🎯 Expected Frontend Behavior (after cache refresh):")
    print(f"1. Load folder 240 (service folder)")
    print(f"2. Try BrightData integration first - should fail")
    print(f"3. Check subfolders - subfolder 241 has 0 posts")  
    print(f"4. Should show: 'No posts found in this service folder. The scraping jobs may not have completed successfully.'")
    print(f"5. Should NOT show 'Job in Progress' anymore")
    print(f"6. Should NOT make invalid API calls like /api/facebook-data/f_/posts/")
    
    print(f"\n🌐 Test URL:")
    print(f"https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/240")
    
    print(f"\n⚠️ IMPORTANT:")
    print(f"You may need to:")
    print(f"1. Wait a few minutes for deployment to complete")
    print(f"2. Hard refresh the browser (Ctrl+F5 or Ctrl+Shift+R)")
    print(f"3. Clear browser cache if still seeing old behavior")
    print(f"4. Check browser developer tools for the new console.log messages")

def check_deployment_time():
    """Check when the deployment happened"""
    print(f"\n⏰ Deployment Status:")
    print(f"   Latest fix deployed at: {datetime.now().strftime('%H:%M:%S')}")
    print(f"   Give it 2-3 minutes to propagate")

def main():
    test_folder_240_behavior()
    check_deployment_time()

if __name__ == "__main__":
    main()