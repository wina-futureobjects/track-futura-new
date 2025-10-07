#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyBatchJob, ApifyScraperRequest
from instagram_data.models import InstagramPost, Folder

print("Checking batch job data...")
print()

for batch_id in [17, 16, 15, 14, 8]:
    try:
        batch = ApifyBatchJob.objects.get(id=batch_id)
        print(f"Batch {batch_id}: {batch.name}")

        requests = ApifyScraperRequest.objects.filter(batch_job_id=batch_id)
        print(f"  Scraper Requests: {requests.count()}")

        for req in requests:
            # Find folders for this request
            folders = Folder.objects.filter(name__contains=f"Req {req.id}")
            print(f"    Request {req.id} ({req.status}): {folders.count()} folders")

            for folder in folders:
                post_count = folder.posts.count()
                print(f"      Folder {folder.id}: {post_count} posts")

                # Show sample posts
                if post_count > 0:
                    sample_posts = folder.posts.all()[:2]
                    for post in sample_posts:
                        print(f"        - Post {post.id}: {post.description[:50] if post.description else 'No content'}...")

        print()
    except ApifyBatchJob.DoesNotExist:
        print(f"Batch {batch_id}: NOT FOUND")
        print()
