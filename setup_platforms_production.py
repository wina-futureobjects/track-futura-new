
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import Platform, Service, PlatformService

print("Creating platforms and services...")

# Create Instagram platform
instagram, created = Platform.objects.get_or_create(
    name='instagram',
    defaults={
        'display_name': 'Instagram',
        'description': 'Instagram social media platform',
        'is_enabled': True
    }
)
print(f"Instagram platform: {'created' if created else 'exists'} - ID {instagram.id}")

# Create Facebook platform
facebook, created = Platform.objects.get_or_create(
    name='facebook',
    defaults={
        'display_name': 'Facebook',
        'description': 'Facebook social media platform',
        'is_enabled': True
    }
)
print(f"Facebook platform: {'created' if created else 'exists'} - ID {facebook.id}")

# Create Posts service
posts, created = Service.objects.get_or_create(
    name='posts',
    defaults={
        'display_name': 'Posts Scraping',
        'description': 'Scrape posts from social media',
        'is_enabled': True
    }
)
print(f"Posts service: {'created' if created else 'exists'} - ID {posts.id}")

# Create Instagram + Posts platform service
ig_posts, created = PlatformService.objects.get_or_create(
    platform=instagram,
    service=posts,
    defaults={
        'description': 'Instagram posts scraping service',
        'is_enabled': True
    }
)
print(f"Instagram-Posts service: {'created' if created else 'exists'} - ID {ig_posts.id}")

# Create Facebook + Posts platform service
fb_posts, created = PlatformService.objects.get_or_create(
    platform=facebook,
    service=posts,
    defaults={
        'description': 'Facebook posts scraping service',
        'is_enabled': True
    }
)
print(f"Facebook-Posts service: {'created' if created else 'exists'} - ID {fb_posts.id}")

print("✅ Platform setup complete!")
print(f"Platform count: {Platform.objects.count()}")
print(f"Service count: {Service.objects.count()}")
print(f"PlatformService count: {PlatformService.objects.count()}")
