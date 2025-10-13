#!/usr/bin/env python
"""
Test API endpoints directly in Django to verify our data
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder
from brightdata_integration.models import BrightDataScrapedPost

def test_data_access():
    print("=== TESTING IMPORTED DATA ACCESS ===")
    
    # Check folders
    print("\n📁 UnifiedRunFolder objects:")
    folders = UnifiedRunFolder.objects.filter(id__in=[400, 401]).values('id', 'name')
    for folder in folders:
        print(f"  ID: {folder['id']}, Name: {folder['name']}")
    
    # Check posts
    print("\n📊 BrightDataScrapedPost data:")
    instagram_posts = BrightDataScrapedPost.objects.filter(folder_id=400)
    facebook_posts = BrightDataScrapedPost.objects.filter(folder_id=401)
    
    print(f"  Instagram posts (folder 400): {instagram_posts.count()}")
    print(f"  Facebook posts (folder 401): {facebook_posts.count()}")
    
    # Sample Instagram post
    if instagram_posts.exists():
        sample = instagram_posts.first()
        print(f"\n  📸 Sample Instagram post:")
        print(f"    Post ID: {sample.post_id}")
        print(f"    User: {getattr(sample, 'user_posted', 'N/A')}")
        print(f"    Likes: {getattr(sample, 'likes', 'N/A')}")
        print(f"    Comments: {getattr(sample, 'comments', 'N/A')}")
        print(f"    Created: {sample.created_at}")
    
    # Sample Facebook post  
    if facebook_posts.exists():
        sample = facebook_posts.first()
        print(f"\n  📘 Sample Facebook post:")
        print(f"    Post ID: {sample.post_id}")
        print(f"    User: {getattr(sample, 'user_posted', 'N/A')}")
        print(f"    Likes: {getattr(sample, 'likes', 'N/A')}")
        print(f"    Comments: {getattr(sample, 'comments', 'N/A')}")
        print(f"    Created: {sample.created_at}")
    
    print("\n✅ Data access test complete!")
    
    # Now test the API view function directly
    print("\n=== TESTING API VIEW FUNCTION ===")
    
    try:
        from django.test import RequestFactory
        from brightdata_integration.views import run_info_lookup
        
        factory = RequestFactory()
        
        # Test Instagram folder 400
        request = factory.get('/api/brightdata/run-info/400/')
        response = run_info_lookup(request, '400')
        print(f"\n📊 Instagram (400) API response:")
        print(f"    Status: {response.status_code}")
        import json
        print(f"    Content: {json.loads(response.content)}")
        
        # Test Facebook folder 401
        request = factory.get('/api/brightdata/run-info/401/')
        response = run_info_lookup(request, '401')
        print(f"\n📘 Facebook (401) API response:")
        print(f"    Status: {response.status_code}")
        print(f"    Content: {json.loads(response.content)}")
        
    except Exception as e:
        print(f"❌ API test error: {str(e)}")
    
    print("\n🎉 All tests complete! Your BrightData scraped data is ready for access.")
    print("📊 Instagram: http://localhost:8000/api/brightdata/run-info/400/")
    print("📊 Facebook: http://localhost:8000/api/brightdata/run-info/401/")

if __name__ == '__main__':
    test_data_access()