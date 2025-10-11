import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from workflow_management.models import UnifiedRunFolder

# Fix the incorrect post counts
folder_fixes = [
    (240, 0), (239, 0), (237, 0), (236, 0), 
    (235, 0), (233, 0), (232, 0)
]

for folder_id, correct_count in folder_fixes:
    try:
        folder = UnifiedRunFolder.objects.get(id=folder_id)
        old_count = folder.post_count
        folder.post_count = correct_count
        folder.save()
        print(f'Fixed folder {folder_id}: {old_count} -> {correct_count}')
    except UnifiedRunFolder.DoesNotExist:
        print(f'Folder {folder_id} not found')

print('Post count fixes applied!')