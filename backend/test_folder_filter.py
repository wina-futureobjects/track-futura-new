import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import TrackSource
from django.db.models import Q

print("=== TEST FOLDER FILTER ===")

# Test 1: All sources in project 6
sources_project_6 = TrackSource.objects.filter(project_id=6)
print(f"\n1. All sources in project 6: {sources_project_6.count()}")
for s in sources_project_6:
    print(f"   - ID {s.id}: {s.name}, Folder: {s.folder_id}, Instagram: {s.instagram_link}")

# Test 2: Sources in project 6 with folder 1
sources_folder_1 = TrackSource.objects.filter(project_id=6, folder_id=1)
print(f"\n2. Sources in project 6 with folder 1: {sources_folder_1.count()}")
for s in sources_folder_1:
    print(f"   - ID {s.id}: {s.name}, Folder: {s.folder_id}, Instagram: {s.instagram_link}")

# Test 3: Sources in project 6 with folder 1 AND Instagram
sources_folder_1_instagram = TrackSource.objects.filter(
    project_id=6,
    folder_id=1
).exclude(
    Q(instagram_link__isnull=True) | Q(instagram_link='')
)
print(f"\n3. Sources in project 6 with folder 1 AND Instagram: {sources_folder_1_instagram.count()}")
for s in sources_folder_1_instagram:
    print(f"   - ID {s.id}: {s.name}, Folder: {s.folder_id}, Instagram: {s.instagram_link}")

#Test 4: Check the actual Instagram link value
source_6 = TrackSource.objects.get(id=6)
print(f"\n4. Source 6 details:")
print(f"   - Name: {source_6.name}")
print(f"   - Project ID: {source_6.project_id}")
print(f"   - Folder ID: {source_6.folder_id}")
print(f"   - Instagram link: '{source_6.instagram_link}'")
print(f"   - Instagram link is None: {source_6.instagram_link is None}")
print(f"   - Instagram link is empty: {source_6.instagram_link == ''}")
print(f"   - Instagram link type: {type(source_6.instagram_link)}")
print(f"   - Instagram link length: {len(source_6.instagram_link) if source_6.instagram_link else 0}")
