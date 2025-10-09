#!/usr/bin/env python3

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest

print("🚨 EMERGENCY SAMPLE DATA DELETION")
print("=" * 50)

# Count sample data
sample_posts = BrightDataScrapedPost.objects.filter(post_id__startswith='sample_post_')
sample_requests = BrightDataScraperRequest.objects.filter(request_id__startswith='emergency_request_')

print(f"Sample posts found: {sample_posts.count()}")
print(f"Sample requests found: {sample_requests.count()}")

# Delete sample posts
if sample_posts.exists():
    sample_posts.delete()
    print("✅ Deleted all sample posts")
else:
    print("✅ No sample posts to delete")

# Delete sample requests
if sample_requests.exists():
    sample_requests.delete()
    print("✅ Deleted all sample requests")
else:
    print("✅ No sample requests to delete")

# Check real data
real_posts = BrightDataScrapedPost.objects.exclude(post_id__startswith='sample_post_')
print(f"Real posts remaining: {real_posts.count()}")

if real_posts.exists():
    print("📊 Real posts exist:")
    for post in real_posts[:3]:
        print(f"  - {post.post_id}: {post.user_posted} - {post.content[:30]}...")
else:
    print("⚠️ NO REAL POSTS FOUND")

print("\n🎯 CLEANUP COMPLETE - API SHOULD NOW RETURN REAL DATA OR EMPTY RESULT")