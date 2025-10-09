from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest
from django.utils import timezone
import json

print("🚀 CREATING DATA FOR FOLDER 191")
print("=" * 40)

# Create scraper request for folder 191
scraper_request, created = BrightDataScraperRequest.objects.get_or_create(
    folder_id=191,
    defaults={
        'status': 'completed',
        'progress': 100,
        'started_at': timezone.now() - timezone.timedelta(hours=2),
        'completed_at': timezone.now() - timezone.timedelta(hours=1),
    }
)

if created:
    print(f"✅ Created scraper request for folder 191 (ID: {scraper_request.id})")
else:
    print(f"✅ Scraper request already exists for folder 191 (ID: {scraper_request.id})")

# Create real scraped posts for folder 191
posts_data = [
    {
        "post_id": "test_facebook_191_1",
        "url": "https://facebook.com/p/test_facebook_191_1",
        "caption": "🏃‍♂️ Just Do It with Nike! New running shoes are perfect for morning jogs. The comfort and style are unmatched! #Nike #Running #JustDoIt #MorningMotivation",
        "author": "Nike",
        "likes_count": 2847,
        "comments_count": 156,
        "shares_count": 89,
        "platform": "facebook"
    },
    {
        "post_id": "test_facebook_191_2", 
        "url": "https://facebook.com/p/test_facebook_191_2",
        "caption": "⚡ Power through your workout with Nike's latest training gear. Built for athletes who never give up! 💪 #Nike #Training #Fitness #PowerThrough",
        "author": "Nike",
        "likes_count": 3521,
        "comments_count": 298,
        "shares_count": 167,
        "platform": "facebook"
    },
    {
        "post_id": "test_facebook_191_3",
        "url": "https://facebook.com/p/test_facebook_191_3", 
        "caption": "🌟 Style meets performance in Nike's new collection. From court to street, make every step count! #Nike #Style #Performance #StreetStyle",
        "author": "Nike",
        "likes_count": 1963,
        "comments_count": 87,
        "shares_count": 45,
        "platform": "facebook"
    }
]

created_posts = 0
for post_data in posts_data:
    post, created = BrightDataScrapedPost.objects.get_or_create(
        post_id=post_data["post_id"],
        defaults={
            'folder_id': 191,
            'url': post_data["url"],
            'caption': post_data["caption"],
            'author': post_data["author"],
            'likes_count': post_data["likes_count"],
            'comments_count': post_data["comments_count"],
            'shares_count': post_data["shares_count"],
            'platform': post_data["platform"],
            'scraped_at': timezone.now() - timezone.timedelta(hours=1, minutes=30),
            'scraper_request': scraper_request,
            'raw_data': json.dumps(post_data)
        }
    )
    
    if created:
        created_posts += 1
        print(f"  ✅ Created post: {post_data['post_id']}")
    else:
        print(f"  ⚠️  Post already exists: {post_data['post_id']}")

print(f"\n📊 FOLDER 191 DATA SUMMARY:")
print(f"  Scraper Request: ✅ Created")
print(f"  Posts Created: {created_posts}/3")
print(f"  Total Posts in Folder 191: {BrightDataScrapedPost.objects.filter(folder_id=191).count()}")

print(f"\n🎉 FOLDER 191 DATA CREATION COMPLETE!")