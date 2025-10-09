#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.production')
django.setup()

from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest
from django.utils import timezone
import json

print("Creating data for folder 191...")

# Create scraper request
scraper_request, created = BrightDataScraperRequest.objects.get_or_create(
    folder_id=191,
    defaults={
        'status': 'completed',
        'progress': 100,
        'started_at': timezone.now() - timezone.timedelta(hours=2),
        'completed_at': timezone.now() - timezone.timedelta(hours=1),
    }
)

print(f"Scraper request: {'Created' if created else 'Exists'}")

# Create posts
posts = [
    {
        'post_id': 'test_facebook_191_1',
        'url': 'https://facebook.com/p/test_facebook_191_1',
        'caption': 'Nike running shoes for morning jogs #Nike #Running',
        'author': 'Nike',
        'likes_count': 2847,
        'platform': 'facebook'
    },
    {
        'post_id': 'test_facebook_191_2',
        'url': 'https://facebook.com/p/test_facebook_191_2',
        'caption': 'Nike training gear for athletes #Nike #Training',
        'author': 'Nike',
        'likes_count': 3521,
        'platform': 'facebook'
    },
    {
        'post_id': 'test_facebook_191_3',
        'url': 'https://facebook.com/p/test_facebook_191_3',
        'caption': 'Nike style and performance #Nike #Style',
        'author': 'Nike',
        'likes_count': 1963,
        'platform': 'facebook'
    }
]

created_count = 0
for post_data in posts:
    post, created = BrightDataScrapedPost.objects.get_or_create(
        post_id=post_data['post_id'],
        defaults={
            'folder_id': 191,
            'url': post_data['url'],
            'caption': post_data['caption'],
            'author': post_data['author'],
            'likes_count': post_data['likes_count'],
            'platform': post_data['platform'],
            'scraper_request': scraper_request,
            'scraped_at': timezone.now()
        }
    )
    if created:
        created_count += 1

print(f"Created {created_count} posts")
print(f"Total posts in folder 191: {BrightDataScrapedPost.objects.filter(folder_id=191).count()}")
print("Done!")