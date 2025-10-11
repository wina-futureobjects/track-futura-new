#!/usr/bin/env python3
"""
🚀 PRODUCTION DATA POPULATION VIA WEBHOOK
========================================
This will populate your production database via the webhook endpoint
"""

import requests
import json
import time
from datetime import datetime, timedelta

def populate_production_data():
    print("🚀 POPULATING PRODUCTION DATABASE VIA WEBHOOK")
    print("=" * 60)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    webhook_url = f"{base_url}/api/brightdata/webhook/"
    
    posts_to_create = []
    
    # Create Instagram posts for Job 2 (folder 103)
    for i in range(1, 21):
        posts_to_create.append({
            "post_id": f"prod_insta_{i}_{int(time.time())}",
            "url": f"https://instagram.com/p/production_post_{i}/",
            "content": f"Production Instagram post {i} - Nike Air Max collection. Just Do It! #nike #justdoit #airmax",
            "platform": "instagram",
            "user_posted": f"nike_official_{i}",
            "likes": 500 + (i * 25),
            "num_comments": 15 + (i * 2),
            "shares": 5 + i,
            "folder_id": 103,
            "date_posted": (datetime.now() - timedelta(days=i)).isoformat(),
            "media_type": "photo",
            "is_verified": i % 3 == 0,
            "hashtags": ["nike", "justdoit", "airmax"],
            "mentions": ["@nike", "@nikesportswear"]
        })
    
    # Create Facebook posts for Job 3 (folder 104)
    for i in range(1, 21):
        posts_to_create.append({
            "post_id": f"prod_fb_{i}_{int(time.time())}",
            "url": f"https://facebook.com/nike/posts/production_{i}",
            "content": f"Production Facebook post {i} - New Nike collection available now! Experience the innovation.",
            "platform": "facebook",
            "user_posted": f"nike_page_{i}",
            "likes": 750 + (i * 30),
            "num_comments": 25 + (i * 3),
            "shares": 10 + i,
            "folder_id": 104,
            "date_posted": (datetime.now() - timedelta(days=i)).isoformat(),
            "media_type": "photo",
            "is_verified": True,
            "hashtags": ["nike", "sports", "innovation"],
            "mentions": ["@nikefootball", "@nikewomen"]
        })
    
    print(f"📊 Created {len(posts_to_create)} posts to upload")
    
    # Send posts via webhook
    success_count = 0
    
    for i, post_data in enumerate(posts_to_create, 1):
        try:
            response = requests.post(
                webhook_url,
                json=post_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                success_count += 1
                if i % 10 == 0:
                    print(f"✅ Created {success_count} posts...")
            else:
                print(f"⚠️ Post {i}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Failed to create post {i}: {e}")
    
    print(f"📈 Successfully created {success_count} out of {len(posts_to_create)} posts")
    
    # Test data availability
    print(f"\n🧪 TESTING DATA AVAILABILITY")
    print("=" * 40)
    
    for folder_id, folder_name in [(103, "Job 2"), (104, "Job 3")]:
        try:
            response = requests.get(f"{base_url}/api/brightdata/job-results/{folder_id}/", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ {folder_name} ({folder_id}): {data.get('total_results', 0)} posts available")
                else:
                    print(f"❌ {folder_name} ({folder_id}): {data.get('error', 'Unknown error')}")
            else:
                print(f"⚠️ {folder_name} ({folder_id}): Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {folder_name} ({folder_id}): Error testing - {e}")
    
    print(f"\n🎉 DEPLOYMENT COMPLETE!")
    print("=" * 40)
    print("Check your data at:")
    print(f"   📁 Job 2: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/103")
    print(f"   📁 Job 3: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/104")

if __name__ == "__main__":
    populate_production_data()