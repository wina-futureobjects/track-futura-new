#!/usr/bin/env python3

import requests
import json

def test_api():
    """Simple API test"""
    try:
        print("🌐 Testing API endpoint...")
        response = requests.get('http://localhost:8000/api/apify/batch-jobs/8/results/')
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Got {len(data)} posts")
            
            if data:
                first_post = data[0]
                print(f"First post user: {first_post.get('user_posted')}")
                print(f"First post content: {first_post.get('description', '')[:50]}...")
                
                if first_post.get('user_posted') == 'nike':
                    print("🎯 ✅ SUCCESS: Nike data is being returned!")
                else:
                    print(f"⚠️ Got user: {first_post.get('user_posted')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_api()