#!/usr/bin/env python3

import os
import sys
import django
import requests

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_frontend_data():
    """Test the actual API endpoint that the frontend calls"""
    print("🌐 Testing frontend API endpoint...")
    
    try:
        # Test the exact endpoint the frontend calls
        response = requests.get('http://localhost:8000/api/apify/batch-jobs/8/results/')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response successful! Total posts: {len(data)}")
            
            if data and len(data) > 0:
                post = data[0]
                print("\n📱 Sample post structure:")
                print(f"   - ID: {post.get('id', 'N/A')}")
                print(f"   - User: {post.get('user_posted', 'N/A')}")
                description = post.get('description', 'N/A')
                if description and len(description) > 100:
                    print(f"   - Content: {description[:100]}...")
                else:
                    print(f"   - Content: {description}")
                print(f"   - Likes: {post.get('likes', 'N/A')}")
                print(f"   - Comments: {post.get('num_comments', 'N/A')}")
                print(f"   - Date: {post.get('date_posted', 'N/A')}")
                print(f"   - URL: {post.get('url', 'N/A')}")
                
                # Check if it's Nike data
                if post.get('user_posted') == 'nike':
                    print("\n🎯 ✅ Confirmed: Frontend is receiving Nike Instagram data!")
                else:
                    print(f"\n⚠️  Warning: Expected 'nike' user but got '{post.get('user_posted')}'")
            else:
                print("❌ No data returned from API")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")

if __name__ == "__main__":
    test_frontend_data()