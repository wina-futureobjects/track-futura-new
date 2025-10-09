import os
import django
from django.utils import timezone

# Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.production')
django.setup()

from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest

# Create request
req, created = BrightDataScraperRequest.objects.get_or_create(
    folder_id=191,
    defaults={
        'platform': 'facebook',
        'status': 'completed',
        'request_id': 'req_191',
        'target_url': 'nike',
        'source_name': 'Nike Official',
        'started_at': timezone.now(),
        'completed_at': timezone.now()
    }
)
print(f"Request: {req.id}")

# Create posts
for i in range(1, 4):
    post, c = BrightDataScrapedPost.objects.get_or_create(
        post_id=f'nike_post_191_{i}',
        defaults={
            'folder_id': 191,
            'content': f'Nike post {i} content #Nike',
            'user_posted': 'Nike',
            'likes': 1000 * i,
            'num_comments': 100 * i,
            'platform': 'facebook',
            'scraper_request': req,
            'date_posted': timezone.now()
        }
    )
    print(f"Post {i}: {'created' if c else 'exists'}")

total = BrightDataScrapedPost.objects.filter(folder_id=191).count()
print(f"Total: {total}")