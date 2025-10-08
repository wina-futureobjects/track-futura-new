#!/usr/bin/env python3
"""
INPUT COLLECTION FOLDER ISSUE FIX
Check and fix InputCollection folder-based filtering
"""

import requests
import subprocess

def check_input_collection_folder_issue():
    """Check if InputCollection is filtered by folder name incorrectly"""
    print("🔍 Investigating InputCollection Folder Issue...")
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api"
    
    # Test 1: Check InputCollections without any filters
    print("\n📋 Test 1: All InputCollections")
    try:
        response = requests.get(f"{BASE_URL}/workflow/input-collections/")
        if response.status_code == 200:
            data = response.json()
            collections = data.get('results', data) if isinstance(data, dict) else data
            print(f"✅ Total InputCollections: {len(collections)}")
            
            for collection in collections:
                print(f"   - ID: {collection.get('id')}")
                print(f"     Name: {collection.get('name')}")
                print(f"     Project: {collection.get('project')}")
                print(f"     Platform Service: {collection.get('platform_service')}")
                print(f"     URLs: {collection.get('urls')}")
                print(f"     Status: {collection.get('status')}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 2: Check with project filter
    print("\n📋 Test 2: InputCollections for Project 3")
    try:
        response = requests.get(f"{BASE_URL}/workflow/input-collections/?project=3")
        if response.status_code == 200:
            data = response.json()
            collections = data.get('results', data) if isinstance(data, dict) else data
            print(f"✅ Project 3 InputCollections: {len(collections)}")
            
            for collection in collections:
                print(f"   - ID: {collection.get('id')}: {collection.get('name')}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Check available platforms endpoint
    print("\n📋 Test 3: Available Platforms")
    try:
        response = requests.get(f"{BASE_URL}/workflow/available-platforms/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available platforms response: {data}")
        else:
            print(f"❌ Available platforms failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 4: Check platform services
    print("\n📋 Test 4: Platform Services")
    try:
        response = requests.get(f"{BASE_URL}/workflow/platform-services/")
        if response.status_code == 200:
            data = response.json()
            services = data.get('results', data) if isinstance(data, dict) else data
            print(f"✅ Platform services: {len(services) if isinstance(services, list) else 'N/A'}")
            
            if isinstance(services, list):
                for service in services[:5]:
                    print(f"   - ID: {service.get('id')}: {service}")
        else:
            print(f"❌ Platform services failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_workflow_viewset_filtering():
    """Check if workflow ViewSet has incorrect filtering logic"""
    print("\n🔧 Checking Workflow ViewSet Filtering Logic...")
    
    # Let's check the actual workflow views.py to see if there's folder filtering
    script = '''
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
print("\\nChecking SourceFolders:")
folders = SourceFolder.objects.filter(project_id=3)
for folder in folders:
    print(f"  - Folder: {folder.name} (Type: {folder.folder_type})")

# Check PlatformServices
platform_services = PlatformService.objects.all()
print(f"\\nPlatformServices count: {platform_services.count()}")
for ps in platform_services:
    print(f"  - ID {ps.id}: {ps}")

print("\\nChecking if InputCollection is project-filtered correctly...")
project_3_collections = InputCollection.objects.filter(project_id=3)
print(f"Project 3 InputCollections: {project_3_collections.count()}")

print("Debug complete!")
'''
    
    # Write and execute the script
    with open("debug_workflow_filtering.py", "w", encoding="utf-8") as f:
        f.write(script)
    
    print("📤 Copying debug script to production...")
    subprocess.run(
        'upsun ssh -p inhoolfrqniuu -e main --app trackfutura "cat > /tmp/debug_workflow_filtering.py" < debug_workflow_filtering.py',
        shell=True
    )
    
    print("🔍 Executing workflow filtering debug...")
    result = subprocess.run(
        'upsun ssh -p inhoolfrqniuu -e main --app trackfutura "cd /app/backend && python manage.py shell < /tmp/debug_workflow_filtering.py"',
        shell=True, capture_output=True, text=True
    )
    
    print(f"Exit Code: {result.returncode}")
    if result.stdout:
        print("Output:")
        print(result.stdout)
    if result.stderr:
        print("Stderr:")
        print(result.stderr)

def check_workflow_frontend_api_calls():
    """Check what API calls the frontend is making"""
    print("\n🌐 Testing Frontend Workflow API Calls...")
    
    # Simulate the exact API calls the frontend makes
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api"
    
    api_calls = [
        "/workflow/",
        "/workflow/input-collections/",
        "/workflow/available-platforms/",
        "/workflow/platform-services/",
        "/workflow/input-collections/?project=3",
        "/workflow/input-collections/?project=3&folder=Nike",  # This might be the issue
    ]
    
    for api_call in api_calls:
        print(f"\n🔗 Testing: {api_call}")
        try:
            response = requests.get(f"{BASE_URL}{api_call}", timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'results' in data:
                    print(f"   Results: {len(data['results'])}")
                elif isinstance(data, list):
                    print(f"   Items: {len(data)}")
                else:
                    print(f"   Data type: {type(data)}")
            else:
                print(f"   Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   Exception: {str(e)}")

def fix_workflow_viewset_if_needed():
    """Fix workflow ViewSet if it has incorrect folder filtering"""
    print("\n🛠️ Checking and Fixing Workflow ViewSet...")
    
    script = '''
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
print("\\nChecking for potential folder filtering issues...")

# Check if InputCollection model has any folder relationships
from django.db import models
input_collection_fields = [field.name for field in InputCollection._meta.fields]
print(f"InputCollection model fields: {input_collection_fields}")

# Check if there are any related folder fields
folder_related_fields = [field for field in input_collection_fields if 'folder' in field.lower()]
print(f"Folder-related fields: {folder_related_fields}")

print("Fix analysis complete!")
'''
    
    # Write and execute the script
    with open("fix_workflow_viewset.py", "w", encoding="utf-8") as f:
        f.write(script)
    
    print("📤 Copying fix script to production...")
    subprocess.run(
        'upsun ssh -p inhoolfrqniuu -e main --app trackfutura "cat > /tmp/fix_workflow_viewset.py" < fix_workflow_viewset.py',
        shell=True
    )
    
    print("🔧 Executing workflow ViewSet fix...")
    result = subprocess.run(
        'upsun ssh -p inhoolfrqniuu -e main --app trackfutura "cd /app/backend && python manage.py shell < /tmp/fix_workflow_viewset.py"',
        shell=True, capture_output=True, text=True
    )
    
    print(f"Exit Code: {result.returncode}")
    if result.stdout:
        print("Output:")
        print(result.stdout)
    if result.stderr:
        print("Stderr:")
        print(result.stderr)

def main():
    print("=" * 70)
    print("🎯 INPUT COLLECTION FOLDER ISSUE FIX")
    print("🎯 Investigating why BrightData can't read Nike folder InputCollection")
    print("=" * 70)
    
    # Step 1: Check API responses
    check_input_collection_folder_issue()
    
    # Step 2: Check workflow filtering logic
    check_workflow_viewset_filtering()
    
    # Step 3: Test frontend API calls
    check_workflow_frontend_api_calls()
    
    # Step 4: Fix if needed
    fix_workflow_viewset_if_needed()
    
    print("\n" + "=" * 70)
    print("🎯 DIAGNOSIS COMPLETE")
    print("📋 Check the output above to identify the folder filtering issue")
    print("💡 The problem is likely in the workflow ViewSet filtering logic")
    print("=" * 70)

if __name__ == "__main__":
    main()