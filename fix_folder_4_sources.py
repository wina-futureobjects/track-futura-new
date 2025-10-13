#!/usr/bin/env python3

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django environment
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')
django.setup()

from track_accounts.models import SourceFolder, TrackSource

def check_folder_4_sources():
    """Check what's in folder 4 and fix if needed"""
    
    print("🔍 FOLDER 4 DIAGNOSIS")
    print("=" * 50)
    
    try:
        # Check if folder 4 exists
        try:
            folder_4 = SourceFolder.objects.get(id=4, project_id=1)
            print(f"✅ Folder 4 exists: {folder_4.name}")
        except SourceFolder.DoesNotExist:
            print("❌ Folder 4 does not exist!")
            
            # Check what folders do exist
            print("\n📁 Available folders in project 1:")
            folders = SourceFolder.objects.filter(project_id=1)
            for folder in folders:
                sources_count = TrackSource.objects.filter(folder_id=folder.id, folder__project_id=1).count()
                print(f"  Folder {folder.id}: {folder.name} ({sources_count} sources)")
            
            # Create folder 4 with Nike sources
            print("\n🔧 Creating folder 4 with Nike sources...")
            folder_4 = SourceFolder.objects.create(
                id=4,
                name="Nike - Complete Social Media Collection",
                description="Complete Nike social media collection including Instagram and Facebook",
                project_id=1,
                created_at=datetime.now()
            )
            print(f"✅ Created folder 4: {folder_4.name}")
        
        # Check sources in folder 4
        sources_in_folder_4 = TrackSource.objects.filter(folder_id=4, folder__project_id=1)
        print(f"\n📊 Sources in folder 4: {sources_in_folder_4.count()}")
        
        if sources_in_folder_4.count() == 0:
            print("❌ No sources in folder 4! Creating Nike sources...")
            
            # Create Nike Instagram source
            instagram_source = TrackSource.objects.create(
                name="Nike Instagram",
                platform="instagram",
                username="nike",
                folder_id=4,
                is_active=True,
                created_at=datetime.now()
            )
            print(f"✅ Created Instagram source: {instagram_source.name}")
            
            # Create Nike Facebook source  
            facebook_source = TrackSource.objects.create(
                name="Nike Facebook",
                platform="facebook", 
                username="nike",
                folder_id=4,
                is_active=True,
                created_at=datetime.now()
            )
            print(f"✅ Created Facebook source: {facebook_source.name}")
            
        else:
            print("✅ Sources found in folder 4:")
            for source in sources_in_folder_4:
                print(f"  - {source.name} ({source.platform})")
        
        # Final verification
        final_sources = TrackSource.objects.filter(folder_id=4, folder__project_id=1)
        print(f"\n🎯 FINAL CHECK: Folder 4 now has {final_sources.count()} sources")
        
        if final_sources.count() > 0:
            print("✅ SUCCESS: Folder 4 is ready for scraping!")
            return True
        else:
            print("❌ FAILED: Still no sources in folder 4")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_scraper_endpoint():
    """Test the scraper endpoint that was failing"""
    
    print("\n🧪 TESTING SCRAPER ENDPOINT")
    print("=" * 50)
    
    try:
        # Test the production endpoint
        test_url = "https://trackfutura.futureobjects.io/api/brightdata/trigger-scraper/"
        
        test_data = {
            "folder_id": 4,
            "platforms": ["instagram", "facebook"]
        }
        
        print(f"Testing: {test_url}")
        print(f"Data: {test_data}")
        
        response = requests.post(test_url, json=test_data, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result}")
            return True
        else:
            print(f"❌ ERROR: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ENDPOINT ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 FIXING FOLDER 4 SCRAPER ISSUE")
    print("=" * 60)
    
    # Fix folder 4
    folder_fixed = check_folder_4_sources()
    
    # Test scraper
    if folder_fixed:
        test_scraper_endpoint()
    
    print("\n🏁 DIAGNOSIS COMPLETE")