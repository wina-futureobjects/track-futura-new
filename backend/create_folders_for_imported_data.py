#!/usr/bin/env python
"""
Create UnifiedRunFolder objects for our imported BrightData scraped data
"""

from track_accounts.models import UnifiedRunFolder

# Create folder 400 for Instagram data
instagram_folder, created = UnifiedRunFolder.objects.get_or_create(
    id=400,
    defaults={
        'name': 'BrightData Instagram Collection',
        'project_id': 1,
        'folder_type': 'run'
    }
)

if created:
    print(f"✅ Created Instagram folder: {instagram_folder.name} (ID: {instagram_folder.id})")
else:
    print(f"📁 Instagram folder already exists: {instagram_folder.name} (ID: {instagram_folder.id})")

# Create folder 401 for Facebook data
facebook_folder, created = UnifiedRunFolder.objects.get_or_create(
    id=401,
    defaults={
        'name': 'BrightData Facebook Collection',
        'project_id': 1,
        'folder_type': 'run'
    }
)

if created:
    print(f"✅ Created Facebook folder: {facebook_folder.name} (ID: {facebook_folder.id})")
else:
    print(f"📁 Facebook folder already exists: {facebook_folder.name} (ID: {facebook_folder.id})")

print("\n🎉 Folder structure ready! API endpoints should now work:")
print("📊 Instagram: http://localhost:8000/api/brightdata/run-info/400/")
print("📊 Facebook: http://localhost:8000/api/brightdata/run-info/401/")