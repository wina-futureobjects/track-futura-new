#!/usr/bin/env python
"""
PRODUCTION DATABASE STATUS CHECK - URGENT
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import Platform, Service, PlatformService
from brightdata_integration.models import BrightDataConfig

print("=== PRODUCTION DATABASE STATUS ===")
print(f"Platforms: {Platform.objects.count()}")
print(f"Services: {Service.objects.count()}")  
print(f"Platform Services: {PlatformService.objects.count()}")
print(f"BrightData Configs: {BrightDataConfig.objects.count()}")

print("\n=== CRITICAL CHECK: Instagram+Posts ===")
instagram_posts = PlatformService.objects.filter(
    platform__name='instagram', 
    service__name='posts', 
    is_enabled=True
)
print(f"Instagram+Posts count: {instagram_posts.count()}")

if instagram_posts.exists():
    print("✅ FOUND Instagram+Posts platform service!")
    for ps in instagram_posts:
        print(f"  - ID: {ps.id}, Platform: {ps.platform.name}, Service: {ps.service.name}")
else:
    print("❌ NO Instagram+Posts platform service found!")
    print("Available platforms:")
    for p in Platform.objects.all():
        print(f"  - {p.name}: {p.display_name}")
    print("Available services:")
    for s in Service.objects.all():
        print(f"  - {s.name}: {s.display_name}")

print("\n=== BrightData Configs ===")
configs = BrightDataConfig.objects.filter(is_active=True)
print(f"Active configs: {configs.count()}")
for config in configs:
    print(f"  - {config.platform}: {config.dataset_id} (API token: {config.api_token[:10]}...)")

print("\n=== RESTORATION STATUS ===")
if instagram_posts.exists() and configs.exists():
    print("🎉 PRODUCTION DATABASE IS READY!")
else:
    print("💥 PRODUCTION DATABASE NEEDS RESTORATION!")