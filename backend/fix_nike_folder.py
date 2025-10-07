#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from instagram_data.models import Folder

def fix_nike_folder_name():
    """Fix the Nike folder name to match the expected pattern"""
    print("🔧 Fixing Nike folder name...")
    
    try:
        # Find the Nike folder
        nike_folder = Folder.objects.filter(name__icontains="Nike Instagram Data").first()
        
        if nike_folder:
            print(f"✅ Found Nike folder: {nike_folder.name}")
            
            # Update the name to match the pattern expected by _get_platform_results
            new_name = "Instagram Posts Collection - Job 8 - Instagram - Nike"
            nike_folder.name = new_name
            nike_folder.save()
            
            print(f"✅ Updated folder name to: {new_name}")
            
            # Also remove the old test folder to avoid confusion
            old_folder = Folder.objects.filter(
                name="Instagram Posts Collection - Job 8 - Instagram Posts - 2025-09-29 20:56"
            ).first()
            
            if old_folder:
                print(f"🗑️ Removing old test folder: {old_folder.name}")
                old_folder.delete()
            
            print("🎉 Nike folder is now ready to be found by the API!")
            
        else:
            print("❌ Nike folder not found")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    fix_nike_folder_name()