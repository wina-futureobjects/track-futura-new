#!/usr/bin/env python

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightdataConfig

configs = BrightdataConfig.objects.all()
print('All BrightData Configs:')
for config in configs:
    print(f'- ID: {config.id}, Platform: {config.platform}, Name: {config.name}, Active: {config.is_active}')

# Look for Instagram configs specifically
instagram_configs = configs.filter(platform__icontains='instagram')
print(f'\nInstagram configs: {instagram_configs.count()}')
for config in instagram_configs:
    print(f'- {config.platform}: {config.name} (Active: {config.is_active})')

# Show what platforms exist
platforms = configs.values_list('platform', flat=True).distinct()
print(f'\nAvailable platforms: {list(platforms)}')
