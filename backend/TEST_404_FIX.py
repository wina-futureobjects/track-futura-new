#!/usr/bin/env python3
"""
URGENT: Test and fix the 404 error on /api/brightdata/data-storage/run/17/
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import resolve, reverse
from django.urls.exceptions import Resolver404
import json

def test_run_endpoint_404():
    print("🚨 URGENT: FIX 404 ERROR ON /api/brightdata/data-storage/run/17/")
    print("=" * 70)
    
    client = Client()
    
    # Test URL resolution first
    test_urls = [
        '/api/brightdata/data-storage/run/17/',
        '/api/brightdata/data-storage/run/18/', 
        '/api/brightdata/run-info/17/',
        '/api/brightdata/run-info/18/',
    ]
    
    print(f"\n🔍 URL RESOLUTION TEST:")
    for url in test_urls:
        try:
            match = resolve(url)
            print(f"   ✅ {url} → {match.func.__name__}")
        except Resolver404:
            print(f"   ❌ {url} → NOT FOUND")
    
    print(f"\n📡 ENDPOINT RESPONSE TEST:")
    for url in test_urls:
        try:
            response = client.get(url)
            print(f"   {url}")
            print(f"   └── Status: {response.status_code}")
            
            if response.status_code == 200:
                data = json.loads(response.content)
                if 'data' in data:
                    print(f"   └── ✅ SUCCESS: {len(data['data'])} posts")
                elif 'folder_name' in data:
                    print(f"   └── ✅ SUCCESS: {data['folder_name']}")
                else:
                    print(f"   └── ✅ SUCCESS: Response OK")
            elif response.status_code == 404:
                print(f"   └── ❌ 404 NOT FOUND")
                print(f"   └── Response: {response.content.decode()}")
            else:
                print(f"   └── ⚠️  Status {response.status_code}")
                print(f"   └── Response: {response.content.decode()}")
        except Exception as e:
            print(f"   └── ❌ ERROR: {e}")
        print()

    # Check if the function exists
    print(f"\n🔧 FUNCTION AVAILABILITY CHECK:")
    try:
        from brightdata_integration.views import data_storage_run_endpoint
        print(f"   ✅ data_storage_run_endpoint function exists")
    except ImportError:
        print(f"   ❌ data_storage_run_endpoint function NOT FOUND")
    
    # Check database content
    from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
    
    print(f"\n📊 DATABASE STATUS:")
    for run_id in [17, 18]:
        try:
            request = BrightDataScraperRequest.objects.get(id=run_id)
            posts = BrightDataScrapedPost.objects.filter(folder_id=request.folder_id)
            print(f"   Run {run_id}: {posts.count()} posts in folder {request.folder_id}")
        except BrightDataScraperRequest.DoesNotExist:
            print(f"   Run {run_id}: ❌ Request not found")

if __name__ == "__main__":
    test_run_endpoint_404()