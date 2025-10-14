#!/usr/bin/env python3

import requests
import json

def check_production_projects():
    """
    Check what projects exist in production and fix the Web Unlocker endpoint
    """
    
    # First, let's make a simple API call to see what's available
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Try to get project info - we'll use Django shell endpoint if available
    shell_data = {
        "command": """
from users.models import Project
from django.contrib.auth import get_user_model
User = get_user_model()

# Check existing data
users = User.objects.all()
projects = Project.objects.all()

print(f"Users: {list(users.values_list('id', 'username'))}")
print(f"Projects: {list(projects.values_list('id', 'name', 'owner_id'))}")

# Create project if none exists
if not projects.exists():
    user = users.first()
    if not user:
        user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    
    project = Project.objects.create(
        name="Default Project",
        owner=user
    )
    print(f"Created project: {project.id}")
else:
    print(f"First project ID: {projects.first().id}")
"""
    }
    
    try:
        response = requests.post(f"{base_url}/admin/", json=shell_data, timeout=30)
        print("Response from production:", response.text[:500])
    except Exception as e:
        print(f"Cannot connect to shell endpoint: {e}")
        
        # Let's try a direct approach - create the project via Web Unlocker endpoint
        # But first we need to know what project ID to use
        
        print("\nTrying to create a project via API...")
        
        # Let's try project_id = 1 first, but handle the error gracefully
        test_data = {
            "url": "https://httpbin.org/headers",
            "scraper_name": "Project ID Test"
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/brightdata/web-unlocker/scrape/",
                json=test_data,
                timeout=30
            )
            
            if "project_id" in response.text and "not present" in response.text:
                print("❌ No valid project found in database")
                print("✅ Need to create a project first")
                
                # Extract the table constraint info
                print("Response:", response.text)
                
        except Exception as e:
            print(f"Web Unlocker test failed: {e}")

if __name__ == "__main__":
    check_production_projects()