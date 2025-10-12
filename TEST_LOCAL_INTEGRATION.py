#!/usr/bin/env python3
"""
Test the endpoints locally to verify integration is working
"""

import os
import sys
import django
import json

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from brightdata_integration.views import data_storage_folder_scrape
from brightdata_integration.models import BrightDataScrapedPost

def test_local_endpoint():
    """Test the endpoint locally to verify it works"""
    
    print("🧪 TESTING LOCAL ENDPOINT INTEGRATION")
    print("=" * 60)
    
    # Create a fake request
    factory = RequestFactory()
    
    # Test with "Job 3" which we know has data
    print("\n📋 Testing endpoint: data_storage_folder_scrape('Job 3', 1)")
    
    request = factory.get('/api/brightdata/data-storage/Job%203/1/')
    response = data_storage_folder_scrape(request, 'Job 3', 1)
    
    print(f"   Response status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            response_data = json.loads(response.content)
            print(f"   ✅ Success: {response_data.get('success')}")
            print(f"   Folder: {response_data.get('folder_name')}")
            print(f"   Scrape: {response_data.get('scrape_number')}")
            print(f"   Total results: {response_data.get('total_results')}")
            
            if response_data.get('data'):
                sample_post = response_data['data'][0]
                print(f"   Sample post:")
                print(f"     - Platform: {sample_post.get('platform')}")
                print(f"     - User: {sample_post.get('user_posted')}")
                print(f"     - URL: {sample_post.get('url')}")
                print(f"     - Likes: {sample_post.get('likes')}")
                print(f"     - Content: {sample_post.get('content', '')[:50]}...")
        except Exception as e:
            print(f"   ❌ Error parsing response: {e}")
            print(f"   Raw response: {response.content[:200]}...")
    else:
        print(f"   ❌ Error response: {response.content}")
    
    # Test with Job 2
    print("\n📋 Testing endpoint: data_storage_folder_scrape('Job 2', 1)")
    
    request = factory.get('/api/brightdata/data-storage/Job%202/1/')
    response = data_storage_folder_scrape(request, 'Job 2', 1)
    
    print(f"   Response status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            response_data = json.loads(response.content)
            print(f"   ✅ Success: {response_data.get('success')}")
            print(f"   Total results: {response_data.get('total_results')}")
        except Exception as e:
            print(f"   ❌ Error parsing response: {e}")
    
    # Test with non-existent folder
    print("\n📋 Testing endpoint: data_storage_folder_scrape('NonExistent', 1)")
    
    request = factory.get('/api/brightdata/data-storage/NonExistent/1/')
    response = data_storage_folder_scrape(request, 'NonExistent', 1)
    
    print(f"   Response status: {response.status_code}")
    print(f"   Expected 404 for non-existent folder: {'✅' if response.status_code == 404 else '❌'}")

def check_missing_imports():
    """Check if any imports are missing in views.py"""
    
    print("\n🔍 CHECKING VIEW IMPORTS")
    print("=" * 60)
    
    try:
        from brightdata_integration.views import (
            data_storage_folder_scrape,
            data_storage_folder_scrape_platform,
            data_storage_folder_scrape_platform_post,
            data_storage_folder_scrape_platform_post_account
        )
        print("   ✅ All view functions imported successfully")
        
        from brightdata_integration.models import (
            BrightDataScrapedPost,
            BrightDataScraperRequest
        )
        print("   ✅ All models imported successfully")
        
        from track_accounts.models import UnifiedRunFolder
        print("   ✅ UnifiedRunFolder imported successfully")
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 LOCAL INTEGRATION TEST")
    print("=" * 70)
    
    if check_missing_imports():
        test_local_endpoint()
    
    print("\n" + "=" * 70)
    print("🎯 SUMMARY:")
    print("- If local tests pass: Integration is working, just waiting for deployment")
    print("- If local tests fail: Need to fix integration issues")
    print("=" * 70)