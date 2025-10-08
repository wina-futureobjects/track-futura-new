#!/usr/bin/env python3
"""
FINAL SIMPLE FIX 
Create InputCollection with correct model imports
"""

import subprocess

def create_final_input_collection():
    """Create InputCollection with correct imports"""
    
    django_commands = """
# Use correct model imports
from workflow.models import InputCollection, PlatformService
from track_accounts.models import TrackSource

# Get Nike source
nike_source = TrackSource.objects.filter(name__icontains='nike').first()
print(f"Nike source: {nike_source}")

# Check existing platform services
platform_services = PlatformService.objects.all()
print(f"PlatformServices count: {platform_services.count()}")

for ps in platform_services:
    print(f"  - PlatformService ID {ps.id}: {ps}")

if platform_services.exists():
    # Use the first platform service
    ps = platform_services.first()
    print(f"Using PlatformService: {ps}")
    
    # Create InputCollection
    ic = InputCollection.objects.create(
        project_id=3,
        platform_service=ps,
        urls=['https://www.instagram.com/nike'],
        status='active'
    )
    print(f"SUCCESS! Created InputCollection ID: {ic.id}")
    
    # Verify
    total = InputCollection.objects.count()
    print(f"Total InputCollections now: {total}")
    
    # Show all collections
    for collection in InputCollection.objects.all():
        print(f"  - Collection ID {collection.id}, Project {collection.project_id}, Status: {collection.status}")
        
else:
    print("ERROR: No PlatformServices found")
"""
    
    # Write script
    with open("final_fix.py", "w", encoding="utf-8") as f:
        f.write(django_commands)
    
    # Execute
    print("Copying final script...")
    subprocess.run('upsun ssh -p inhoolfrqniuu -e main --app trackfutura "cat > /tmp/final_fix.py" < final_fix.py', shell=True)
    
    print("Executing final script...")
    result = subprocess.run(
        'upsun ssh -p inhoolfrqniuu -e main --app trackfutura "cd /app/backend && python manage.py shell < /tmp/final_fix.py"',
        shell=True, capture_output=True, text=True
    )
    
    print(f"Exit Code: {result.returncode}")
    if result.stdout:
        print("Output:")
        print(result.stdout)
    if result.stderr:
        print("Stderr:")
        print(result.stderr)
    
    return result.returncode == 0

def final_verification():
    """Final check via API"""
    import requests
    import time
    
    print("\nWaiting 3 seconds for database propagation...")
    time.sleep(3)
    
    try:
        response = requests.get(
            "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/workflow/input-collections/"
        )
        
        print(f"API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            collections = data.get('results', data)
            
            print(f"Collections found: {len(collections)}")
            
            if collections:
                print("SUCCESS! Collections available:")
                for c in collections:
                    print(f"  - ID: {c.get('id')}")
                    print(f"    Project: {c.get('project')}")
                    print(f"    Platform Service: {c.get('platform_service')}")
                    print(f"    URLs: {c.get('urls')}")
                    print(f"    Status: {c.get('status')}")
                
                print("\n" + "=" * 60)
                print("🎉 WORKFLOW FIX COMPLETE! 🎉")
                print("=" * 60)
                print("🔗 URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/2/projects/3/workflow-management")
                print("🔄 Refresh the page")
                print("✅ You should now see input collections available")
                print("🚀 You can now create scraping runs!")
                print("🎯 CLIENT TESTING IS NOW POSSIBLE!")
                print("=" * 60)
                return True
            else:
                print("No collections found")
                return False
        else:
            print(f"API Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"API verification failed: {e}")
        return False

def main():
    print("FINAL SIMPLE FIX - Creating InputCollection with correct models")
    print("=" * 60)
    
    success = create_final_input_collection()
    
    if success:
        final_verification()
    else:
        print("Final fix failed")

if __name__ == "__main__":
    main()