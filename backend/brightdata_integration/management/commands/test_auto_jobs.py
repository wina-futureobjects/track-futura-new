#!/usr/bin/env python3
"""
🧪 DJANGO MANAGEMENT COMMAND FOR TESTING AUTOMATIC JOB CREATION
===============================================================

Django management command to test the automatic job creation workflow.
Run with: python manage.py test_auto_jobs
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from brightdata_integration.services import BrightDataAutomatedBatchScraper
from track_accounts.models import UnifiedRunFolder
from users.models import Project

class Command(BaseCommand):
    help = 'Test automatic job creation workflow for BrightData scraping'

    def handle(self, *args, **options):
        self.stdout.write("🧪 TESTING BRIGHTDATA AUTOMATIC JOB CREATION")
        self.stdout.write("=" * 50)
        
        # Show current structure
        self.show_current_job_structure()
        
        # Test automatic job creation
        self.test_automatic_job_creation()
        
        # Show updated structure
        self.stdout.write("\n" + "=" * 50)
        self.show_current_job_structure()
        
        self.stdout.write("\n✅ Test completed! Check the data storage pages to see the new job folder.")

    def create_test_scraped_data(self):
        """Create test scraped data for testing automatic job creation"""
        try:
            self.stdout.write("🧪 Creating test scraped data...")
            
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
            self.stdout.write(f"✅ Created test scraper request: {scraper_request.id}")
            
            # Create test scraped posts
            for i in range(5):
                BrightDataScrapedPost.objects.create(
                    scraper_request=scraper_request,
                    folder_id=0,  # No folder yet - will be set by automatic job creation
                    post_id=f'test_post_{i}_{int(timezone.now().timestamp())}',
                    url=f'https://instagram.com/p/test_post_{i}/',
                    platform='instagram',
                    user_posted='test_user_account',
                    content=f'Test post content {i} for automatic job creation workflow testing',
                    likes=100 + i * 10,
                    num_comments=5 + i * 2,
                    date_posted=timezone.now(),
                    raw_data={'test': True, 'post_number': i}
                )
            
            self.stdout.write(f"✅ Created 5 test scraped posts")
            return scraper_request
            
        except Exception as e:
            self.stdout.write(f"❌ Error creating test data: {e}")
            return None

    def test_automatic_job_creation(self):
        """Test the automatic job creation workflow"""
        self.stdout.write("\n🚀 TESTING AUTOMATIC JOB CREATION WORKFLOW")
        self.stdout.write("=" * 50)
        
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
            self.stdout.write("📝 No existing completed scraper requests with data found")
            test_request = self.create_test_scraped_data()
            if not test_request:
                self.stdout.write("❌ Failed to create test data")
                return
        
        self.stdout.write(f"🎯 Testing with scraper request {test_request.id}")
        self.stdout.write(f"📊 Posts to organize: {test_request.scraped_posts.count()}")
        self.stdout.write(f"🔧 Platform: {test_request.platform}")
        
        # Get current job count
        before_count = UnifiedRunFolder.objects.filter(folder_type='job').count()
        self.stdout.write(f"📋 Current job folders: {before_count}")
        
        # Test automatic job creation
        try:
            scraper_service = BrightDataAutomatedBatchScraper()
            result = scraper_service.create_automatic_job_for_completed_scraper(test_request)
            
            if result:
                self.stdout.write(f"\n🎉 SUCCESS! Automatic job creation worked!")
                self.stdout.write(f"   Job Number: {result['job_number']}")
                self.stdout.write(f"   Job Folder ID: {result['job_folder_id']}")
                self.stdout.write(f"   Posts Moved: {result['moved_posts']}")
                self.stdout.write(f"   Data Storage URL: {result['data_storage_url']}")
                
                # Verify job folder was created
                after_count = UnifiedRunFolder.objects.filter(folder_type='job').count()
                self.stdout.write(f"📋 Job folders after: {after_count} (increased by {after_count - before_count})")
                
                # Verify job folder exists
                job_folder = UnifiedRunFolder.objects.get(id=result['job_folder_id'])
                self.stdout.write(f"   Job Folder Name: {job_folder.name}")
                self.stdout.write(f"   Job Folder Type: {job_folder.folder_type}")
                self.stdout.write(f"   Job Folder Platform: {job_folder.platform_code}")
                
                # Check platform-specific data
                if test_request.platform == 'instagram':
                    from instagram_data.models import Folder as IGFolder, InstagramPost
                    ig_folders = IGFolder.objects.filter(unified_job_folder=job_folder)
                    if ig_folders.exists():
                        ig_folder = ig_folders.first()
                        post_count = InstagramPost.objects.filter(folder=ig_folder).count()
                        self.stdout.write(f"   Instagram Folder: {ig_folder.name} ({post_count} posts)")
                    
                elif test_request.platform == 'facebook':
                    from facebook_data.models import Folder as FBFolder, FacebookPost
                    fb_folders = FBFolder.objects.filter(unified_job_folder=job_folder)
                    if fb_folders.exists():
                        fb_folder = fb_folders.first()
                        post_count = FacebookPost.objects.filter(folder=fb_folder).count()
                        self.stdout.write(f"   Facebook Folder: {fb_folder.name} ({post_count} posts)")
                
                self.stdout.write(f"\n🌐 RESULT: Data should now appear at URL: {result['data_storage_url']}")
                
            else:
                self.stdout.write("❌ Automatic job creation failed")
                
        except Exception as e:
            self.stdout.write(f"❌ Error testing automatic job creation: {e}")
            import traceback
            traceback.print_exc()

    def show_current_job_structure(self):
        """Display current job folder structure"""
        self.stdout.write("\n📁 CURRENT JOB FOLDER STRUCTURE")
        self.stdout.write("=" * 40)
        
        job_folders = UnifiedRunFolder.objects.filter(
            folder_type='job'
        ).order_by('name')
        
        if not job_folders.exists():
            self.stdout.write("📭 No job folders found")
            return
        
        for job_folder in job_folders:
            self.stdout.write(f"📂 {job_folder.name} (ID: {job_folder.id})")
            self.stdout.write(f"   Platform: {job_folder.platform_code}")
            self.stdout.write(f"   Service: {job_folder.service_code}")
            self.stdout.write(f"   Content Count: {job_folder.get_content_count()}")
            
            # Check platform-specific folders
            if job_folder.platform_code == 'instagram':
                try:
                    from instagram_data.models import Folder as IGFolder
                    ig_folders = IGFolder.objects.filter(unified_job_folder=job_folder)
                    for ig_folder in ig_folders:
                        self.stdout.write(f"   └── Instagram: {ig_folder.name}")
                except:
                    pass
                    
            elif job_folder.platform_code == 'facebook':
                try:
                    from facebook_data.models import Folder as FBFolder
                    fb_folders = FBFolder.objects.filter(unified_job_folder=job_folder)
                    for fb_folder in fb_folders:
                        self.stdout.write(f"   └── Facebook: {fb_folder.name}")
                except:
                    pass
            
            self.stdout.write("")