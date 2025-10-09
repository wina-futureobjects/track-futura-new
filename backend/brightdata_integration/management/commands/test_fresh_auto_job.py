#!/usr/bin/env python3
"""
🧪 CREATE FRESH TEST DATA FOR AUTOMATIC JOB CREATION
===================================================

Create fresh test scraped data and test automatic job creation workflow.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from brightdata_integration.services import BrightDataAutomatedBatchScraper
from track_accounts.models import UnifiedRunFolder
from users.models import Project

class Command(BaseCommand):
    help = 'Create fresh test data and test automatic job creation'

    def handle(self, *args, **options):
        self.stdout.write("🧪 CREATING FRESH TEST DATA AND TESTING AUTOMATIC JOB")
        self.stdout.write("=" * 55)
        
        # Create fresh test data
        scraper_request = self.create_fresh_test_data()
        if not scraper_request:
            self.stdout.write("❌ Failed to create test data")
            return
        
        # Test automatic job creation
        self.test_job_creation_with_fresh_data(scraper_request)

    def create_fresh_test_data(self):
        """Create fresh test scraped data"""
        try:
            self.stdout.write("🧪 Creating fresh test scraped data...")
            
            # Create a fresh test scraper request
            timestamp = int(timezone.now().timestamp())
            scraper_request = BrightDataScraperRequest.objects.create(
                platform='instagram',
                content_type='posts',
                target_url=f'https://instagram.com/test_account_{timestamp}',
                source_name=f'Test Account {timestamp}',
                dataset_id='gd_lk5ns7kz21pck8jpis',
                status='completed',
                completed_at=timezone.now()
            )
            self.stdout.write(f"✅ Created fresh scraper request: {scraper_request.id}")
            
            # Create fresh test scraped posts with unique IDs
            for i in range(3):
                BrightDataScrapedPost.objects.create(
                    scraper_request=scraper_request,
                    folder_id=0,  # No folder yet - will be set by automatic job creation
                    post_id=f'fresh_test_post_{timestamp}_{i}',
                    url=f'https://instagram.com/p/fresh_test_post_{timestamp}_{i}/',
                    platform='instagram',
                    user_posted=f'test_user_{timestamp}',
                    content=f'Fresh test post content {i} for automatic job creation - {timestamp}',
                    likes=50 + i * 5,
                    num_comments=3 + i,
                    date_posted=timezone.now(),
                    hashtags=['#test', '#automatic', f'#post{i}'],
                    raw_data={'test': True, 'fresh': True, 'post_number': i, 'timestamp': timestamp}
                )
            
            self.stdout.write(f"✅ Created 3 fresh test scraped posts")
            return scraper_request
            
        except Exception as e:
            self.stdout.write(f"❌ Error creating fresh test data: {e}")
            return None

    def test_job_creation_with_fresh_data(self, scraper_request):
        """Test automatic job creation with fresh data"""
        self.stdout.write("\n🚀 TESTING AUTOMATIC JOB CREATION WITH FRESH DATA")
        self.stdout.write("=" * 50)
        
        self.stdout.write(f"🎯 Testing with fresh scraper request {scraper_request.id}")
        self.stdout.write(f"📊 Posts to organize: {scraper_request.scraped_posts.count()}")
        self.stdout.write(f"🔧 Platform: {scraper_request.platform}")
        
        # Get current job count
        before_count = UnifiedRunFolder.objects.filter(folder_type='job').count()
        self.stdout.write(f"📋 Current job folders: {before_count}")
        
        # Test automatic job creation
        try:
            scraper_service = BrightDataAutomatedBatchScraper()
            result = scraper_service.create_automatic_job_for_completed_scraper(scraper_request)
            
            if result:
                self.stdout.write(f"\n🎉 SUCCESS! Fresh data automatic job creation worked!")
                self.stdout.write(f"   Job Number: {result['job_number']}")
                self.stdout.write(f"   Job Folder ID: {result['job_folder_id']}")
                self.stdout.write(f"   Posts Moved: {result['moved_posts']}")
                self.stdout.write(f"   Data Storage URL: {result['data_storage_url']}")
                
                # Verify job folder was created
                after_count = UnifiedRunFolder.objects.filter(folder_type='job').count()
                self.stdout.write(f"📋 Job folders after: {after_count} (increased by {after_count - before_count})")
                
                # Verify job folder exists and has data
                job_folder = UnifiedRunFolder.objects.get(id=result['job_folder_id'])
                self.stdout.write(f"   Job Folder Name: {job_folder.name}")
                
                # Check Instagram-specific data
                from instagram_data.models import Folder as IGFolder, InstagramPost
                ig_folders = IGFolder.objects.filter(unified_job_folder=job_folder)
                if ig_folders.exists():
                    ig_folder = ig_folders.first()
                    post_count = InstagramPost.objects.filter(folder=ig_folder).count()
                    self.stdout.write(f"   Instagram Folder: {ig_folder.name} ({post_count} posts)")
                    
                    # Show sample posts
                    if post_count > 0:
                        sample_posts = InstagramPost.objects.filter(folder=ig_folder)[:2]
                        for post in sample_posts:
                            self.stdout.write(f"     📝 Post: {post.post_id} by {post.user_posted} - {post.likes} likes")
                
                self.stdout.write(f"\n🌐 RESULT: Fresh data should now appear at URL: {result['data_storage_url']}")
                self.stdout.write(f"🎯 The user can now see Job {result['job_number']} in their data storage pages!")
                
            else:
                self.stdout.write("❌ Fresh data automatic job creation failed")
                
        except Exception as e:
            self.stdout.write(f"❌ Error testing fresh data automatic job creation: {e}")
            import traceback
            traceback.print_exc()