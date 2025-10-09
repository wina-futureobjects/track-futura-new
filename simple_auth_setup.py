from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Create admin user
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@trackfutura.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'is_active': True,
        'is_staff': True,
        'is_superuser': True
    }
)

if created:
    admin.set_password('TrackAdmin2025!')
    admin.save()

admin_token, created = Token.objects.get_or_create(user=admin)
print(f"Admin token: {admin_token.key}")

# Create test user  
test_user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@trackfutura.com',
        'first_name': 'Test', 
        'last_name': 'User',
        'is_active': True,
        'is_staff': True,
        'is_superuser': False
    }
)

test_token, created = Token.objects.get_or_create(user=test_user)
print(f"Test token: {test_token.key}")

print("Authentication setup complete!")