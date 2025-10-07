#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder

# Check if 32 is a unified run folder
try:
    unified_folder = UnifiedRunFolder.objects.get(id=32)
    print(f"Found UnifiedRunFolder 32:")
    print(f"  Name: {unified_folder.name}")
    print(f"  Folder Type: {unified_folder.folder_type}")
    print(f"  Platform Code: {unified_folder.platform_code}")
    print(f"  Service Code: {unified_folder.service_code}")
    print(f"  Parent Folder: {unified_folder.parent_folder_id}")
    print(f"  Batch Job: {unified_folder.batch_job_id}")
    print(f"  Created: {unified_folder.created_at}")

    if unified_folder.batch_job:
        print(f"\n  Associated Batch Job:")
        print(f"    ID: {unified_folder.batch_job.id}")
        print(f"    Name: {unified_folder.batch_job.name}")
        print(f"    Status: {unified_folder.batch_job.status}")

except UnifiedRunFolder.DoesNotExist:
    print("No UnifiedRunFolder with ID 32")

# List all unified folders
print("\n\nAll UnifiedRunFolders:")
for folder in UnifiedRunFolder.objects.all().order_by('-id')[:20]:
    print(f"  ID {folder.id}: {folder.name} ({folder.folder_type}) - Batch Job: {folder.batch_job_id}")