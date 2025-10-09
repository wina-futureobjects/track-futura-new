#!/usr/bin/env python3
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest

print("🚨 EMERGENCY PRODUCTION FIX - REMOVING SAMPLE DATA")
print("=" * 60)

# Delete all sample posts
sample_posts = BrightDataScrapedPost.objects.filter(post_id__startswith='sample_post_')
sample_count = sample_posts.count()
if sample_count > 0:
    sample_posts.delete()
    print(f'🗑️ Deleted {sample_count} fake sample posts')
else:
    print('✅ No sample posts found')

# Delete sample scraper requests  
sample_requests = BrightDataScraperRequest.objects.filter(request_id__startswith='emergency_request_')
request_count = sample_requests.count()
if request_count > 0:
    sample_requests.delete() 
    print(f'🗑️ Deleted {request_count} fake scraper requests')
else:
    print('✅ No sample requests found')

# Check real data
real_posts = BrightDataScrapedPost.objects.exclude(post_id__startswith='sample_post_')
print(f'📊 Real posts in database: {real_posts.count()}')

if real_posts.exists():
    print("\n📝 SAMPLE OF REAL DATA:")
    for i, post in enumerate(real_posts[:3], 1):
        print(f"   {i}. {post.user_posted}: {post.content[:40]}...")
        print(f"      👍 {post.likes} likes, 💬 {post.num_comments} comments")
else:
    print("⚠️ NO REAL DATA FOUND - You need to run a scraping job")

print("\n🎯 WHAT HAPPENS NOW:")
print("1. All fake sample data has been removed from database")
print("2. API will only return real scraped data")
print("3. If no real data exists, API returns empty result")
print("4. No more 'Exciting brand content' fake messages!")

print("\n✅ EMERGENCY FIX COMPLETE - REAL DATA WILL NOW BE SHOWN")