#!/usr/bin/env python3
"""
🚀 AUTOMATIC JOB CREATION WORKFLOW
==================================

This script enhances the BrightData integration to automatically:
1. Create new job folders with incremental numbers when scraping completes
2. Store scraped data in the new job folder 
3. Update data storage URLs with the new job number
4. Ensure scraped data appears in data storage pages

User Request: "AFTER I SCRAPED DATA, AND AFTER IT IS SUCCESSFUL ON BRIGHTDATA, 
I WANT IT TO BE STORED ON DATA STORAGE"

Target: /data-storage/job/XXX with automatic job number generation
"""

import os
import sys
import django

# Set up Django environment
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')
django.setup()

from django.db import transaction
from django.utils import timezone
from track_accounts.models import UnifiedRunFolder
from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest
from users.models import Project
from workflow.models import ScrapingRun

def get_next_job_number(project_id=1):
    """
    Get the next job number by finding the highest existing job number
    """
    try:
        # Find all job folders for this project
        job_folders = UnifiedRunFolder.objects.filter(
            project_id=project_id,
            folder_type='job'
        ).values_list('name', flat=True)
        
        # Extract job numbers
        job_numbers = []
        for name in job_folders:
            # Look for patterns like "Job 195", "job195", "195", etc.
            import re
            match = re.search(r'(\d+)', name)
            if match:
                job_numbers.append(int(match.group(1)))
        
        # Get next number
        if job_numbers:
            next_number = max(job_numbers) + 1
        else:
            next_number = 1  # Start from 1 if no jobs exist
            
        print(f"📊 Found {len(job_numbers)} existing jobs, next number: {next_number}")
        return next_number
        
    except Exception as e:
        print(f"❌ Error getting next job number: {e}")
        return 196  # Safe fallback

def create_job_folder_hierarchy(job_number, platform, project_id=1):
    """
    Create the complete folder hierarchy for a new job:
    Run -> Platform -> Service -> Job
    """
    try:
        with transaction.atomic():
            project = Project.objects.get(id=project_id)
            
            # 1. Get or create Run folder
            run_folder, created = UnifiedRunFolder.objects.get_or_create(
                project=project,
                folder_type='run',
                name=f'BrightData Scraping Run',
                defaults={
                    'description': 'Automated BrightData scraping runs',
                    'category': 'posts'
                }
            )
            if created:
                print(f"✅ Created Run folder: {run_folder.name}")
            
            # 2. Get or create Platform folder under Run
            platform_folder, created = UnifiedRunFolder.objects.get_or_create(
                project=project,
                folder_type='platform',
                platform_code=platform,
                parent_folder=run_folder,
                name=f'{platform.title()} Platform',
                defaults={
                    'description': f'All {platform} data collection',
                    'category': 'posts'
                }
            )
            if created:
                print(f"✅ Created Platform folder: {platform_folder.name}")
            
            # 3. Get or create Service folder under Platform
            service_folder, created = UnifiedRunFolder.objects.get_or_create(
                project=project,
                folder_type='service',
                platform_code=platform,
                service_code='posts',
                parent_folder=platform_folder,
                name=f'{platform.title()} Posts Service',
                defaults={
                    'description': f'{platform} posts scraping service',
                    'category': 'posts'
                }
            )
            if created:
                print(f"✅ Created Service folder: {service_folder.name}")
            
            # 4. Create new Job folder
            job_folder = UnifiedRunFolder.objects.create(
                project=project,
                folder_type='job',
                platform_code=platform,
                service_code='posts',
                parent_folder=service_folder,
                name=f'Job {job_number}',
                description=f'Automated job {job_number} - {platform} posts scraping',
                category='posts'
            )
            print(f"🎯 Created Job folder: {job_folder.name} (ID: {job_folder.id})")
            
            return job_folder
            
    except Exception as e:
        print(f"❌ Error creating folder hierarchy: {e}")
        return None

