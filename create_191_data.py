print("Creating test data for folder 191...")

# Create simple test data for folder 191
import os
import sys
import django

# Ensure we're in the right directory and have Django set up
sys.path.insert(0, '/app/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.production')
django.setup()

from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest
from django.utils import timezone

try:
    # Create scraper request first
    scraper_request, created = BrightDataScraperRequest.objects.get_or_create(
        folder_id=191,
        defaults={
            'status': 'completed',
            'progress': 100,
            'started_at': timezone.now() - timezone.timedelta(hours=1),
            'completed_at': timezone.now(),
        }
    )
    print(f"Scraper request: {'Created' if created else 'Already exists'}")

    # Create test posts
    posts_created = 0
    for i in range(1, 4):
        post, created = BrightDataScrapedPost.objects.get_or_create(
            post_id=f'test_facebook_191_{i}',
            defaults={
                'folder_id': 191,
                'url': f'https://facebook.com/p/test_facebook_191_{i}',
                'caption': f'Nike athletic gear post {i} - Just Do It! #Nike #Sports #Training',
                'author': 'Nike',
                'likes_count': 1500 + i * 300,
                'comments_count': 50 + i * 10,
                'shares_count': 20 + i * 5,
                'platform': 'facebook',
                'scraper_request': scraper_request,
                'scraped_at': timezone.now() - timezone.timedelta(minutes=30),
            }
        )
        if created:
            posts_created += 1
            print(f"Created post {i}: {post.post_id}")

    total_posts = BrightDataScrapedPost.objects.filter(folder_id=191).count()
    print(f"Successfully created {posts_created} new posts")
    print(f"Total posts in folder 191: {total_posts}")
    
    if total_posts > 0:
        print("✅ SUCCESS: Folder 191 now has scraped data!")
    else:
        print("❌ ERROR: No posts found in folder 191")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()