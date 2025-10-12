#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder
from brightdata_integration.models import BrightDataScrapedPost

print("📋 ALL FOLDERS:")
folders = UnifiedRunFolder.objects.all().order_by('-id')
for folder in folders:
    posts_count = BrightDataScrapedPost.objects.filter(folder_id=folder.id).count()
    print(f"   Folder ID: {folder.id}, Name: {folder.name}, Posts: {posts_count}")

print(f"\n📊 Total folders: {UnifiedRunFolder.objects.count()}")
if folders.exists():
    print(f"📊 Highest folder ID: {folders.first().id}")
else:
    print("📊 No folders found")

# Check if folder 286 exists anywhere
print(f"\n🔍 SEARCHING FOR ANYTHING WITH '286':")
folders_with_286 = UnifiedRunFolder.objects.filter(name__icontains='286')
if folders_with_286.exists():
    for folder in folders_with_286:
        print(f"   Found folder with '286' in name: ID {folder.id}, Name: {folder.name}")
else:
    print("   No folders with '286' in name found")