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
    print("Setting up admin user...")
    
    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@trackfutura.com',
            'is_staff': True,
            'is_superuser': True
        }
    )

    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f'Created admin user: {admin_user.username}')
    else:
        print(f'Admin user already exists: {admin_user.username}')

    # Get or create super_admin role
    super_admin_role, created = UserRole.objects.get_or_create(
        role_name='super_admin',
        defaults={
            'description': 'Super Administrator with full access'
        }
    )

    if created:
        print(f'Created super_admin role: {super_admin_role.role_name}')
    else:
        print(f'Super_admin role already exists: {super_admin_role.role_name}')

    # Get or create admin profile and assign role
    profile, created = UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={
            'global_role': super_admin_role
        }
    )

    if created:
        print(f'Created new profile for admin with super_admin role')
    else:
        # Update existing profile
        profile.global_role = super_admin_role
        profile.save()
        print(f'Updated existing admin profile with super_admin role')

    print(f'Final admin user role: {profile.global_role.role_name}')
    return admin_user, profile

if __name__ == '__main__':
    admin_user, profile = setup_admin()
    print("Setup completed successfully!")