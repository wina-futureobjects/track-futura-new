#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from instagram_data.models import Folder, InstagramPost
from apify_integration.models import ApifyScraperRequest

# Get scraper request 10
req = ApifyScraperRequest.objects.get(id=10)
print(f"Scraper Request: {req.id}")
print(f"Status: {req.status}")
print(f"Run ID: {req.request_id}")

# Check for folders created around the same time
batch_job = req.batch_job
print(f"\nBatch Job: {batch_job.name}")
print(f"Project ID: {batch_job.project.id}")

# Look for folders
folders = Folder.objects.filter(project=batch_job.project).order_by('-created_at')[:10]
print(f"\nRecent Folders for this project:")
for folder in folders:
    post_count = folder.posts.count()
    print(f"  Folder {folder.id}: {folder.name}")
    print(f"    Created: {folder.created_at}")
    print(f"    Posts: {post_count}")
    if post_count > 0:
        print(f"    Sample posts:")
        for post in folder.posts.all()[:3]:
            print(f"      - {post.user_posted}: {post.description[:50] if post.description else 'No description'}")

# Check total Instagram posts
total_posts = InstagramPost.objects.count()
print(f"\nTotal Instagram Posts in DB: {total_posts}")