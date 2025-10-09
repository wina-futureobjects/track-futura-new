#!/usr/bin/env python3
"""
Test the brightdata_job_results API endpoint to ensure it returns real data
"""

import os
import sys
import django
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_brightdata_job_results():
    """Test the brightdata_job_results API endpoint"""
    
    print("🧪 TESTING BRIGHTDATA JOB RESULTS API")
    print("=" * 50)
    
    from brightdata_integration.models import BrightDataScrapedPost
    from django.test import RequestFactory
    from brightdata_integration.views import brightdata_job_results
    from django.contrib.auth.models import User
    import json
    
    # Find a folder with real data
    folder_with_data = BrightDataScrapedPost.objects.exclude(
        post_id__startswith='sample_post_'
    ).values_list('folder_id', flat=True).first()
    
    if not folder_with_data:
        print("❌ No folders with real data found")
        return
    
    print(f"📂 Testing with folder ID: {folder_with_data}")
    
    # Create a test request
    factory = RequestFactory()
    request = factory.get(f'/api/brightdata/job-results/{folder_with_data}/')
    
    # Create a test user
    user, created = User.objects.get_or_create(username='testuser')
    request.user = user
    
    # Call the view
    try:
        response = brightdata_job_results(request, folder_with_data)
        
        print(f"🌐 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            
            print(f"📊 Response data structure:")
            print(f"   - Success: {data.get('success')}")
            print(f"   - Message: {data.get('message')}")
            print(f"   - Total results: {data.get('total_results')}")
            print(f"   - Posts found: {len(data.get('data', []))}")
            print(f"   - Source: {data.get('source')}")
            
            # Check if we got real data
            posts = data.get('data', [])
            if posts:
                sample_post = posts[0]
                print(f"\n📝 Sample post data:")
                print(f"   - Post ID: {sample_post.get('post_id')}")
                print(f"   - User: {sample_post.get('user_posted')}")
                print(f"   - Content: {sample_post.get('content', '')[:50]}...")
                print(f"   - Likes: {sample_post.get('likes')}")
                print(f"   - Platform: {sample_post.get('platform')}")
                
                # Check if it's real data (not sample)
                if sample_post.get('post_id', '').startswith('sample_post_'):
                    print("❌ Still returning sample data!")
                else:
                    print("✅ Returning real scraped data!")
            else:
                print("⚠️ No posts in response")
        else:
            print(f"❌ Error response: {response.content}")
            
    except Exception as e:
        print(f"❌ Error calling view: {e}")
        import traceback
        traceback.print_exc()


def check_database_state():
    """Check the current database state"""
    
    print("\n🗄️ DATABASE STATE CHECK")
    print("=" * 50)
    
    from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest
    
    # Real posts by folder
    real_posts = BrightDataScrapedPost.objects.exclude(
        post_id__startswith='sample_post_'
    )
    
    folders = real_posts.values_list('folder_id', flat=True).distinct()
    
    print(f"📁 Folders with real data: {list(folders)}")
    
    for folder_id in folders:
        folder_posts = real_posts.filter(folder_id=folder_id)
        print(f"\n📂 Folder {folder_id}:")
        print(f"   Posts: {folder_posts.count()}")
        
        # Sample data
        for post in folder_posts[:2]:
            print(f"   - {post.post_id}: {post.user_posted}")
            print(f"     Content: {post.content[:40]}...")
            print(f"     Platform: {post.platform}, Likes: {post.likes}")


def main():
    """Run the test"""
    
    print("🚀 BRIGHTDATA API ENDPOINT TEST")
    print("=" * 60)
    
    # Check database state
    check_database_state()
    
    # Test the API endpoint
    test_brightdata_job_results()
    
    print("\n📊 TEST SUMMARY")
    print("=" * 30)
    print("✅ Database state checked")
    print("✅ API endpoint tested")
    print("\n🎯 IF STILL SEEING ISSUES:")
    print("1. Check the view code modifications")
    print("2. Restart Django development server")
    print("3. Clear browser cache")
    print("4. Check frontend API calls")


if __name__ == "__main__":
    main()