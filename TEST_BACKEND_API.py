#!/usr/bin/env python3
"""
🎯 TEST BACKEND API DIRECTLY
Test your BrightData snapshots through Django's internal API
"""

import os
import sys
import json
import django
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse

def test_backend_api():
    """Test your BrightData snapshots through Django API"""
    
    print("🎯 TESTING BACKEND API FOR YOUR BRIGHTDATA SNAPSHOTS")
    print("=" * 60)
    
    # Create a test client
    client = Client()
    
    # Test Facebook data (Folder 514)
    print("📘 TESTING FACEBOOK DATA (Folder 514):")
    print("-" * 40)
    
    try:
        response = client.get('/api/brightdata/data-storage/run/514/')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ SUCCESS! Facebook data retrieved:")
            print(f"   📁 Folder: {data.get('folder_name', 'Unknown')}")
            print(f"   📊 Total Posts: {data.get('total_results', 0)}")
            print(f"   📋 Status: {data.get('message', 'No message')}")
            
            # Show sample posts
            posts = data.get('data', [])
            if posts:
                print(f"\n   📝 SAMPLE FACEBOOK POSTS:")
                for i, post in enumerate(posts[:3], 1):
                    user = post.get('user_posted', 'Unknown')
                    content = post.get('content', '')[:100]
                    likes = post.get('likes', 0)
                    comments = post.get('num_comments', 0)
                    shares = post.get('shares', 0)
                    
                    print(f"      {i}. {user}: {content}...")
                    print(f"         💖 {likes} likes, 💬 {comments} comments, 🔄 {shares} shares")
                    
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.content.decode()}")
            
    except Exception as e:
        print(f"❌ API Error: {e}")
    
    # Test Instagram data (Folder 515)
    print(f"\n📷 TESTING INSTAGRAM DATA (Folder 515):")
    print("-" * 40)
    
    try:
        response = client.get('/api/brightdata/data-storage/run/515/')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ SUCCESS! Instagram data retrieved:")
            print(f"   📁 Folder: {data.get('folder_name', 'Unknown')}")
            print(f"   📊 Total Posts: {data.get('total_results', 0)}")
            print(f"   📋 Status: {data.get('message', 'No message')}")
            
            # Show sample posts
            posts = data.get('data', [])
            if posts:
                print(f"\n   📝 SAMPLE INSTAGRAM POSTS:")
                for i, post in enumerate(posts[:3], 1):
                    user = post.get('user_posted', 'Unknown')
                    content = post.get('content', '')[:100]
                    likes = post.get('likes', 0)
                    comments = post.get('num_comments', 0)
                    
                    print(f"      {i}. {user}: {content}...")
                    print(f"         💖 {likes} likes, 💬 {comments} comments")
                    
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.content.decode()}")
            
    except Exception as e:
        print(f"❌ API Error: {e}")
    
    print(f"\n" + "=" * 60)
    print("🌐 YOUR BACKEND IS RUNNING AT:")
    print("   • Facebook Data: http://localhost:8000/api/brightdata/data-storage/run/514/")
    print("   • Instagram Data: http://localhost:8000/api/brightdata/data-storage/run/515/")
    print("   • Server: http://localhost:8000/")
    
    print(f"\n🔍 TO VIEW IN BROWSER:")
    print("   1. Keep the Django server running")
    print("   2. Open: http://localhost:8000/api/brightdata/data-storage/run/514/")
    print("   3. Open: http://localhost:8000/api/brightdata/data-storage/run/515/")
    
    return True

if __name__ == "__main__":
    try:
        success = test_backend_api()
        if success:
            print(f"\n✅ BACKEND API TEST COMPLETED!")
        else:
            print(f"\n❌ BACKEND API TEST FAILED!")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()