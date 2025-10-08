#!/usr/bin/env python3
"""
DIRECT DATABASE FIX
Using Upsun CLI to execute commands directly on production
"""

import subprocess
import time

def run_upsun_command(command, description):
    """Run a command via Upsun CLI"""
    print(f"🚀 {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        
        print(f"   Exit Code: {result.returncode}")
        
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        
        if result.stderr:
            print(f"   Stderr: {result.stderr.strip()}")
            
        return result.returncode == 0, result.stdout, result.stderr
    
    except subprocess.TimeoutExpired:
        print("   ❌ Command timed out")
        return False, "", "Timeout"
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False, "", str(e)

def create_input_collection_via_cli():
    """Create InputCollection via Django shell on production"""
    print("=" * 60)
    print("🎯 DIRECT DATABASE FIX")
    print("🎯 Creating InputCollection via Django Shell")
    print("=" * 60)
    
    # Django shell command to create InputCollection
    django_commands = """
from workflow.models import InputCollection, Platform, Service, PlatformService
from track_accounts.models import TrackSource

# Get Nike IG track source
nike_source = TrackSource.objects.filter(name__icontains='nike').first()
print(f"Found Nike source: {nike_source}")

# Get or create platform and service
platform, created = Platform.objects.get_or_create(
    name='Instagram',
    defaults={'description': 'Instagram platform'}
)
print(f"Platform: {platform} (created: {created})")

service, created = Service.objects.get_or_create(
    name='Posts',
    defaults={'description': 'Posts scraping service'}
)
print(f"Service: {service} (created: {created})")

platform_service, created = PlatformService.objects.get_or_create(
    platform=platform,
    service=service,
    defaults={'is_active': True}
)
print(f"PlatformService: {platform_service} (created: {created})")

# Create InputCollection
input_collection, created = InputCollection.objects.get_or_create(
    name='Nike Instagram Collection',
    defaults={
        'description': 'Nike Instagram for BrightData workflow',
        'project_id': 3,
        'platform_service': platform_service,
        'is_active': True,
        'metadata': {
            'track_source_id': nike_source.id if nike_source else None,
            'instagram_url': 'https://www.instagram.com/nike',
            'brightdata_ready': True
        }
    }
)

print(f"InputCollection created: {input_collection} (created: {created})")
print(f"InputCollection ID: {input_collection.id}")

# Verify
total_collections = InputCollection.objects.count()
print(f"Total InputCollections: {total_collections}")

# List all collections
for collection in InputCollection.objects.all():
    print(f"  - {collection.name} (ID: {collection.id}, Active: {collection.is_active})")
"""
    
    # Write the commands to a temporary file
    with open("create_input_collection.py", "w") as f:
        f.write(django_commands)
    
    # Execute via Upsun CLI
    upsun_command = 'upsun ssh -p inhoolfrqniuu -e main --app trackfutura "cd /app/backend && python manage.py shell < /tmp/create_input_collection.py"'
    
    # First, copy the script to the server
    copy_command = 'upsun ssh -p inhoolfrqniuu -e main --app trackfutura "cat > /tmp/create_input_collection.py" < create_input_collection.py'
    
    print("📤 Copying script to server...")
    success, stdout, stderr = run_upsun_command(copy_command, "Copy script to production")
    
    if not success:
        print("❌ Failed to copy script")
        return False
    
    print("🐍 Executing Django shell commands...")
    success, stdout, stderr = run_upsun_command(upsun_command, "Execute Django shell commands")
    
    if success:
        print("✅ Commands executed successfully!")
        return True
    else:
        print("❌ Commands failed")
        return False

def verify_workflow_via_api():
    """Verify the fix worked by checking the API"""
    print("\n🧪 Verifying Fix via API...")
    
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
                
            print(f"✅ API Response: {len(collections)} input collections found")
            
            if collections:
                for collection in collections:
                    print(f"   - {collection.get('name')} (ID: {collection.get('id')})")
                    print(f"     Project: {collection.get('project')}")
                    print(f"     Active: {collection.get('is_active')}")
                return True
            else:
                print("❌ No collections found")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API Request failed: {str(e)}")
        return False

def main():
    success = create_input_collection_via_cli()
    
    if success:
        time.sleep(2)  # Wait for database to propagate
        
        if verify_workflow_via_api():
            print("\n" + "=" * 60)
            print("🎉 SUCCESS! WORKFLOW FIX COMPLETE!")
            print("=" * 60)
            print("🔗 Go to: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/2/projects/3/workflow-management")
            print("🔄 Refresh the page")
            print("✅ You should now see 'Nike Instagram Collection' available")
            print("🚀 You can now create scraping runs for CLIENT TESTING!")
            print("=" * 60)
        else:
            print("\n❌ Verification failed - check manually")
    else:
        print("\n❌ Direct fix failed")
        print("💡 Recommendation: Check Upsun deployment status and try the management command approach")

if __name__ == "__main__":
    main()