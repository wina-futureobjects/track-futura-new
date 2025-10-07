#!/usr/bin/env python3

# Simple script to create an admin user for production
from django.contrib.auth.models import User

try:
    # Try to get existing admin user
    user = User.objects.get(username='admin')
    print(f"Admin user already exists: {user.username}")
except User.DoesNotExist:
    # Create new admin user
    user = User.objects.create_user(
        username='admin',
        email='admin@trackfutura.com',
        password='admin123'
    )
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"Created new admin user: {user.username}")

# Set/reset password
user.set_password('admin123')
user.save()
print(f"Password set for user: {user.username}")

# Create a test user too
try:
    test_user = User.objects.get(username='testuser')
    print(f"Test user already exists: {test_user.username}")
except User.DoesNotExist:
    test_user = User.objects.create_user(
        username='testuser',
        email='test@trackfutura.com',
        password='test123'
    )
    print(f"Created test user: {test_user.username}")

test_user.set_password('test123')
test_user.save()
print(f"Password set for test user: {test_user.username}")

print(f"Total users in database: {User.objects.count()}")