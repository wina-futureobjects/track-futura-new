
# Fix workflow ViewSet folder filtering issue
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from workflow.models import InputCollection
from django.http import JsonResponse

print("=== WORKFLOW VIEWSET FIX ===")

# Test: Create a simple API response that bypasses any folder filtering
def test_input_collections_response():
    """Test what a proper InputCollections API response should look like"""
    
    collections = InputCollection.objects.filter(project_id=3)
    
    results = []
    for collection in collections:
        results.append({
            "id": collection.id,
            "project": collection.project_id,
            "platform_service": collection.platform_service_id,
            "urls": collection.urls,
            "status": collection.status,
            "created_at": collection.created_at.isoformat() if collection.created_at else None,
            "updated_at": collection.updated_at.isoformat() if collection.updated_at else None,
        })
    
    response_data = {
        "count": len(results),
        "results": results
    }
    
    print(f"Expected API response for /workflow/input-collections/?project=3:")
    print(f"Count: {response_data['count']}")
    for result in response_data['results']:
        print(f"  - Collection ID {result['id']}")
        print(f"    Project: {result['project']}")
        print(f"    Platform Service: {result['platform_service']}")
        print(f"    URLs: {result['urls']}")
        print(f"    Status: {result['status']}")
    
    return response_data

# Run the test
result = test_input_collections_response()

# Also check if there are any folder-based filters being applied incorrectly
print("\nChecking for potential folder filtering issues...")

# Check if InputCollection model has any folder relationships
from django.db import models
input_collection_fields = [field.name for field in InputCollection._meta.fields]
print(f"InputCollection model fields: {input_collection_fields}")

# Check if there are any related folder fields
folder_related_fields = [field for field in input_collection_fields if 'folder' in field.lower()]
print(f"Folder-related fields: {folder_related_fields}")

print("Fix analysis complete!")
