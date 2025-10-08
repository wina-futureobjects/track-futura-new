from brightdata_integration.models import BrightDataConfig
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Create Instagram configuration
config1, created1 = BrightDataConfig.objects.get_or_create(
    platform='instagram',
    defaults={
        'name': 'Instagram Posts Scraper',
        'dataset_id': 'gd_lk5ns7kz21pck8jpis',
        'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb',
        'is_active': True
    }
)

# Create Facebook configuration
config2, created2 = BrightDataConfig.objects.get_or_create(
    platform='facebook',
    defaults={
        'name': 'Facebook Posts Scraper',
        'dataset_id': 'gd_lkaxegm826bjpoo9m5',
        'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb',
        'is_active': True
    }
)

# Create test user
user, created3 = User.objects.get_or_create(
    username='test',
    defaults={
        'email': 'test@trackfutura.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
)

user.set_password('test123')
user.save()

# Create auth token
token, created4 = Token.objects.get_or_create(user=user)

print(f'Instagram: {"Created" if created1 else "Updated"} (ID: {config1.id})')
print(f'Facebook: {"Created" if created2 else "Updated"} (ID: {config2.id})')
print(f'User: {"Created" if created3 else "Updated"} ({user.username})')
print(f'Token: {token.key}')
print(f'Total configs: {BrightDataConfig.objects.count()}')
print('Setup complete!')