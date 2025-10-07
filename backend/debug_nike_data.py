#!/usr/bin/env python3

import requests
import json

def debug_nike_data():
    """Debug the Nike data structure"""
    try:
        response = requests.get('http://127.0.0.1:8000/api/apify/batch-jobs/8/results/')
        if response.status_code == 200:
            data = response.json()
            print("🔍 Debugging Nike Data Structure...")
            
            for i, post in enumerate(data['results']):
                print(f"\n📱 Post {i+1}:")
                print(f"   Description: {post.get('description', 'N/A')[:50]}...")
                print(f"   Hashtags: {post.get('hashtags', [])} (type: {type(post.get('hashtags', []))})")
                print(f"   Likes: {post.get('likes', 0):,}")
                print(f"   Comments: {post.get('num_comments', 0)}")
                
                # Check hashtag structure
                hashtags = post.get('hashtags', [])
                if hashtags:
                    print(f"   Hashtag details:")
                    for j, hashtag in enumerate(hashtags):
                        print(f"     {j+1}. {hashtag} (type: {type(hashtag)})")
                
            return data
        else:
            print(f"❌ Error getting data: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    debug_nike_data()