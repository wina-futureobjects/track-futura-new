import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import TrackSource, SourceFolder

print("=== ALL SOURCES ===")
sources = TrackSource.objects.all()
print(f"Total: {sources.count()}")
for s in sources:
    print(f"ID: {s.id}, Name: {s.name}, Project: {s.project_id}, Folder ID: {s.folder_id}, Instagram: {s.instagram_link}")

print("\n=== SOURCE FROM FOLDER 1 ===")
folder1 = SourceFolder.objects.get(id=1)
for s in folder1.sources.all():
    print(f"ID: {s.id}, Name: {s.name}, Project: {s.project_id}, Folder ID: {s.folder_id}, Instagram: {s.instagram_link}")
