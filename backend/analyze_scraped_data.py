#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from instagram_data.models import InstagramPost, Folder as InstagramFolder
from facebook_data.models import FacebookPost, Folder as FacebookFolder
from track_accounts.models import TrackSource, SourceFolder
from users.models import Project

print("=== DATA STORAGE ANALYSIS ===")

# Check projects
projects = Project.objects.all()
print(f"Total Projects: {projects.count()}")
for project in projects:
    print(f"  - Project {project.id}: {project.name}")

# Check source folders and their types
source_folders = SourceFolder.objects.all()
print(f"\nSource Folders: {source_folders.count()}")
for folder in source_folders:
    print(f"  - {folder.name} (Type: {folder.folder_type})")

# Check track sources
track_sources = TrackSource.objects.all()
print(f"\nTrack Sources: {track_sources.count()}")
for source in track_sources:
    print(f"  - {source.name} (Instagram: {source.instagram_link}, Project: {source.project_id})")
    if source.folder:
        print(f"    → Folder: {source.folder.name} ({source.folder.folder_type})")

# Check Instagram data
instagram_folders = InstagramFolder.objects.all()
print(f"\nInstagram Folders: {instagram_folders.count()}")
for folder in instagram_folders:
    posts_count = InstagramPost.objects.filter(folder=folder).count()
    print(f"  - {folder.name} (Project: {folder.project_id}, Posts: {posts_count})")

# Check Facebook data
facebook_folders = FacebookFolder.objects.all()
print(f"\nFacebook Folders: {facebook_folders.count()}")
for folder in facebook_folders:
    posts_count = FacebookPost.objects.filter(folder=folder).count()
    print(f"  - {folder.name} (Project: {folder.project_id}, Posts: {posts_count})")

# Sample some Instagram posts to see usernames
instagram_posts = InstagramPost.objects.all()[:10]
print(f"\nSample Instagram Posts: {instagram_posts.count()}")
for post in instagram_posts:
    print(f"  - User: {post.user_posted}, Likes: {getattr(post, 'likes_count', getattr(post, 'like_count', 'N/A'))}, Folder: {post.folder.name}")

# Sample some Facebook posts to see usernames
facebook_posts = FacebookPost.objects.all()[:10]
print(f"\nSample Facebook Posts: {facebook_posts.count()}")
for post in facebook_posts:
    print(f"  - User: {post.user_posted}, Likes: {getattr(post, 'likes_count', getattr(post, 'like_count', 'N/A'))}, Folder: {post.folder.name}")

print("\n=== NIKE vs ADIDAS ANALYSIS ===")
# Check for Nike/Adidas related posts
nike_instagram = InstagramPost.objects.filter(user_posted__icontains='nike').count()
adidas_instagram = InstagramPost.objects.filter(user_posted__icontains='adidas').count()
nike_facebook = FacebookPost.objects.filter(user_posted__icontains='nike').count()
adidas_facebook = FacebookPost.objects.filter(user_posted__icontains='adidas').count()

print(f"Nike Posts - Instagram: {nike_instagram}, Facebook: {nike_facebook}")
print(f"Adidas Posts - Instagram: {adidas_instagram}, Facebook: {adidas_facebook}")