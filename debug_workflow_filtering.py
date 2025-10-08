
# Check workflow ViewSet filtering
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from workflow.models import InputCollection, PlatformService
from track_accounts.models import SourceFolder

print("=== WORKFLOW FILTERING DEBUG ===")

# Check all InputCollections
all_collections = InputCollection.objects.all()
print(f"Total InputCollections in database: {all_collections.count()}")

for collection in all_collections:
    print(f"  - ID {collection.id}: {collection.project_id}")
    print(f"    Platform Service: {collection.platform_service}")
    print(f"    URLs: {collection.urls}")
    print(f"    Status: {collection.status}")

# Check if there's any folder-based filtering happening
print("\nChecking SourceFolders:")
folders = SourceFolder.objects.filter(project_id=3)
for folder in folders:
    print(f"  - Folder: {folder.name} (Type: {folder.folder_type})")

# Check PlatformServices
platform_services = PlatformService.objects.all()
print(f"\nPlatformServices count: {platform_services.count()}")
for ps in platform_services:
    print(f"  - ID {ps.id}: {ps}")

print("\nChecking if InputCollection is project-filtered correctly...")
project_3_collections = InputCollection.objects.filter(project_id=3)
print(f"Project 3 InputCollections: {project_3_collections.count()}")

print("Debug complete!")