def create_platform_specific_folder(job_folder, platform):
    """
    Create platform-specific folder linked to the unified job folder
    """
    try:
        if platform == 'instagram':
            from instagram_data.models import Folder as IGFolder
            ig_folder = IGFolder.objects.create(
                name=f'Job {job_folder.name.split()[-1]} - Instagram Posts',
                description=f'Instagram posts for {job_folder.name}',
                category='posts',
                project=job_folder.project,
                folder_type='run',
                unified_job_folder=job_folder
            )
            print(f"✅ Created Instagram folder: {ig_folder.name} (ID: {ig_folder.id})")
            return ig_folder
            
        elif platform == 'facebook':
            from facebook_data.models import Folder as FBFolder
            fb_folder = FBFolder.objects.create(
                name=f'Job {job_folder.name.split()[-1]} - Facebook Posts',
                description=f'Facebook posts for {job_folder.name}',
                category='posts',
                project=job_folder.project,
                folder_type='run',
                unified_job_folder=job_folder
            )
            print(f"✅ Created Facebook folder: {fb_folder.name} (ID: {fb_folder.id})")
            return fb_folder
            
        # Add other platforms as needed
        return None
        
    except Exception as e:
        print(f"❌ Error creating platform-specific folder: {e}")
        return None

def move_scraped_data_to_job_folder(job_folder, platform_folder, scraper_request):
    """
    Move scraped posts from BrightData to the new job folder
    """
    try:
        # Get all scraped posts for this scraper request
        scraped_posts = BrightDataScrapedPost.objects.filter(
            scraper_request=scraper_request
        )
        
        if not scraped_posts.exists():
            print(f"⚠️ No scraped posts found for scraper request {scraper_request.id}")
            return 0
        
        moved_count = 0
        
        if scraper_request.platform == 'instagram' and platform_folder:
            from instagram_data.models import InstagramPost, InstagramAccount
            
            for scraped_post in scraped_posts:
                try:
                    # Get or create Instagram account
                    account, created = InstagramAccount.objects.get_or_create(
                        username=scraped_post.user_posted or 'unknown',
                        defaults={
                            'display_name': scraped_post.user_posted or 'Unknown',
                            'followers_count': scraped_post.follower_count or 0,
                        }
                    )
                    
                    # Create Instagram post in the job folder
                    instagram_post, created = InstagramPost.objects.get_or_create(
                        post_id=scraped_post.post_id,
                        folder=platform_folder,
                        defaults={
                            'account': account,
                            'content': scraped_post.content or '',
                            'likes_count': scraped_post.likes or 0,
                            'comments_count': scraped_post.num_comments or 0,
                            'date_posted': scraped_post.date_posted,
                            'url': scraped_post.url or '',
                            'hashtags': scraped_post.hashtags or [],
                            'mentions': scraped_post.mentions or [],
                            'media_type': scraped_post.media_type or 'post',
                            'media_url': scraped_post.media_url or '',
                            'location': scraped_post.location or '',
                        }
                    )
                    
                    if created:
                        moved_count += 1
                        print(f"✅ Moved post {scraped_post.post_id} to job folder")
                    
                except Exception as e:
                    print(f"❌ Error moving post {scraped_post.post_id}: {e}")
                    continue
        
        elif scraper_request.platform == 'facebook' and platform_folder:
            from facebook_data.models import FacebookPost, FacebookAccount
            
            for scraped_post in scraped_posts:
                try:
                    # Get or create Facebook account
                    account, created = FacebookAccount.objects.get_or_create(
                        username=scraped_post.user_posted or 'unknown',
                        defaults={
                            'display_name': scraped_post.user_posted or 'Unknown',
                            'followers_count': scraped_post.follower_count or 0,
                        }
                    )
                    
                    # Create Facebook post in the job folder
                    facebook_post, created = FacebookPost.objects.get_or_create(
                        post_id=scraped_post.post_id,
                        folder=platform_folder,
                        defaults={
                            'account': account,
                            'content': scraped_post.content or '',
                            'likes_count': scraped_post.likes or 0,
                            'comments_count': scraped_post.num_comments or 0,
                            'shares_count': scraped_post.shares or 0,
                            'date_posted': scraped_post.date_posted,
                            'url': scraped_post.url or '',
                            'location': scraped_post.location or '',
                        }
                    )
                    
                    if created:
                        moved_count += 1
                        print(f"✅ Moved post {scraped_post.post_id} to job folder")
                    
                except Exception as e:
                    print(f"❌ Error moving post {scraped_post.post_id}: {e}")
                    continue
        
        print(f"📊 Moved {moved_count} posts to job folder {job_folder.name}")
        return moved_count
        
    except Exception as e:
        print(f"❌ Error moving scraped data: {e}")
        return 0

