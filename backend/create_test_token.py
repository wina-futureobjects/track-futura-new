import os
import sys
import django

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User
from rest_framework.authtoken.models import Token

# Get admin user
admin = User.objects.get(username='admin')

# Delete old token if exists
Token.objects.filter(user=admin).delete()

# Create new token
token = Token.objects.create(user=admin)

print("="*60)
print("🔑 Authentication Token Created")
print("="*60)
print(f"Username: admin")
print(f"Token: {token.key}")
print("="*60)
print("\n📝 You can use this token to manually authenticate:")
print(f"   Authorization: Token {token.key}")
print("\nOr try logging in with:")
print("   Username: admin")
print("   Password: admin123")
