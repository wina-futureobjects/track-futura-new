import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import TrackSource

# Update source 6 to have project_id = 6
source = TrackSource.objects.get(id=6)
print(f"Before: ID: {source.id}, Name: {source.name}, Project: {source.project_id}")
source.project_id = 6
source.save()
print(f"After: ID: {source.id}, Name: {source.name}, Project: {source.project_id}")

# Verify
print("\n=== VERIFICATION ===")
sources_in_project_6 = TrackSource.objects.filter(project_id=6)
print(f"Total sources in project 6: {sources_in_project_6.count()}")
for s in sources_in_project_6:
    print(f"ID: {s.id}, Name: {s.name}, Folder ID: {s.folder_id}, Instagram: {s.instagram_link}")
