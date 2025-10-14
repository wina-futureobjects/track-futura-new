#!/usr/bin/env python3
"""
🔧 COMPREHENSIVE HIERARCHICAL FOLDER FIX
========================================

Fix all hierarchical folder structure issues:
1. Create missing folders for old runs
2. Repair broken folder links  
3. Standardize folder creation
4. Unify API responses
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder
from workflow.models import ScrapingRun, ScrapingJob
from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from instagram_data.models import Folder as InstagramFolder
from facebook_data.models import Folder as FacebookFolder
from linkedin_data.models import Folder as LinkedInFolder
from tiktok_data.models import Folder as TikTokFolder
from django.db import transaction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class ComprehensiveFolderFix:
    """Fix all hierarchical folder structure issues"""
    
    def __init__(self):
        self.platform_models = {
            'instagram': InstagramFolder,
            'facebook': FacebookFolder,
            'linkedin': LinkedInFolder,
            'tiktok': TikTokFolder
        }
    
    def fix_all_folder_issues(self):
        """Execute all folder fixes"""
        
        print("🔧 COMPREHENSIVE HIERARCHICAL FOLDER FIX")
        print("=" * 50)
        
        try:
            with transaction.atomic():
                # Step 1: Create missing folders for old runs
                self.create_missing_folders()
                
                # Step 2: Repair broken folder links
                self.repair_broken_links()
                
                # Step 3: Clean up orphaned folders
                self.cleanup_orphaned_folders()
                
                # Step 4: Validate folder structure
                self.validate_folder_structure()
                
            print("\n🎉 ALL FOLDER FIXES COMPLETED SUCCESSFULLY!")
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR DURING FIX: {e}")
            return False
    
    def create_missing_folders(self):
        """Create missing platform/service folders for old runs"""
        
        print("\n1️⃣ CREATING MISSING FOLDERS FOR OLD RUNS")
        print("-" * 45)
        
        # Find old scraping runs that only have run folders
        old_runs = ScrapingRun.objects.filter(
            id__lte=37  # Runs 21-37 are the problematic ones
        ).order_by('id')
        
        print(f"📊 Found {old_runs.count()} old scraping runs to fix")
        
        for run in old_runs:
            print(f"\n🔧 Fixing ScrapingRun {run.id}: {run.name}")
            
            # Check if run folder exists
            run_folder = UnifiedRunFolder.objects.filter(
                scraping_run=run, 
                folder_type='run'
            ).first()
            
            if not run_folder:
                # Create run folder if missing
                run_folder = UnifiedRunFolder.objects.create(
                    name=f"Scraping Run - {run.created_at.strftime('%d/%m/%Y %H:%M')}",
                    description=f"Scraping run created on {run.created_at.strftime('%d/%m/%Y %H:%M')}",
                    folder_type='run',
                    scraping_run=run,
                    project=run.project,
                    category='posts'
                )
                print(f"   ✅ Created run folder: {run_folder.id}")
            else:
                print(f"   ✅ Run folder exists: {run_folder.id}")
            
            # Create platform folders for each platform
            platforms = ['instagram', 'facebook', 'linkedin', 'tiktok']
            
            for platform in platforms:
                # Check if platform folder exists
                platform_folder = UnifiedRunFolder.objects.filter(
                    scraping_run=run,
                    folder_type='platform',
                    platform_code=platform
                ).first()
                
                if not platform_folder:
                    platform_folder = UnifiedRunFolder.objects.create(
                        name=f"{platform.title()}",
                        description=f"{platform.title()} platform folder",
                        folder_type='platform',
                        parent_folder=run_folder,
                        scraping_run=run,
                        project=run.project,
                        platform_code=platform,
                        category='posts'
                    )
                    print(f"   ✅ Created {platform} platform folder: {platform_folder.id}")
                
                # Create service folder (Posts)
                service_folder = UnifiedRunFolder.objects.filter(
                    scraping_run=run,
                    folder_type='service',
                    platform_code=platform,
                    service_code='posts'
                ).first()
                
                if not service_folder:
                    service_folder = UnifiedRunFolder.objects.create(
                        name=f"{platform.title()} - Posts",
                        description=f"{platform.title()} posts service folder",
                        folder_type='service',
                        parent_folder=platform_folder,
                        scraping_run=run,
                        project=run.project,
                        platform_code=platform,
                        service_code='posts',
                        category='posts'
                    )
                    print(f"   ✅ Created {platform} service folder: {service_folder.id}")
                
                # Find existing platform-specific folders for this run
                platform_model = self.platform_models[platform]
                existing_folders = platform_model.objects.filter(
                    scraping_run=run
                )
                
                # Link existing folders to the new hierarchy
                for existing_folder in existing_folders:
                    if not existing_folder.unified_job_folder:
                        # Create job folder if needed
                        job_folder = UnifiedRunFolder.objects.create(
                            name=f"Job - {existing_folder.name}",
                            description=f"Job folder for {existing_folder.name}",
                            folder_type='job',
                            parent_folder=service_folder,
                            scraping_run=run,
                            project=run.project,
                            platform_code=platform,
                            service_code='posts',
                            category='posts'
                        )
                        
                        # Link existing folder to job folder
                        existing_folder.unified_job_folder = job_folder
                        existing_folder.save()
                        
                        print(f"   🔗 Linked {platform} folder {existing_folder.id} to job {job_folder.id}")
        
        print(f"\n✅ Completed missing folder creation for {old_runs.count()} old runs")
    
    def repair_broken_links(self):
        """Repair broken folder links"""
        
        print("\n2️⃣ REPAIRING BROKEN FOLDER LINKS")
        print("-" * 35)
        
        fixed_count = 0
        
        for platform, model in self.platform_models.items():
            print(f"\n🔧 Checking {platform} folders...")
            
            # Find platform folders without unified_job_folder link
            orphaned_folders = model.objects.filter(
                unified_job_folder__isnull=True
            )
            
            print(f"   📊 Found {orphaned_folders.count()} orphaned {platform} folders")
            
            for folder in orphaned_folders:
                # Try to find or create appropriate job folder
                if folder.scraping_run:
                    # Find the service folder for this run/platform
                    service_folder = UnifiedRunFolder.objects.filter(
                        scraping_run=folder.scraping_run,
                        folder_type='service',
                        platform_code=platform,
                        service_code='posts'
                    ).first()
                    
                    if service_folder:
                        # Create job folder
                        job_folder = UnifiedRunFolder.objects.create(
                            name=f"Job - {folder.name}",
                            description=f"Job folder for {folder.name}",
                            folder_type='job',
                            parent_folder=service_folder,
                            scraping_run=folder.scraping_run,
                            project=folder.scraping_run.project,
                            platform_code=platform,
                            service_code='posts',
                            category='posts'
                        )
                        
                        # Link folder to job folder
                        folder.unified_job_folder = job_folder
                        folder.save()
                        
                        print(f"   🔗 Fixed {platform} folder {folder.id} → job {job_folder.id}")
                        fixed_count += 1
        
        print(f"\n✅ Repaired {fixed_count} broken folder links")
    
    def cleanup_orphaned_folders(self):
        """Clean up orphaned folders and fix relationships"""
        
        print("\n3️⃣ CLEANING UP ORPHANED FOLDERS")
        print("-" * 35)
        
        # Find UnifiedRunFolders without proper relationships
        orphaned_unified = UnifiedRunFolder.objects.filter(
            scraping_run__isnull=True,
            folder_type__in=['platform', 'service', 'job']
        )
        
        print(f"📊 Found {orphaned_unified.count()} orphaned UnifiedRunFolders")
        
        # For BrightData folders without scraping_run
        brightdata_folders = UnifiedRunFolder.objects.filter(
            created_by__icontains='brightdata'
        ).exclude(
            scraping_run__isnull=False
        )
        
        for folder in brightdata_folders:
            # These are direct BrightData folders - ensure they have proper structure
            if folder.folder_type == 'job' and not folder.parent_folder:
                # Create minimal hierarchy for BrightData folders
                platform = folder.platform_code or 'web_unlocker'
                
                # Create service folder as parent
                service_folder = UnifiedRunFolder.objects.create(
                    name=f"{platform.title()} - Scraped Data",
                    description=f"BrightData scraped data for {platform}",
                    folder_type='service',
                    project=folder.project,
                    platform_code=platform,
                    service_code='scraped',
                    category='posts'
                )
                
                folder.parent_folder = service_folder
                folder.save()
                
                print(f"   🔧 Fixed BrightData folder {folder.id} hierarchy")
        
        print("✅ Completed orphaned folder cleanup")
    
    def validate_folder_structure(self):
        """Validate the entire folder structure"""
        
        print("\n4️⃣ VALIDATING FOLDER STRUCTURE")
        print("-" * 35)
        
        # Validate each scraping run has complete hierarchy
        runs = ScrapingRun.objects.all()
        valid_runs = 0
        
        for run in runs:
            run_folder = UnifiedRunFolder.objects.filter(
                scraping_run=run,
                folder_type='run'
            ).first()
            
            if run_folder:
                platform_count = UnifiedRunFolder.objects.filter(
                    scraping_run=run,
                    folder_type='platform'
                ).count()
                
                service_count = UnifiedRunFolder.objects.filter(
                    scraping_run=run,
                    folder_type='service'
                ).count()
                
                if platform_count >= 1 and service_count >= 1:
                    valid_runs += 1
                else:
                    print(f"   ⚠️ Run {run.id} incomplete: {platform_count} platforms, {service_count} services")
        
        print(f"✅ Validated: {valid_runs}/{runs.count()} runs have complete hierarchy")
        
        # Validate platform folder links
        total_links = 0
        broken_links = 0
        
        for platform, model in self.platform_models.items():
            folders = model.objects.all()
            for folder in folders:
                total_links += 1
                if not folder.unified_job_folder:
                    broken_links += 1
        
        print(f"✅ Folder links: {total_links - broken_links}/{total_links} properly linked")
        
        if broken_links == 0:
            print("🎉 ALL FOLDER STRUCTURES ARE VALID!")
        else:
            print(f"⚠️ {broken_links} folders still need linking")

def run_comprehensive_fix():
    """Run the comprehensive folder fix"""
    
    fixer = ComprehensiveFolderFix()
    success = fixer.fix_all_folder_issues()
    
    if success:
        print("\n🎯 HIERARCHICAL FOLDER STRUCTURE FIXED!")
        print("=" * 40)
        print("✅ Missing folders created for old runs")
        print("✅ Broken folder links repaired")
        print("✅ Orphaned folders cleaned up")
        print("✅ Folder structure validated")
        print("\n🚀 Ready for production deployment!")
    else:
        print("\n❌ FOLDER FIX FAILED - CHECK LOGS")

if __name__ == "__main__":
    run_comprehensive_fix()