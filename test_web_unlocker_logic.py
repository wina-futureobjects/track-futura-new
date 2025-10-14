#!/usr/bin/env python3
"""
Local Web Unlocker Test
Test the Web Unlocker logic locally to verify the fix works
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
from track_accounts.models import UnifiedRunFolder

def test_web_unlocker_logic():
    """Test the Web Unlocker project selection logic locally"""
    
    print("🧪 Testing Web Unlocker Logic Locally")
    print("=" * 50)
    
    # Check current database state
    users = User.objects.all()
    projects = Project.objects.all()
    
    print(f"📊 Database State:")
    print(f"   Users: {users.count()}")
    print(f"   Projects: {projects.count()}")
    
    # Test the project selection logic from Web Unlocker
    from django.db import transaction
    
    print("\n🔍 Testing Project Selection Logic:")
    
    with transaction.atomic():
        # This is the same logic as in Web Unlocker
        project = Project.objects.filter(id=1).first() or Project.objects.first()
        
        if not project:
            print("📋 No project found, would create default project...")
            
            # Get or create superuser
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                print("👤 Would create superuser...")
                user = User.objects.create_superuser(
                    username='webunlocker_admin_test',
                    email='webunlocker_test@trackfutura.com',
                    password='WebUnlocker2024!'
                )
                print(f"✅ Created test superuser: {user.username} (ID: {user.id})")
            else:
                print(f"✅ Using existing superuser: {user.username} (ID: {user.id})")
            
            print("🏗️ Would create Web Unlocker project...")
            project = Project.objects.create(
                name="Web Unlocker Test Project",
                description="Test project for BrightData Web Unlocker integration",
                owner=user,
                is_public=False
            )
            print(f"✅ Created test project: {project.name} (ID: {project.id})")
        else:
            print(f"✅ Found existing project: {project.name} (ID: {project.id})")
    
    # Test creating UnifiedRunFolder with this project
    print(f"\n🧪 Testing UnifiedRunFolder Creation:")
    
    try:
        folder = UnifiedRunFolder.objects.create(
            name=f"Test Web Unlocker Folder",
            folder_type='job',
            platform_code=None,
            service_code=None,
            project=project,  # Use the project object
            parent_folder=None,
            description=f"Test folder for Web Unlocker"
        )
        
        print(f"✅ Successfully created folder: {folder.name} (ID: {folder.id})")
        print(f"✅ Folder project: {folder.project.name} (ID: {folder.project.id})")
        
        # Clean up test folder
        folder.delete()
        print("🧹 Cleaned up test folder")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating folder: {e}")
        return False

if __name__ == "__main__":
    success = test_web_unlocker_logic()
    
    if success:
        print("\n🎉 SUCCESS: Web Unlocker logic works locally!")
        print("✅ The fix should work in production")
    else:
        print("\n❌ FAILED: Web Unlocker logic has issues")
        print("⚠️ Need to investigate further")