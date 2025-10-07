import os
import sys
import django

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

# Reset admin password to simple one for testing
try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.save()
    print("✅ Admin password reset to: admin123")
    print(f"   Username: admin")
    print(f"   Password: admin123")
    print(f"   Email: {admin.email}")
except User.DoesNotExist:
    print("❌ Admin user not found")

print("\n" + "="*60)
print("🔐 Login Credentials for Testing:")
print("="*60)
print("Username: admin")
print("Password: admin123")
print("="*60)
print("\n📝 Login URL: http://localhost:5175/login")
