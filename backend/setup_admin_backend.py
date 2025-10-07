#!/usr/bin/env python
import os
import sys
import django

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now import Django models
from django.contrib.auth.models import User
from users.models import UserProfile, UserRole

def setup_admin():
    print("Setting up superadmin user...")
    
    # Get or create superadmin user
    admin_user, created = User.objects.get_or_create(
        username='superadmin',
        defaults={
            'email': 'superadmin@trackfutura.com',
            'is_staff': True,
            'is_superuser': True
        }
    )

    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f'Created superadmin user: {admin_user.username}')
    else:
        print(f'Superadmin user already exists: {admin_user.username}')

    # Get or create super_admin role
    user_role, created = UserRole.objects.get_or_create(
        user=admin_user,
        defaults={
            'role': 'super_admin'
        }
    )

    if created:
        print(f'Created super_admin role for user: {user_role.role}')
    else:
        # Update existing role
        user_role.role = 'super_admin'
        user_role.save()
        print(f'Updated existing user role to: {user_role.role}')

    # Get or create admin profile
    profile, created = UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={}
    )

    if created:
        print(f'Created new profile for superadmin')
    else:
        print(f'Superadmin profile already exists')

    print(f'Final superadmin user role: {user_role.role}')
    return admin_user, user_role

if __name__ == '__main__':
    admin_user, user_role = setup_admin()
    print("Setup completed successfully!")