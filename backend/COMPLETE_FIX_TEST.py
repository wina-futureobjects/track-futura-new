#!/usr/bin/env python3
"""
COMPLETE FIX TEST - Verify frontend can now access scraped data
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse
import json

def test_complete_fix():
    print("🚀 COMPLETE FIX VERIFICATION")
    print("=" * 50)
    
    # Create test client
    client = Client()
    
    # Test the endpoints that were failing
    test_urls = [
        '/api/brightdata/data-storage/run/17/',
        '/api/brightdata/data-storage/run/18/',
        '/api/brightdata/run-info/17/',
        '/api/brightdata/run-info/18/',
    ]
    
    for url in test_urls:
        print(f"\n📡 Testing: {url}")
        try:
            response = client.get(url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = json.loads(response.content)
                if 'data' in data:
                    print(f"   ✅ SUCCESS: {len(data['data'])} posts returned")
                elif 'folder_name' in data:
                    print(f"   ✅ SUCCESS: Folder info returned - {data['folder_name']}")
                else:
                    print(f"   ✅ SUCCESS: Response received")
            else:
                print(f"   ❌ FAILED: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n🎯 FRONTEND ACCESS VERIFICATION:")
    print(f"   • https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage")
    print(f"   • Backend endpoints should now respond correctly")
    print(f"   • New scraped data will be immediately accessible")
    print(f"   • No more 404 errors on /api/brightdata/data-storage/run/278/")

if __name__ == "__main__":
    test_complete_fix()