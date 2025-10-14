#!/usr/bin/env python3
"""
Fix Production Project Issue
Create project with ID 1 or fix the Web Unlocker to use existing project
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

def fix_production_project():
    """Fix the production project issue"""
    
    print("🔧 Fixing Production Project Issue")
    print("=" * 50)
    
    # Check current state
    users = User.objects.all()
    projects = Project.objects.all()
    
    print(f"📊 Current Database State:")
    print(f"   Total Users: {users.count()}")
    print(f"   Total Projects: {projects.count()}")
    
    if users.exists():
        print(f"   First User: {users.first().username} (ID: {users.first().id})")
    
    if projects.exists():
        print(f"   First Project: {projects.first().name} (ID: {projects.first().id})")
    
    # Get or create superuser
    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        print("\n👤 Creating superuser...")
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@trackfutura.com',
            password='TrackFutura2024!'
        )
        print(f"✅ Created: {superuser.username} (ID: {superuser.id})")
    else:
        print(f"\n✅ Using superuser: {superuser.username} (ID: {superuser.id})")
    
    # Check if project with ID 1 exists
    project_1 = Project.objects.filter(id=1).first()
    
    if not project_1:
        print(f"\n🏗️ Creating project with ID 1...")
        
        # Create project with specific ID
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users_project (id, name, description, owner_id, is_public, created_at, updated_at)
                VALUES (1, 'Web Unlocker Default Project', 'Default project for Web Unlocker integration', %s, FALSE, NOW(), NOW())
                ON CONFLICT (id) DO NOTHING
            """, [superuser.id])
            
            # Reset sequence to avoid conflicts
            cursor.execute("SELECT setval('users_project_id_seq', (SELECT MAX(id) FROM users_project))")
        
        project_1 = Project.objects.get(id=1)
        print(f"✅ Created project with ID 1: {project_1.name}")
    else:
        print(f"\n✅ Project ID 1 exists: {project_1.name}")
    
    # Verify the fix
    print(f"\n🎯 Final State:")
    print(f"   Project ID 1: {Project.objects.filter(id=1).exists()}")
    print(f"   Superuser: {superuser.username} (ID: {superuser.id})")
    print(f"   Project: {project_1.name} (ID: {project_1.id})")
    
    return project_1

if __name__ == "__main__":
    try:
        project = fix_production_project()
        print(f"\n🎉 SUCCESS: Project ID 1 is ready for Web Unlocker!")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()