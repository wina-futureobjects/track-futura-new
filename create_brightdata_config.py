#!/usr/bin/env python
"""
Create BrightData configuration for production
"""
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataConfig
from users.models import Project

def create_brightdata_config():
    print("🔧 CREATING BRIGHTDATA CONFIGURATION")
    print("="*50)
    
    try:
        # Get or create a project to associate with
        project, created = Project.objects.get_or_create(
            id=1,
            defaults={
                'name': 'Default BrightData Project',
                'description': 'Default project for BrightData configurations'
            }
        )
        
        if created:
            print(f"✅ Created default project: {project.name}")
        else:
            print(f"✅ Using existing project: {project.name}")
        
        # Create BrightData config with correct settings
        config, created = BrightDataConfig.objects.get_or_create(
            platform='instagram',
            defaults={
                'dataset_id': 'web_unlocker1',  # CORRECT zone name
                'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb',  # Working token
                'project': project,
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Created new BrightData config:")
        else:
            print(f"✅ Updated existing BrightData config:")
            # Update existing config with correct values
            config.dataset_id = 'web_unlocker1'
            config.api_token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
            config.is_active = True
            config.save()
        
        print(f"   Platform: {config.platform}")
        print(f"   Dataset ID: {config.dataset_id}")
        print(f"   API Token: {config.api_token[:20]}...")
        print(f"   Project: {config.project}")
        print(f"   Active: {config.is_active}")
        
        print("\n🎉 BrightData configuration created successfully!")
        print("✅ Zone name 'web_unlocker1' is correctly set!")
        print("✅ Superadmin can now scrape!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_brightdata_config()