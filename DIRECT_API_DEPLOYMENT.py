#!/usr/bin/env python3
"""
🚀 DIRECT PRODUCTION API DEPLOYMENT
==================================
This will deploy data directly to your production API
"""

import requests
import json
import time

# Your production API details
PRODUCTION_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
API_TOKEN = "your_api_token_here"  # You'll need to provide this

# Test data to create on production
SAMPLE_POSTS = []

# Create Instagram posts for Job 2 (folder 103)
for i in range(1, 21):
    SAMPLE_POSTS.append({
        "post_id": f"insta_post_{i}_{int(time.time())}",
        "url": f"https://instagram.com/p/production_post_{i}/",
        "content": f"Production Instagram post {i} - Nike Air Max collection. Just Do It! #nike #justdoit #airmax",
        "platform": "instagram", 
        "user_posted": f"nike_official_{i}",
        "likes": 500 + i * 25,
        "num_comments": 15 + i * 2,
        "shares": 5 + i,
        "folder_id": 103,
        "media_type": "photo",
        "is_verified": i % 3 == 0,
        "hashtags": ["nike", "justdoit", "airmax"],
        "mentions": ["@nike", "@nikesportswear"]
    })

# Create Facebook posts for Job 3 (folder 104)  
for i in range(1, 21):
    SAMPLE_POSTS.append({
        "post_id": f"fb_post_{i}_{int(time.time())}",
        "url": f"https://facebook.com/nike/posts/production_{i}",
        "content": f"Production Facebook post {i} - New Nike collection available now! Experience the innovation.",
        "platform": "facebook",
        "user_posted": f"nike_page_{i}",
        "likes": 750 + i * 30,
        "num_comments": 25 + i * 3,
        "shares": 10 + i,
        "folder_id": 104,
        "media_type": "photo",
        "is_verified": True,
        "hashtags": ["nike", "sports", "innovation"],
        "mentions": ["@nikefootball", "@nikewomen"]
    })

def test_production_api():
    """Test if we can reach the production API"""
    print("🧪 TESTING PRODUCTION API CONNECTION")
    print("=" * 50)
    
    try:
        # Test basic connectivity
        response = requests.get(f"{PRODUCTION_URL}/api/", timeout=10)
        print(f"✅ Production API reachable: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Cannot reach production API: {e}")
        return False

def create_job_folders():
    """Create job folders via API"""
    print("\n📁 CREATING JOB FOLDERS VIA API")
    print("=" * 50)
    
    folders_to_create = [
        {"id": 103, "name": "Job 2", "folder_type": "job"},
        {"id": 104, "name": "Job 3", "folder_type": "job"}
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {API_TOKEN}" if API_TOKEN != "your_api_token_here" else ""
    }
    
    for folder_data in folders_to_create:
        try:
            # Try to create folder via unified run folder API
            response = requests.post(
                f"{PRODUCTION_URL}/api/track-accounts/unified-run-folders/",
                json=folder_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Created folder: {folder_data['name']}")
            else:
                print(f"⚠️ Folder {folder_data['name']}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"❌ Failed to create {folder_data['name']}: {e}")

def deploy_scraped_posts():
    """Deploy scraped posts via API"""
    print("\n📄 DEPLOYING SCRAPED POSTS VIA API")
    print("=" * 50)
    
    if API_TOKEN == "your_api_token_here":
        print("❌ API token not provided - cannot create posts")
        print("💡 You need to provide your API token to create posts")
        return
    
    headers = {
        "Content-Type": "application/json", 
        "Authorization": f"Token {API_TOKEN}"
    }
    
    success_count = 0
    
    for i, post_data in enumerate(SAMPLE_POSTS):
        try:
            # Try to create scraped post
            response = requests.post(
                f"{PRODUCTION_URL}/api/brightdata/scraped-posts/",
                json=post_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                success_count += 1
                if i % 10 == 0:  # Progress update every 10 posts
                    print(f"✅ Created {success_count} posts...")
            else:
                print(f"⚠️ Post {i+1}: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Failed to create post {i+1}: {e}")
    
    print(f"✅ Successfully created {success_count}/{len(SAMPLE_POSTS)} posts")

def verify_deployment():
    """Verify the deployment worked"""
    print("\n🔍 VERIFYING DEPLOYMENT")
    print("=" * 50)
    
    # Test the job results endpoints
    for folder_id in [103, 104]:
        try:
            response = requests.get(
                f"{PRODUCTION_URL}/api/brightdata/job-results/{folder_id}/",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                post_count = len(data.get('data', []))
                print(f"✅ Folder {folder_id}: {post_count} posts available")
            else:
                print(f"⚠️ Folder {folder_id}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Failed to verify folder {folder_id}: {e}")

def main():
    """Main deployment function"""
    print("🚀 DIRECT PRODUCTION API DEPLOYMENT")
    print("=" * 60)
    
    # Test API connectivity
    if not test_production_api():
        print("❌ Cannot proceed - API not reachable")
        return
    
    # Create job folders
    create_job_folders()
    
    # Deploy scraped posts
    deploy_scraped_posts()
    
    # Verify deployment
    verify_deployment()
    
    print("\n🎉 DEPLOYMENT PROCESS COMPLETE!")
    print("=" * 50)
    print("Check your data at:")
    print("   📁 Job 2: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/103")
    print("   📁 Job 3: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/104")

if __name__ == "__main__":
    main()