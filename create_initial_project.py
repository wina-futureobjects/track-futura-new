#!/usr/bin/env python3
"""
Create Initial Project Management Command
Creates the initial project and user structure for production
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import Project

def create_initial_project():
    """Create initial project and superuser for production"""
    
    print("🏗️ Creating Initial Project Structure")
    print("=" * 50)
    
    # Check current state
    print(f"📊 Current State:")
    print(f"   Users: {User.objects.count()}")
    print(f"   Projects: {Project.objects.count()}")
    
    # Create superuser if none exists
    if not User.objects.filter(is_superuser=True).exists():
        print("\n👤 Creating Superuser...")
        superuser = User.objects.create_superuser(
            username='superadmin',
            email='admin@trackfutura.com',
            password='TrackFutura2024!',
            first_name='Super',
            last_name='Admin'
        )
        print(f"✅ Created superuser: {superuser.username} (ID: {superuser.id})")
    else:
        superuser = User.objects.filter(is_superuser=True).first()
        print(f"✅ Using existing superuser: {superuser.username} (ID: {superuser.id})")
    
    # Create default project if none exists
    if not Project.objects.exists():
        print("\n📁 Creating Default Project...")
        project = Project.objects.create(
            name="TrackFutura Default Project",
            description="Default project for Web Unlocker and general scraping",
            created_by=superuser,
            is_active=True
        )
        print(f"✅ Created project: {project.name} (ID: {project.id})")
    else:
        project = Project.objects.first()
        print(f"✅ Using existing project: {project.name} (ID: {project.id})")
    
    print(f"\n🎯 Final State:")
    print(f"   Users: {User.objects.count()}")
    print(f"   Projects: {Project.objects.count()}")
    print(f"   Superuser: {superuser.username} (ID: {superuser.id})")
    print(f"   Default Project: {project.name} (ID: {project.id})")
    
    return project, superuser

if __name__ == "__main__":
    try:
        project, user = create_initial_project()
        print("\n🎉 SUCCESS: Initial project structure created!")
        print(f"🔗 Project ID {project.id} is now available for Web Unlocker")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()