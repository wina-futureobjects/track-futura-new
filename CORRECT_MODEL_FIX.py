#!/usr/bin/env python3
"""
CORRECT MODEL FIX
Check what models exist and create InputCollection properly
"""

import subprocess

def create_input_collection_correct():
    """Create InputCollection with correct model imports"""
    
    django_commands = """
# First, let's see what models are available
print("=== Checking available models ===")

try:
    from workflow.models import InputCollection
    print("✅ InputCollection model exists")
except ImportError as e:
    print(f"❌ InputCollection import error: {e}")

try:
    from brightdata_integration.models import Platform, Service, PlatformService
    print("✅ BrightData models exist")
except ImportError as e:
    print(f"❌ BrightData models import error: {e}")
    try:
        from workflow.models import Platform, Service, PlatformService
        print("✅ Workflow Platform models exist")
    except ImportError as e2:
        print(f"❌ Workflow Platform models error: {e2}")

try:
    from track_accounts.models import TrackSource
    print("✅ TrackSource model exists")
except ImportError as e:
    print(f"❌ TrackSource import error: {e}")

# Check what's actually in workflow.models
import workflow.models
print(f"Workflow models: {dir(workflow.models)}")

# Try to find the Nike source
from track_accounts.models import TrackSource
nike_sources = TrackSource.objects.filter(name__icontains='nike')
print(f"Nike sources found: {nike_sources.count()}")
for source in nike_sources:
    print(f"  - {source.name} (ID: {source.id})")

# Check existing InputCollections
try:
    from workflow.models import InputCollection
    existing = InputCollection.objects.all()
    print(f"Existing InputCollections: {existing.count()}")
    for ic in existing:
        print(f"  - {ic.name}")
except Exception as e:
    print(f"Error checking InputCollections: {e}")

# Let's try to create a minimal InputCollection
if nike_sources.exists():
    nike_source = nike_sources.first()
    
    # Try different approaches to create InputCollection
    try:
        # Approach 1: Minimal required fields
        ic = InputCollection(
            name='Nike Instagram Collection',
            description='Nike Instagram for workflow',
            project_id=3,
            is_active=True
        )
        
        # Check what fields are required
        print(f"InputCollection fields: {[f.name for f in InputCollection._meta.fields]}")
        
        # Try to save
        ic.save()
        print(f"✅ InputCollection created: {ic.id}")
        
    except Exception as e:
        print(f"❌ Error creating InputCollection: {e}")
        
        # Try with different field combinations
        try:
            # Check what platform_service options exist
            from brightdata_integration.models import PlatformService
            platform_services = PlatformService.objects.all()
            print(f"Available PlatformServices: {platform_services.count()}")
            for ps in platform_services:
                print(f"  - {ps}")
                
            if platform_services.exists():
                ic = InputCollection(
                    name='Nike Instagram Collection',
                    description='Nike Instagram for workflow',
                    project_id=3,
                    platform_service=platform_services.first(),
                    is_active=True
                )
                ic.save()
                print(f"✅ InputCollection created with PlatformService: {ic.id}")
                
        except Exception as e2:
            print(f"❌ Second attempt failed: {e2}")
"""
    
    # Write the commands to a file
    with open("check_models.py", "w") as f:
        f.write(django_commands)
    
    # Execute via Upsun CLI
    copy_command = 'upsun ssh -p inhoolfrqniuu -e main --app trackfutura "cat > /tmp/check_models.py" < check_models.py'
    exec_command = 'upsun ssh -p inhoolfrqniuu -e main --app trackfutura "cd /app/backend && python manage.py shell < /tmp/check_models.py"'
    
    print("📤 Copying model check script...")
    subprocess.run(copy_command, shell=True)
    
    print("🔍 Checking models and creating InputCollection...")
    result = subprocess.run(exec_command, shell=True, capture_output=True, text=True)
    
    print(f"Exit Code: {result.returncode}")
    if result.stdout:
        print("Output:")
        print(result.stdout)
    if result.stderr:
        print("Stderr:")
        print(result.stderr)
    
    return result.returncode == 0

def verify_final_result():
    """Final verification"""
    print("\n🧪 Final Verification...")
    
    import requests
    try:
        response = requests.get(
            "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/workflow/input-collections/",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                collections = data['results']
            else:
                collections = data
                
            print(f"✅ Final check: {len(collections)} input collections")
            
            if collections:
                for collection in collections:
                    print(f"   - {collection.get('name')} (ID: {collection.get('id')})")
                print("\n🎉 SUCCESS! Workflow should now work!")
                return True
        
        print("❌ Still no InputCollections found")
        return False
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🎯 CORRECT MODEL FIX")
    print("🎯 Finding correct models and creating InputCollection")
    print("=" * 60)
    
    success = create_input_collection_correct()
    
    if success:
        verify_final_result()
    else:
        print("❌ Model fix failed")

if __name__ == "__main__":
    main()