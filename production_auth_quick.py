#!/usr/bin/env python
"""
Quick production authentication setup via Django shell
"""
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from brightdata_integration.models import BrightDataConfig

# Create users with tokens
users_data = [
    ('admin', 'admin@trackfutura.com', True, True),
    ('testuser', 'test@trackfutura.com', True, False),
    ('demo', 'demo@trackfutura.com', False, False)
]

print("Setting up production authentication...")
tokens = {}

for username, email, is_staff, is_superuser in users_data:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'is_active': True,
            'is_staff': is_staff,
            'is_superuser': is_superuser
        }
    )
    
    if created:
        user.set_password(f'{username.title()}2025!')
        user.save()
    
    token, _ = Token.objects.get_or_create(user=user)
    tokens[username] = token.key
    print(f'{username}: {token.key}')

# Update BrightData configs
configs = [
    ('instagram', 'gd_lk5ns7kz21pck8jpis'),
    ('facebook', 'gd_lkaxegm826bjpoo9m5')
]

for platform, dataset_id in configs:
    config, created = BrightDataConfig.objects.get_or_create(
        platform=platform,
        defaults={
            'name': f'{platform.title()} Posts Scraper',
            'dataset_id': dataset_id,
            'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb',
            'is_active': True
        }
    )
    if not created:
        config.api_token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
        config.is_active = True
        config.save()

print("Authentication setup complete!")
print("Use any of these tokens: Authorization: Token {token}")