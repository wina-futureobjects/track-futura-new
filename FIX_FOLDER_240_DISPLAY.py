#!/usr/bin/env python3
"""
Fix Folder 240 Data Display Issue

The issue is that folder 240 is a service folder with 1 post, but:
1. The subfolder (241) has 0 posts
2. The platform-specific API returns 0 posts
3. BrightData integration doesn't find the data

Let's identify where the 1 post actually is and fix the display.
"""

import requests
import json
from datetime import datetime

PRODUCTION_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def check_all_post_sources():
    """Check all possible sources for the missing post"""
    print("🔍 Checking All Possible Post Sources for Folder 240...")
    
    # 1. BrightData scraped posts
    print("\n1. BrightData Scraped Posts:")
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/brightdata/job-results/240/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ BrightData: {data.get('total_results', 0)} posts")
        else:
            print(f"   ❌ BrightData: {response.status_code}")
    except Exception as e:
        print(f"   ❌ BrightData: Error - {e}")
    
    # 2. Platform-specific API (Facebook)
    print("\n2. Platform-Specific API (Facebook):")
    endpoints = [
        f"/api/facebook-data/posts/?folder=240&project=1",
        f"/api/facebook-data/posts/?project=1",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{PRODUCTION_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'count' in data:
                    total = data['count']
                    results = data.get('results', [])
                    # Check if any posts are for folder 240
                    folder_240_posts = [p for p in results if p.get('folder') == 240]
                    print(f"   📡 {endpoint}: {total} total, {len(folder_240_posts)} for folder 240")
                else:
                    print(f"   📡 {endpoint}: {len(data)} items" if isinstance(data, list) else f"   📡 {endpoint}: {type(data)}")
            else:
                print(f"   📡 {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"   📡 {endpoint}: Error - {e}")
    
    # 3. Check scraping run 50 directly
    print("\n3. Scraping Run 50:")
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/workflow/scraping-runs/50/")
        if response.status_code == 200:
            data = response.json()
            scraped_posts = data.get('scraped_posts', [])
            print(f"   📊 Scraping Run 50: {len(scraped_posts)} posts")
            for post in scraped_posts[:3]:  # Show first 3
                print(f"      - Post {post.get('id')}: Folder {post.get('folder')}")
        else:
            print(f"   ❌ Scraping Run 50: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Scraping Run 50: Error - {e}")

def suggest_fixes():
    """Suggest possible fixes for the data display issue"""
    print("\n🔧 SUGGESTED FIXES:")
    
    print("\n1. FRONTEND FIX - Update JobFolderView.tsx:")
    print("   - Handle service folders differently from job folders")
    print("   - For service folders, check if BrightData integration has data")
    print("   - Fall back to aggregating data from subfolders")
    
    print("\n2. BACKEND FIX - Update post_count calculation:")
    print("   - Service folder post_count should reflect actual accessible posts")
    print("   - Update UnifiedRunFolder.post_count to match reality")
    
    print("\n3. DATA LINKING FIX:")
    print("   - Link existing posts to correct folders")
    print("   - Update BrightData integration to find orphaned posts")
    
    print("\n4. IMMEDIATE WORKAROUND:")
    print("   - Show better error message when no posts found")
    print("   - Hide 'Job in Progress' for completed but empty jobs")

def create_frontend_fix():
    """Suggest specific frontend code changes"""
    print("\n💻 FRONTEND CODE FIX:")
    print("""
    In JobFolderView.tsx, around line 260, add this logic:
    
    // Before trying to fetch from platform folders, check BrightData
    if (jobFolderData.folder_type === 'service' && jobFolderData.post_count > 0) {
      // For service folders, try BrightData integration first
      try {
        const brightDataResponse = await apiFetch(`/api/brightdata/job-results/${folderId}/`);
        if (brightDataResponse.ok) {
          const brightDataResult = await brightDataResponse.json();
          if (brightDataResult.success && brightDataResult.total_results > 0) {
            // Use BrightData posts
            const brightDataPosts = brightDataResult.data.posts || [];
            setPosts(brightDataPosts);
            setLoading(false);
            return;
          }
        }
      } catch (err) {
        console.log('BrightData integration not available, trying subfolders...');
      }
    }
    
    // If no BrightData posts and no subfolders have posts, show appropriate message
    if (allPosts.length === 0 && jobFolderData.post_count > 0) {
      setJobStatus({
        status: 'warning',
        message: 'Data exists but is not accessible through current endpoints. Please check data integration.'
      });
    }
    """)

def main():
    """Run the complete investigation and provide fixes"""
    print("🚨 FIXING FOLDER 240 DATA DISPLAY ISSUE")
    print("=" * 60)
    print(f"Production URL: {PRODUCTION_URL}")
    print(f"Problem: Folder 240 shows 1 post but frontend can't access it")
    print(f"Analysis time: {datetime.now()}")
    print()
    
    check_all_post_sources()
    suggest_fixes()
    create_frontend_fix()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("The issue is a mismatch between the data architecture and frontend expectations.")
    print("Folder 240 is a service folder that claims to have 1 post, but:")
    print("- BrightData integration doesn't find it")
    print("- Platform-specific APIs don't return it")
    print("- Subfolders are empty")
    print("\nThe post_count is incorrect or the data is orphaned.")
    print("Need to either fix the data linking or update the frontend logic.")

if __name__ == "__main__":
    main()