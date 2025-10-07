from track_accounts.models import UnifiedRunFolder
from track_accounts.serializers import UnifiedRunFolderSerializer

# Get the folder
f = UnifiedRunFolder.objects.get(id=41)
print(f"Current name: {f.name}")

# Test update via serializer
data = {
    'name': 'Brand Sources - 06/10/2025 14:00:00',
    'description': 'Updated description test'
}

serializer = UnifiedRunFolderSerializer(f, data=data, partial=True)
print(f"Is valid: {serializer.is_valid()}")

if not serializer.is_valid():
    print(f"Errors: {serializer.errors}")
else:
    serializer.save()
    print("Successfully updated!")
    f.refresh_from_db()
    print(f"New name: {f.name}")
    print(f"New description: {f.description}")