def create_automatic_job_for_scraper_request(scraper_request_id):
    """
    Main function to create automatic job for completed scraper request
    """
    try:
        print(f"🚀 Creating automatic job for scraper request {scraper_request_id}")
        
        # Get the scraper request
        scraper_request = BrightDataScraperRequest.objects.get(id=scraper_request_id)
        print(f"📋 Found scraper request: {scraper_request.platform} - {scraper_request.target_url}")
        
        # Check if it's completed and has data
        if scraper_request.status != 'completed':
            print(f"⚠️ Scraper request not completed (status: {scraper_request.status})")
            return None
        
        scraped_count = BrightDataScrapedPost.objects.filter(scraper_request=scraper_request).count()
        if scraped_count == 0:
            print(f"⚠️ No scraped posts found for this request")
            return None
        
        print(f"📊 Found {scraped_count} scraped posts to organize")
        
        # Get next job number
        job_number = get_next_job_number()
        
        # Create job folder hierarchy
        job_folder = create_job_folder_hierarchy(job_number, scraper_request.platform)
        if not job_folder:
            return None
        
        # Create platform-specific folder
        platform_folder = create_platform_specific_folder(job_folder, scraper_request.platform)
        
        # Move scraped data to job folder
        moved_count = move_scraped_data_to_job_folder(job_folder, platform_folder, scraper_request)
        
        # Update scraper request with job folder reference
        scraper_request.folder_id = job_folder.id
        scraper_request.save()
        
        print(f"🎉 SUCCESS! Created Job {job_number} with {moved_count} posts")
        print(f"🔗 Job folder ID: {job_folder.id}")
        print(f"🌐 Data storage URL: /data-storage/job/{job_number}")
        
        return {
            'job_number': job_number,
            'job_folder_id': job_folder.id,
            'moved_posts': moved_count,
            'data_storage_url': f'/data-storage/job/{job_number}'
        }
        
    except Exception as e:
        print(f"❌ Error creating automatic job: {e}")
        return None

def test_automatic_job_creation():
    """
    Test the automatic job creation with existing scraped data
    """
    print("🧪 Testing automatic job creation...")
    
    # Find a completed scraper request with data
    scraper_requests = BrightDataScraperRequest.objects.filter(
        status='completed'
    ).annotate(
        post_count=models.Count('scraped_posts')
    ).filter(post_count__gt=0)
    
    if scraper_requests.exists():
        test_request = scraper_requests.first()
        print(f"🎯 Testing with scraper request {test_request.id} ({test_request.scraped_posts.count()} posts)")
        
        result = create_automatic_job_for_scraper_request(test_request.id)
        if result:
            print(f"✅ Test successful: {result}")
        else:
            print("❌ Test failed")
    else:
        print("⚠️ No completed scraper requests with data found for testing")

if __name__ == "__main__":
    print("🚀 BRIGHTDATA AUTOMATIC JOB CREATION WORKFLOW")
    print("=" * 50)
    
    test_automatic_job_creation()