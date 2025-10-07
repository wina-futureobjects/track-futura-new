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

# Set/reset password and make sure it's superuser
user.set_password('admin123')
user.is_staff = True
user.is_superuser = True
user.save()
print(f"Password set for user: {user.username}, is_superuser: {user.is_superuser}")

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

# Now let's assign proper roles using the UserProfile model
try:
    from users.models import UserProfile, UserRole
    
    # Create or update admin user profile with super_admin role
    admin_profile, created = UserProfile.objects.get_or_create(user=user)
    super_admin_role, role_created = UserRole.objects.get_or_create(
        role='super_admin',
        defaults={'role_display': 'Super Administrator'}
    )
    admin_profile.global_role = super_admin_role
    admin_profile.save()
    print(f"Admin user role set to: {super_admin_role.role}")
    
    # Create or update test user profile with user role  
    test_profile, created = UserProfile.objects.get_or_create(user=test_user)
    user_role, role_created = UserRole.objects.get_or_create(
        role='user',
        defaults={'role_display': 'User'}
    )
    test_profile.global_role = user_role
    test_profile.save()
    print(f"Test user role set to: {user_role.role}")
    
except ImportError as e:
    print(f"Could not import user models: {e}")
    print("User roles not set - check if UserProfile and UserRole models exist")

print(f"Total users in database: {User.objects.count()}")