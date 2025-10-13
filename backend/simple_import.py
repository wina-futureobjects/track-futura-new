"""
Simple BrightData import script - Just store posts directly
"""
import os
import json
from datetime import datetime
from brightdata_integration.models import BrightDataScrapedPost

print("🚀 BrightData Import Started")

# Import Instagram data
instagram_file = r"C:\Users\winam\Downloads\bd_20251013_024949_0.json"
if os.path.exists(instagram_file):
    print("📱 Instagram...")
    with open(instagram_file, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    count = 0
    for i, post in enumerate(posts):
        try:
            obj, created = BrightDataScrapedPost.objects.get_or_create(
                post_id=post.get('post_id', post.get('shortcode', f'ig_{i}')),
                platform='instagram',
                folder_id=400,
                defaults={
                    'user_posted': post.get('user_posted', 'unknown'),
                    'content': post.get('description', ''),
                    'description': post.get('description', ''),
                    'likes': post.get('likes', 0),
                    'num_comments': post.get('num_comments', 0),
                    'date_posted': datetime.fromisoformat(post.get('timestamp', '2025-10-13T02:50:00.000Z').replace('Z', '+00:00')),
                    'url': post.get('url', ''),
                    'raw_data': post
                }
            )
            if created:
                count += 1
        except Exception as e:
            print(f"IG Error: {e}")
    print(f"✅ Instagram: {count} posts")

# Import Facebook data
facebook_file = r"C:\Users\winam\Downloads\bd_20251013_024949_0 (1).json"  
if os.path.exists(facebook_file):
    print("📘 Facebook...")
    with open(facebook_file, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    count = 0
    for i, post in enumerate(posts):
        try:
            obj, created = BrightDataScrapedPost.objects.get_or_create(
                post_id=post.get('post_id', post.get('shortcode', f'fb_{i}')),
                platform='facebook',
                folder_id=401,
                defaults={
                    'user_posted': post.get('user_username_raw', 'unknown'),
                    'content': post.get('content', ''),
                    'description': post.get('content', ''),
                    'likes': post.get('likes', post.get('num_likes_type', {}).get('num', 0)),
                    'num_comments': post.get('num_comments', 0),
                    'date_posted': datetime.fromisoformat(post.get('date_posted', '2025-10-13T02:50:00.000Z').replace('Z', '+00:00')),
                    'url': post.get('url', ''),
                    'raw_data': post
                }
            )
            if created:
                count += 1
        except Exception as e:
            print(f"FB Error: {e}")
    print(f"✅ Facebook: {count} posts")

print("🎉 Done! Check:")
print("📊 http://localhost:8000/api/run-info/400/ (Instagram)")
print("📊 http://localhost:8000/api/run-info/401/ (Facebook)")
print("🌐 Frontend Instagram: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/run/400")
print("🌐 Frontend Facebook: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/run/401")