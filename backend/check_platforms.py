#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import Platform, PlatformService

print('=== PLATFORMS ===')
platforms = Platform.objects.all()
for platform in platforms:
    print(f'Platform: name="{platform.name}", display_name="{platform.display_name}"')

print()
print('=== PLATFORM SERVICES ===')
platform_services = PlatformService.objects.all()
for ps in platform_services:
    print(f'PlatformService: platform="{ps.platform.name}" (display: "{ps.platform.display_name}"), service="{ps.service.name}"')