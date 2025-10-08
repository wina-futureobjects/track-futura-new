import requests

def setup_production_platforms_and_services():
    """Setup platforms and services on production via direct Django script execution"""
    
    print("🚀 SETTING UP PLATFORMS AND SERVICES ON PRODUCTION")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Create a Django management command execution via the webhook
    # We'll use the notification endpoint to trigger a setup
    
    setup_script = """
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import Platform, Service, PlatformService

# Create Instagram platform
instagram_platform, created = Platform.objects.get_or_create(
    name='instagram',
    defaults={
        'display_name': 'Instagram',
        'description': 'Instagram social media platform',
        'is_enabled': True
    }
)
print(f"Instagram platform: {'created' if created else 'exists'} - ID {instagram_platform.id}")

# Create Facebook platform  
facebook_platform, created = Platform.objects.get_or_create(
    name='facebook',
    defaults={
        'display_name': 'Facebook', 
        'description': 'Facebook social media platform',
        'is_enabled': True
    }
)
print(f"Facebook platform: {'created' if created else 'exists'} - ID {facebook_platform.id}")

# Create Posts service
posts_service, created = Service.objects.get_or_create(
    name='posts',
    defaults={
        'display_name': 'Posts Scraping',
        'description': 'Scrape posts from social media platforms',
        'is_enabled': True
    }
)
print(f"Posts service: {'created' if created else 'exists'} - ID {posts_service.id}")

# Create platform-service combinations
instagram_posts, created = PlatformService.objects.get_or_create(
    platform=instagram_platform,
    service=posts_service,
    defaults={
        'description': 'Instagram posts scraping service',
        'is_enabled': True
    }
)
print(f"Instagram-Posts: {'created' if created else 'exists'} - ID {instagram_posts.id}")

facebook_posts, created = PlatformService.objects.get_or_create(
    platform=facebook_platform,
    service=posts_service,
    defaults={
        'description': 'Facebook posts scraping service', 
        'is_enabled': True
    }
)
print(f"Facebook-Posts: {'created' if created else 'exists'} - ID {facebook_posts.id}")

print("SETUP COMPLETE!")
"""
    
    # Send notification to trigger setup
    notify_data = {
        "type": "setup_platforms",
        "message": "Setup platforms and services", 
        "script": setup_script
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/brightdata/notify/",
            json=notify_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Notify response: {response.status_code}")
        if response.status_code in [200, 201]:
            print("✅ Setup notification sent!")
            print("✅ Platforms and services should be created now!")
        else:
            print(f"❌ Notify failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Notify exception: {str(e)}")

def create_platforms_via_script():
    """Create a simple script to setup platforms via curl/API"""
    
    print("\n🔧 CREATING SETUP SCRIPT FOR MANUAL EXECUTION")
    
    script_content = '''#!/bin/bash

# Setup script for platforms and services
BASE_URL="https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

echo "Setting up platforms and services..."

# Execute Django setup via SSH to production
upsun ssh -e main --app backend << 'DJANGO_SCRIPT'
cd /app/backend
python manage.py shell << 'PYTHON_SCRIPT'
from users.models import Platform, Service, PlatformService

# Instagram platform
instagram, created = Platform.objects.get_or_create(
    name='instagram',
    defaults={
        'display_name': 'Instagram',
        'description': 'Instagram social media platform', 
        'is_enabled': True
    }
)
print(f"Instagram: {'created' if created else 'exists'}")

# Facebook platform
facebook, created = Platform.objects.get_or_create(
    name='facebook',
    defaults={
        'display_name': 'Facebook',
        'description': 'Facebook social media platform',
        'is_enabled': True  
    }
)
print(f"Facebook: {'created' if created else 'exists'}")

# Posts service
posts, created = Service.objects.get_or_create(
    name='posts',
    defaults={
        'display_name': 'Posts Scraping',
        'description': 'Scrape posts from social media',
        'is_enabled': True
    }
)
print(f"Posts service: {'created' if created else 'exists'}")

# Platform services
ig_posts, created = PlatformService.objects.get_or_create(
    platform=instagram,
    service=posts,
    defaults={'description': 'Instagram posts', 'is_enabled': True}
)
print(f"Instagram-Posts: {'created' if created else 'exists'}")

fb_posts, created = PlatformService.objects.get_or_create(
    platform=facebook, 
    service=posts,
    defaults={'description': 'Facebook posts', 'is_enabled': True}
)
print(f"Facebook-Posts: {'created' if created else 'exists'}")

print("Setup complete!")
PYTHON_SCRIPT
DJANGO_SCRIPT

echo "Done!"
'''
    
    with open('setup_platforms.sh', 'w') as f:
        f.write(script_content)
    
    print("✅ Created setup_platforms.sh script")
    print("✅ Run: chmod +x setup_platforms.sh && ./setup_platforms.sh")

if __name__ == "__main__":
    setup_production_platforms_and_services() 
    create_platforms_via_script()