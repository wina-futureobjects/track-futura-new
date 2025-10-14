#!/usr/bin/env python3

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')
django.setup()

from users.models import Project
from django.contrib.auth import get_user_model

def setup_project():
    """
    Setup a default project for the Web Unlocker endpoint
    """
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
            description="Main project for BrightData Web Unlocker integration",
            owner=user
        )
        print(f"✅ Created project: {project.name} (ID: {project.id})")
    else:
        print(f"✅ Found project: {project.name} (ID: {project.id})")
    
    return project.id

if __name__ == "__main__":
    try:
        project_id = setup_project()
        print(f"\n🎯 Use project_id={project_id} in Web Unlocker endpoint")
        
        # Update the WebUnlockerAPIView with correct project_id
        views_file = "brightdata_integration/views.py"
        if os.path.exists(views_file):
            with open(views_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace project_id=1 with the actual project ID
            if f"project_id={project_id}" not in content:
                content = content.replace(
                    "project_id=1",
                    f"project_id={project_id}"
                )
                
                with open(views_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Updated views.py with project_id={project_id}")
            else:
                print("✅ Views.py already has correct project_id")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)