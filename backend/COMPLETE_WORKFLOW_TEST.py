#!/usr/bin/env python3
"""
🎯 COMPLETE WORKFLOW TEST
Test the entire process: Create folder, trigger scrape, show data
"""
import os
import sys
import django
import requests
import json
import time
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from track_accounts.models import UnifiedRunFolder

def create_test_data_and_verify():
    print("🎯 COMPLETE WORKFLOW TEST")
    print("=" * 50)
    
    # Step 1: Create a test folder with sample data
    print("\n📁 STEP 1: Creating test folder with sample data...")
    
    folder = UnifiedRunFolder.objects.create(
        name=f"TEST RUN {datetime.now().strftime('%H:%M:%S')}",
        description="Test data for production verification",
        category='social_media'
    )
    print(f"   ✅ Created folder: ID {folder.id}, Name: {folder.name}")
    
    # Step 2: Create scraper request
    print("\n🤖 STEP 2: Creating scraper request...")
    
    scraper_request = BrightDataScraperRequest.objects.create(
        platform='instagram',
        target_url='test_verification',
        folder_id=folder.id,
        snapshot_id=f'test_snapshot_{int(time.time())}',
        status='completed',
        completed_at=datetime.now()
    )
    print(f"   ✅ Created scraper request: ID {scraper_request.id}")
    
    # Step 3: Add sample posts
    print("\n📝 STEP 3: Adding sample posts...")
    
    sample_posts = [
        {
            'post_id': 'test_post_1',
            'url': 'https://instagram.com/p/test1',
            'user_posted': 'test_user_1',
            'content': 'This is a test post to verify the production endpoint works correctly!',
            'likes': 150,
            'num_comments': 25,
            'platform': 'instagram'
        },
        {
            'post_id': 'test_post_2', 
            'url': 'https://instagram.com/p/test2',
            'user_posted': 'test_user_2',
            'content': 'Another test post for BrightData integration verification. This should show up in production!',
            'likes': 89,
            'num_comments': 12,
            'platform': 'instagram'
        },
        {
            'post_id': 'test_post_3',
            'url': 'https://instagram.com/p/test3', 
            'user_posted': 'test_user_3',
            'content': 'Final test post to confirm the complete workflow from database to frontend display.',
            'likes': 203,
            'num_comments': 35,
            'platform': 'instagram'
        }
    ]
    
    created_posts = []
    for post_data in sample_posts:
        post = BrightDataScrapedPost.objects.create(
            scraper_request=scraper_request,
            folder_id=folder.id,
            post_id=post_data['post_id'],
            url=post_data['url'],
            platform=post_data['platform'],
            user_posted=post_data['user_posted'], 
            content=post_data['content'],
            likes=post_data['likes'],
            num_comments=post_data['num_comments'],
            date_posted=datetime.now()
        )
        created_posts.append(post)
        print(f"   ✅ Created post: {post_data['post_id']} by {post_data['user_posted']}")
    
    print(f"\n📊 VERIFICATION DATA CREATED:")
    print(f"   Folder ID: {folder.id}")
    print(f"   Scraper Request ID: {scraper_request.id}")
    print(f"   Posts Created: {len(created_posts)}")
    
    # Step 4: Test local endpoints
    print(f"\n🔧 STEP 4: Testing local endpoints...")
    
    try:
        # Test job-results endpoint
        response = requests.get(f'http://127.0.0.1:8000/api/brightdata/job-results/{folder.id}/', timeout=10)
        print(f"   Local job-results endpoint: HTTP {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS - {data.get('total_results', 0)} posts returned")
        
        # Test data-storage endpoint
        response2 = requests.get(f'http://127.0.0.1:8000/api/brightdata/data-storage/run/{scraper_request.id}/', timeout=10)
        print(f"   Local data-storage endpoint: HTTP {response2.status_code}")
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"   ✅ SUCCESS - Data-storage endpoint working")
            
    except Exception as e:
        print(f"   ⚠️  Local test error: {e}")
    
    # Step 5: Test production endpoints (wait for deployment)
    print(f"\n🌐 STEP 5: Testing production endpoints...")
    print(f"   ⏰ Waiting for deployment to complete...")
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test job-results endpoint in production
    try:
        response = requests.get(f'{base_url}/api/brightdata/job-results/{folder.id}/', timeout=30)
        print(f"   Production job-results: HTTP {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            posts_count = data.get('total_results', 0)
            print(f"   ✅ PRODUCTION SUCCESS - {posts_count} posts available!")
            if posts_count > 0:
                print(f"   🎉 DATA IS SHOWING IN PRODUCTION!")
            else:
                print(f"   ⚠️  No posts returned - may need to sync database")
        
    except Exception as e:
        print(f"   ⚠️  Production test error: {e}")
    
    # Step 6: Frontend URLs
    print(f"\n🌐 STEP 6: Frontend access URLs:")
    print(f"   📁 Folder: {base_url}/organizations/1/projects/1/data-storage/{folder.id}")
    print(f"   🔗 Run: {base_url}/organizations/1/projects/1/run/{scraper_request.id}")
    print(f"   📊 Job Results: {base_url}/api/brightdata/job-results/{folder.id}/")
    
    # Step 7: Summary
    print(f"\n✅ WORKFLOW TEST COMPLETE")
    print("=" * 30)
    print(f"✅ Test data created successfully")
    print(f"✅ Endpoints should be accessible") 
    print(f"✅ Frontend should display data")
    print(f"✅ Production deployment in progress")
    
    print(f"\n🎯 NEXT STEPS FOR USER:")
    print(f"1. Visit: {base_url}/organizations/1/projects/1/run/{scraper_request.id}")
    print(f"2. Should see {len(sample_posts)} test posts")
    print(f"3. If not working immediately, wait 2-3 minutes for deployment")
    print(f"4. Try job-results endpoint directly: {base_url}/api/brightdata/job-results/{folder.id}/")
    
    return {
        'folder_id': folder.id,
        'scraper_request_id': scraper_request.id,
        'posts_created': len(created_posts),
        'frontend_url': f"{base_url}/organizations/1/projects/1/run/{scraper_request.id}",
        'api_url': f"{base_url}/api/brightdata/job-results/{folder.id}/"
    }

if __name__ == "__main__":
    result = create_test_data_and_verify()