#!/usr/bin/env python3
"""
🧪 TEST AUTOMATIC JOB CREATION
=============================

Test script to verify the new automatic job creation workflow
for BrightData scraping results.

This will:
1. Find or create test scraped data
2. Test the automatic job creation
3. Verify the job appears in data storage URLs
"""

import os
import sys
import django

# Set up Django environment
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')
django.setup()

from django.db import transaction
from django.utils import timezone
from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from brightdata_integration.services import BrightDataAutomatedBatchScraper
from track_accounts.models import UnifiedRunFolder
from users.models import Project

def create_test_scraped_data():
    """Create test scraped data for testing automatic job creation"""
    try:
        print("🧪 Creating test scraped data...")
        
        project = Project.objects.get(id=1)
        
        # Create a test scraper request
        scraper_request = BrightDataScraperRequest.objects.create(
            platform='instagram',
            content_type='posts',
            target_url='https://instagram.com/test_account',
            source_name='Test Account',
            dataset_id='gd_lk5ns7kz21pck8jpis',
            status='completed',
            completed_at=timezone.now()
        )
        print(f"✅ Created test scraper request: {scraper_request.id}")
        
        # Create test scraped posts
        for i in range(5):
            BrightDataScrapedPost.objects.create(
                scraper_request=scraper_request,
                folder_id=0,  # No folder yet - will be set by automatic job creation
                post_id=f'test_post_{i}_{timezone.now().timestamp()}',
                url=f'https://instagram.com/p/test_post_{i}/',
                platform='instagram',
                user_posted='test_user_account',
                content=f'Test post content {i} for automatic job creation workflow testing',
                likes=100 + i * 10,
                num_comments=5 + i * 2,
                date_posted=timezone.now(),
                raw_data={'test': True, 'post_number': i}
            )
        
        print(f"✅ Created 5 test scraped posts")
        return scraper_request
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        return None

def test_automatic_job_creation():
    """Test the automatic job creation workflow"""
    print("\n🚀 TESTING AUTOMATIC JOB CREATION WORKFLOW")
    print("=" * 50)
    
    # Check for existing completed scraper requests
    existing_requests = BrightDataScraperRequest.objects.filter(
        status='completed'
    ).prefetch_related('scraped_posts')
    
    test_request = None
    
    # Find a request with scraped posts
    for request in existing_requests:
        if request.scraped_posts.count() > 0:
            test_request = request
            break
    
    # If no existing data, create test data
    if not test_request:
        print("📝 No existing completed scraper requests with data found")
        test_request = create_test_scraped_data()
        if not test_request:
            print("❌ Failed to create test data")
            return
    
    print(f"🎯 Testing with scraper request {test_request.id}")
    print(f"📊 Posts to organize: {test_request.scraped_posts.count()}")
    print(f"🔧 Platform: {test_request.platform}")
    
    # Get current job count
    before_count = UnifiedRunFolder.objects.filter(folder_type='job').count()
    print(f"📋 Current job folders: {before_count}")
    
    # Test automatic job creation
    try:
        scraper_service = BrightDataAutomatedBatchScraper()
        result = scraper_service.create_automatic_job_for_completed_scraper(test_request)
        
        if result:
            print(f"\n🎉 SUCCESS! Automatic job creation worked!")
            print(f"   Job Number: {result['job_number']}")
            print(f"   Job Folder ID: {result['job_folder_id']}")
            print(f"   Posts Moved: {result['moved_posts']}")
            print(f"   Data Storage URL: {result['data_storage_url']}")
            
            # Verify job folder was created
            after_count = UnifiedRunFolder.objects.filter(folder_type='job').count()
            print(f"📋 Job folders after: {after_count} (increased by {after_count - before_count})")
            
            # Verify job folder exists
            job_folder = UnifiedRunFolder.objects.get(id=result['job_folder_id'])
            print(f"   Job Folder Name: {job_folder.name}")
            print(f"   Job Folder Type: {job_folder.folder_type}")
            print(f"   Job Folder Platform: {job_folder.platform_code}")
            
            # Check platform-specific data
            if test_request.platform == 'instagram':
                from instagram_data.models import Folder as IGFolder, InstagramPost
                ig_folders = IGFolder.objects.filter(unified_job_folder=job_folder)
                if ig_folders.exists():
                    ig_folder = ig_folders.first()
                    post_count = InstagramPost.objects.filter(folder=ig_folder).count()
                    print(f"   Instagram Folder: {ig_folder.name} ({post_count} posts)")
                
            elif test_request.platform == 'facebook':
                from facebook_data.models import Folder as FBFolder, FacebookPost
                fb_folders = FBFolder.objects.filter(unified_job_folder=job_folder)
                if fb_folders.exists():
                    fb_folder = fb_folders.first()
                    post_count = FacebookPost.objects.filter(folder=fb_folder).count()
                    print(f"   Facebook Folder: {fb_folder.name} ({post_count} posts)")
            
            print(f"\n🌐 RESULT: Data should now appear at URL: {result['data_storage_url']}")
            
        else:
            print("❌ Automatic job creation failed")
            
    except Exception as e:
        print(f"❌ Error testing automatic job creation: {e}")
        import traceback
        traceback.print_exc()

def show_current_job_structure():
    """Display current job folder structure"""
    print("\n📁 CURRENT JOB FOLDER STRUCTURE")
    print("=" * 40)
    
    job_folders = UnifiedRunFolder.objects.filter(
        folder_type='job'
    ).order_by('name')
    
    for job_folder in job_folders:
        print(f"📂 {job_folder.name} (ID: {job_folder.id})")
        print(f"   Platform: {job_folder.platform_code}")
        print(f"   Service: {job_folder.service_code}")
        print(f"   Content Count: {job_folder.get_content_count()}")
        
        # Check platform-specific folders
        if job_folder.platform_code == 'instagram':
            try:
                from instagram_data.models import Folder as IGFolder
                ig_folders = IGFolder.objects.filter(unified_job_folder=job_folder)
                for ig_folder in ig_folders:
                    print(f"   └── Instagram: {ig_folder.name}")
            except:
                pass
                
        elif job_folder.platform_code == 'facebook':
            try:
                from facebook_data.models import Folder as FBFolder
                fb_folders = FBFolder.objects.filter(unified_job_folder=job_folder)
                for fb_folder in fb_folders:
                    print(f"   └── Facebook: {fb_folder.name}")
            except:
                pass
        
        print()

if __name__ == "__main__":
    print("🧪 TESTING BRIGHTDATA AUTOMATIC JOB CREATION")
    print("=" * 50)
    
    # Show current structure
    show_current_job_structure()
    
    # Test automatic job creation
    test_automatic_job_creation()
    
    # Show updated structure
    print("\n" + "=" * 50)
    show_current_job_structure()
    
    print("\n✅ Test completed! Check the data storage pages to see the new job folder.")