#!/usr/bin/env python3
"""
Simple test script to check TrackSource data and API endpoint
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import TrackSource
from users.models import Project

def check_tracksource_data():
    """Check if there are any TrackSource entries in the database"""
    print("=== TrackSource Data Check ===")
    
    # Check total count
    total_sources = TrackSource.objects.all().count()
    print(f"Total TrackSource entries: {total_sources}")
    
    if total_sources == 0:
        print("No TrackSource entries found in database")
        return False
    
    # Check by project
    projects = Project.objects.all()
    print(f"Available projects: {projects.count()}")
    
    for project in projects:
        project_sources = TrackSource.objects.filter(project=project).count()
        print(f"Project {project.id} ({project.name}): {project_sources} sources")
        
        if project_sources > 0:
            sources = TrackSource.objects.filter(project=project)[:3]  # Show first 3
            for source in sources:
                print(f"  - {source.name}: FB={bool(source.facebook_link)}, IG={bool(source.instagram_link)}, LI={bool(source.linkedin_link)}, TT={bool(source.tiktok_link)}")
    
    return True

def create_test_data():
    """Create some test TrackSource data"""
    print("\n=== Creating Test Data ===")
    
    # Get or create project
    project, created = Project.objects.get_or_create(
        id=1,
        defaults={
            'name': 'Test Project',
            'description': 'Test project for debugging'
        }
    )
    
    if created:
        print(f"Created project: {project.name}")
    else:
        print(f"Using existing project: {project.name}")
    
    # Create test sources
    test_sources = [
        {
            'name': 'Test Company 1',
            'facebook_link': 'https://www.facebook.com/testcompany1',
            'instagram_link': 'https://www.instagram.com/testcompany1',
            'linkedin_link': 'https://www.linkedin.com/company/testcompany1',
            'tiktok_link': 'https://www.tiktok.com/@testcompany1',
            'other_social_media': 'https://twitter.com/testcompany1'
        },
        {
            'name': 'Test Company 2',
            'facebook_link': 'https://www.facebook.com/testcompany2',
            'instagram_link': None,
            'linkedin_link': 'https://www.linkedin.com/company/testcompany2',
            'tiktok_link': None,
            'other_social_media': None
        }
    ]
    
    created_count = 0
    for source_data in test_sources:
        source, created = TrackSource.objects.get_or_create(
            name=source_data['name'],
            project=project,
            defaults=source_data
        )
        
        if created:
            created_count += 1
            print(f"Created source: {source.name}")
        else:
            print(f"Source already exists: {source.name}")
    
    print(f"Created {created_count} new test sources")
    return True

if __name__ == '__main__':
    print("TrackSource Data Test Script")
    print("=" * 40)
    
    # Check existing data
    has_data = check_tracksource_data()
    
    # Create test data if none exists
    if not has_data:
        create_test_data()
        print("\n" + "=" * 40)
        check_tracksource_data()
    
    print("\nTest completed!") 