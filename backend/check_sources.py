import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import TrackSource, SourceFolder

print("=== ALL SOURCES IN PROJECT 6 ===")
sources = TrackSource.objects.filter(project_id=6)
print(f"Total: {sources.count()}")
for s in sources:
    print(f"ID: {s.id}, Name: {s.name}, Folder ID: {s.folder_id}, Instagram: {s.instagram_link}")

print("\n=== ALL FOLDERS IN PROJECT 6 ===")
folders = SourceFolder.objects.filter(project_id=6)
print(f"Total: {folders.count()}")
for f in folders:
    print(f"ID: {f.id}, Name: {f.name}, Type: {f.folder_type}, Sources: {f.sources.count()}")
