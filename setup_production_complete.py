#!/usr/bin/env python3
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from brightdata_integration.models import BrightDataConfig

# Create user
user, created = User.objects.get_or_create(
    username="winam", 
    defaults={
        "email": "wina@futureobjects.io", 
        "first_name": "Wina", 
        "last_name": "Munada"
    }
)
user.set_password("Sniped@10")
user.save()
print(f"User created/updated: {user.username}")

# Check BrightData configs
configs = BrightDataConfig.objects.all()
print(f"\nBrightData Configurations: {configs.count()}")
for config in configs:
    print(f"- Username: {config.username}")
    print(f"- Zone: {config.zone}")
    print(f"- Host: {config.host}:{config.port}")
    print(f"- Enabled: {config.is_enabled}")
    print(f"- API Token: {config.api_token[:20]}...")
    print()

# If no configs, create one
if configs.count() == 0:
    print("Creating BrightData configuration...")
    config = BrightDataConfig.objects.create(
        username="brd-customer-hl_5c16b0ec-zone-web_unlocker1",
        password="oj8awtxrb9pk",
        zone="web_unlocker1",
        host="brd-customer-hl_5c16b0ec-zone-web_unlocker1.brd.superproxy.io",
        port=22225,
        api_token="a4a3e1f6-2d4a-4e89-b1ff-87f6dbf3bb25",
        is_enabled=True
    )
    print(f"Created BrightData config: {config.username}")
else:
    print("BrightData configuration already exists")