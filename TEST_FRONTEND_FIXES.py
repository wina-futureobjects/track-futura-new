#!/usr/bin/env python3
"""
Test if Frontend Fixes Are Working

Check if the frontend changes resolved the loading spinner issue
even without the database fix.
"""

import requests
import json
from datetime import datetime

PRODUCTION_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def test_frontend_fixes():
    """Test if the frontend is now handling empty folders correctly"""
    print("🧪 Testing Frontend Fixes...")
    
    # Test folder 240 which should now show better error handling
    print("\n📁 Testing Folder 240 (Facebook - Posts):")
    response = requests.get(f"{PRODUCTION_URL}/api/track-accounts/report-folders/240/")
    if response.status_code == 200:
        data = response.json()
        print(f"   Name: {data['name']}")
        print(f"   Type: {data['folder_type']}")
        print(f"   Post Count: {data['post_count']}")
        print(f"   Subfolders: {len(data.get('subfolders', []))}")
        
        # Check BrightData endpoint
        bd_response = requests.get(f"{PRODUCTION_URL}/api/brightdata/job-results/240/")
        if bd_response.status_code == 200:
            bd_data = bd_response.json()
            print(f"   BrightData Success: {bd_data.get('success')}")
            print(f"   BrightData Posts: {bd_data.get('total_results', 0)}")
    
    print(f"\n🌐 Frontend URL to test:")
    print(f"   https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/240")
    print(f"\n📋 Expected behavior with frontend fixes:")
    print(f"   1. Should try BrightData integration first (service folder)")
    print(f"   2. Should show better error message instead of 'Job in Progress'")
    print(f"   3. Should not show loading spinner indefinitely")

def check_deployment_status():
    """Check if the latest deployment is active"""
    print("\n🚀 Checking Deployment Status...")
    
    # Test if the health endpoint is responding
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/health/")
        if response.status_code == 200:
            print("✅ Production environment is healthy")
        else:
            print(f"⚠️ Health check returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

def main():
    """Test the fixes"""
    print("🧪 TESTING FRONTEND FIXES")
    print("=" * 40)
    print(f"Production URL: {PRODUCTION_URL}")
    print(f"Test time: {datetime.now()}")
    print()
    
    check_deployment_status()
    test_frontend_fixes()
    
    print("\n" + "=" * 40)
    print("🎯 NEXT STEPS:")
    print("1. Visit the folder URL above to test the frontend fixes")
    print("2. Check if loading spinner issue is resolved")
    print("3. Verify better error messages are shown")
    print("4. Apply database fix if needed for completely accurate counts")

if __name__ == "__main__":
    main()