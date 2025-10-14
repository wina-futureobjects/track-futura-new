#!/usr/bin/env python3
"""
Simple password reset script - Run this locally then deploy
"""

# This will be executed on production to reset admin password
admin_reset_script = """
from django.contrib.auth.models import User
try:
    user = User.objects.get(username='superadmin')
    user.set_password('quickaccess123')
    user.save()
    print('SUCCESS: Password updated!')
    print('Login URL: https://trackfutura.futureobjects.io/admin/')
    print('Username: superadmin')
    print('Password: quickaccess123')
except Exception as e:
    print(f'Error: {e}')
"""

print("Copy this command and run it on your production server:")
print("=" * 60)
print(f'echo "{admin_reset_script}" | python manage.py shell')
print("=" * 60)
print("\nAfter running this, you can login to:")
print("🌐 https://trackfutura.futureobjects.io/admin/")
print("👤 Username: superadmin") 
print("🔑 Password: quickaccess123")
print("\n📍 Your BrightData JSON is at:")
print("🗂️ https://trackfutura.futureobjects.io/admin/brightdata_integration/brightdatawebhookevent/")