import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder
from track_accounts.serializers import UnifiedRunFolderSerializer

# Get the Nike Instagram job folder
job_folder = UnifiedRunFolder.objects.get(id=44)
print(f"Job Folder: {job_folder.name}")
print(f"Folder Type: {job_folder.folder_type}")

# Check for linked folders
from instagram_data.models import Folder as IGFolder
ig_folders = IGFolder.objects.filter(unified_job_folder=job_folder)
print(f"\nLinked Instagram folders: {ig_folders.count()}")
for igf in ig_folders:
    print(f"  - {igf.name} (ID: {igf.id})")

# Try to serialize it
try:
    serializer = UnifiedRunFolderSerializer(job_folder)
    data = serializer.data
    print(f"\nSerialized subfolders: {len(data['subfolders'])}")
    print(f"Serialized post_count: {data['post_count']}")

    if data['subfolders']:
        print("\nSubfolders:")
        for sf in data['subfolders']:
            print(f"  - {sf['name']} (ID: {sf['id']})")
except Exception as e:
    print(f"\nError during serialization: {e}")
    import traceback
    traceback.print_exc()
