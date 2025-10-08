#!/bin/bash

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
