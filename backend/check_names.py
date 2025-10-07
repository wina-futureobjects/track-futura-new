import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import TrackSource
from users.models import Platform, Service

# Check track source data
track_source = TrackSource.objects.get(id=1)
print(f'TrackSource platform: "{track_source.platform}"')
print(f'TrackSource service_name: "{track_source.service_name}"')

# Check platform names
platforms = Platform.objects.all()
for platform in platforms:
    print(f'Platform name: "{platform.name}"')

# Check service names
services = Service.objects.all()
for service in services:
    print(f'Service name: "{service.name}"')