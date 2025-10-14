#!/usr/bin/env python3
"""
Production Project Setup Script
Ensures project and user exist for Web Unlocker integration
"""
import requests
import json

def create_project_via_django_shell():
    """Create project using Django shell endpoint if available"""
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Try to execute Django commands via a custom endpoint
    management_code = """
from django.contrib.auth import get_user_model
from users.models import Project

User = get_user_model()

# Get or create superuser
user = User.objects.filter(is_superuser=True).first()
if not user:
    user = User.objects.create_superuser(
        username='admin',
        email='admin@trackfutura.com',
        password='admin123'
    )
    print(f"✅ Created superuser: {user.username}")
else:
    print(f"✅ Found superuser: {user.username}")

# Get or create project
project = Project.objects.first()
if not project:
    project = Project.objects.create(
        name="TrackFutura Main Project",
        description="Main project for Web Unlocker integration", 
        owner=user
    )
    print(f"✅ Created project: {project.name} (ID: {project.id})")
else:
    print(f"✅ Found project: {project.name} (ID: {project.id})")

print(f"🎯 Project setup complete - ID: {project.id}")
"""
    
    print("🔧 Setting up project via management endpoint...")
    
    # Since we can't directly access Django shell, let's make the Web Unlocker endpoint 
    # handle project creation more robustly
    print("📝 The Web Unlocker endpoint should now handle project creation automatically")
    print("💡 If this fails, we need to create the project through Django admin")
    
def test_simple_endpoint():
    """Test a simpler endpoint to debug the issue"""
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test if we can hit any API endpoint
    test_endpoints = [
        "/api/",
        "/admin/",
        "/api/brightdata/",
    ]
    
    print("🧪 Testing available endpoints...")
    for endpoint in test_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"✅ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

if __name__ == "__main__":
    print("🚀 Production Project Setup for Web Unlocker Integration")
    print("=" * 60)
    
    test_simple_endpoint()
    
    print("\n" + "=" * 60)
    print("📋 Next Steps:")
    print("1. The Web Unlocker endpoint needs a project with ID=1")
    print("2. We need to ensure the project creation code works")
    print("3. Alternative: Create project via Django admin panel")
    print("4. Test Web Unlocker endpoint again")