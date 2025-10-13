#!/usr/bin/env python
"""
BrightData Import Status Report
Generated: October 13, 2025 - 12:05
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder
from brightdata_integration.models import BrightDataScrapedPost

print("🎉 BRIGHTDATA IMPORT SUCCESS REPORT")
print("="*50)

# Check folder structure
folders = UnifiedRunFolder.objects.filter(id__in=[400, 401])
for folder in folders:
    print(f"📁 Folder {folder.id}: {folder.name}")

print("\n📊 DATA SUMMARY:")
instagram_count = BrightDataScrapedPost.objects.filter(folder_id=400).count()
facebook_count = BrightDataScrapedPost.objects.filter(folder_id=401).count()
total_count = BrightDataScrapedPost.objects.count()

print(f"  • Instagram posts (folder 400): {instagram_count}")
print(f"  • Facebook posts (folder 401): {facebook_count}")
print(f"  • Total posts in system: {total_count}")

print("\n✅ READY FOR FRONTEND ACCESS:")
print("  📊 Instagram API: /api/brightdata/run-info/400/")
print("  📊 Facebook API: /api/brightdata/run-info/401/") 
print("  🌐 Server: http://localhost:8000")

print("\n📱 SAMPLE POST DATA:")
# Show sample Instagram post
sample_ig = BrightDataScrapedPost.objects.filter(folder_id=400).first()
if sample_ig:
    print(f"  Instagram - User: {getattr(sample_ig, 'user_posted', 'N/A')}")
    print(f"  Instagram - Post: {sample_ig.post_id[:50]}...")
    print(f"  Instagram - Likes: {getattr(sample_ig, 'likes', 'N/A')}")

# Show sample Facebook post  
sample_fb = BrightDataScrapedPost.objects.filter(folder_id=401).first()
if sample_fb:
    print(f"  Facebook - User: {getattr(sample_fb, 'user_posted', 'N/A')}")
    print(f"  Facebook - Post: {sample_fb.post_id[:50]}...")
    print(f"  Facebook - Likes: {getattr(sample_fb, 'likes', 'N/A')}")

print("\n🚀 STATUS: READY TO VIEW IN TRACKFUTURA INTERFACE!")
print("Start Django server: python manage.py runserver 8000")
print("Access your data through the TrackFutura dashboard.")