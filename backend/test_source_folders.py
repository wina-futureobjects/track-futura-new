#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.serializers import SourceFolderSerializer
from track_accounts.models import SourceFolder

# Test the updated serializer
from django.db.models import Q
nike_adidas_folders = SourceFolder.objects.filter(
    Q(name__icontains='Nike') | Q(name__icontains='Adidas')
)

serializer = SourceFolderSerializer(nike_adidas_folders, many=True)

print("Updated source counts:")
for folder_data in serializer.data:
    print(f"  {folder_data['name']}: {folder_data['source_count']} posts available")

print("\nDirect Facebook folder check:")
from facebook_data.models import Folder as FacebookFolder
try:
    nike_folder = FacebookFolder.objects.get(id=21)
    print(f"  Nike folder (21): {nike_folder.posts.count()} posts")
except:
    print("  Nike folder (21): Not found")

try:
    adidas_folder = FacebookFolder.objects.get(id=20)
    print(f"  Adidas folder (20): {adidas_folder.posts.count()} posts")
except:
    print("  Adidas folder (20): Not found")