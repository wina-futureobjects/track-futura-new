#!/usr/bin/env python3
"""
Create test user and fix authentication for BrightData testing
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import Organization, Project, GlobalRole

def create_test_environment():
    print("=== CREATING TEST AUTHENTICATION ENVIRONMENT ===")
    print()
    
    # 1. Create test user
    username = 'test'
    password = 'test123'
    email = 'test@trackfutura.com'
    
    try:
        user = User.objects.get(username=username)
        print(f"✅ Test user already exists: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name='Test',
            last_name='User'
        )
        print(f"✅ Created test user: {username}")
    
    # 2. Create test organization
    try:
        org = Organization.objects.get(name='Test Organization')
        print(f"✅ Test organization already exists: {org.name}")
    except Organization.DoesNotExist:
        org = Organization.objects.create(
            name='Test Organization',
            description='Test organization for BrightData testing',
            created_by=user
        )
        print(f"✅ Created test organization: {org.name}")
    
    # 3. Create test project
    try:
        project = Project.objects.get(name='Nike Singapore', organization=org)
        print(f"✅ Test project already exists: {project.name}")
    except Project.DoesNotExist:
        project = Project.objects.create(
            name='Nike Singapore',
            description='Test project for Nike BrightData scraping',
            organization=org,
            created_by=user
        )
        print(f"✅ Created test project: {project.name}")
    
    # 4. Set user role
    try:
        global_role = GlobalRole.objects.get(user=user)
        print(f"✅ User role already exists: {global_role.role}")
    except GlobalRole.DoesNotExist:
        global_role = GlobalRole.objects.create(
            user=user,
            role='super_admin'
        )
        print(f"✅ Created user role: {global_role.role}")
    
    # 5. Test authentication token generation
    from rest_framework.authtoken.models import Token
    token, created = Token.objects.get_or_create(user=user)
    
    print()
    print("=== AUTHENTICATION DETAILS ===")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")
    print(f"Auth Token: {token.key}")
    print(f"User ID: {user.id}")
    print(f"Organization ID: {org.id}")
    print(f"Project ID: {project.id}")
    print()
    print("=== FRONTEND LOGIN INSTRUCTIONS ===")
    print("1. Go to your frontend application")
    print("2. Open browser developer tools (F12)")
    print("3. Go to Console tab")
    print("4. Run this command:")
    print(f'   localStorage.setItem("authToken", "{token.key}");')
    print("5. Refresh the page")
    print()
    print("Alternatively, use the login API:")
    print(f"POST /api/users/login/")
    print(f"Body: {{\"username\": \"{username}\", \"password\": \"{password}\"}}")
    
    return {
        'user': user,
        'token': token.key,
        'organization': org,
        'project': project
    }

if __name__ == "__main__":
    result = create_test_environment()
    print("\n🎉 Test environment ready for BrightData testing!")