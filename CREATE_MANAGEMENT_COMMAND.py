#!/usr/bin/env python3
"""
DJANGO MANAGEMENT COMMAND - COMPREHENSIVE FOLDER FIX
===================================================

This creates a Django management command to fix hierarchical folder structure issues.
"""

import os
from pathlib import Path

def create_management_command():
    """Create Django management command for folder fix"""
    
    # Create management command directory structure
    management_dir = Path(r"C:\Users\winam\OneDrive\문서\PREVIOUS\TrackFutura - Copy\track_accounts\management")
    commands_dir = management_dir / "commands"
    
    management_dir.mkdir(exist_ok=True)
    commands_dir.mkdir(exist_ok=True)
    
    # Create __init__.py files
    (management_dir / "__init__.py").touch()
    (commands_dir / "__init__.py").touch()
    
    # Create management command
    command_content = '''#!/usr/bin/env python3
"""
Django Management Command: Comprehensive Folder Structure Fix
===========================================================

Usage: python manage.py fix_folder_hierarchy
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from track_accounts.models import UnifiedRunFolder
from instagram_data.models import InstagramFolder
from facebook_data.models import FacebookFolder
from linkedin_data.models import LinkedInFolder
from tiktok_data.models import TikTokFolder
from brightdata_integration.models import BrightDataScrapedPost
from collections import defaultdict


class Command(BaseCommand):
    help = 'Fix hierarchical folder structure issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed progress information',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.verbose = options['verbose']
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 DRY RUN MODE - No changes will be made')
            )
        
        try:
            with transaction.atomic():
                self.fix_missing_unified_folders()
                self.fix_broken_folder_links()
                self.fix_orphaned_folders()
                self.validate_hierarchy()
                
                if self.dry_run:
                    # Rollback in dry run mode
                    transaction.set_rollback(True)
                    
            if not self.dry_run:
                self.stdout.write(
                    self.style.SUCCESS('✅ Comprehensive folder fix completed successfully!')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ Dry run completed - use without --dry-run to apply changes')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during folder fix: {str(e)}')
            )
            raise

    def fix_missing_unified_folders(self):
        """Create missing UnifiedRunFolder entries for old runs"""
        self.stdout.write('🔧 Fixing missing unified run folders...')
        
        # Get runs that should have unified folders but don't
        old_runs = list(range(21, 38))  # Runs 21-37
        
        missing_runs = []
        for run_id in old_runs:
            if not UnifiedRunFolder.objects.filter(scraping_run=run_id, folder_type='run').exists():
                missing_runs.append(run_id)
        
        if self.verbose:
            self.stdout.write(f'Found {len(missing_runs)} missing run folders: {missing_runs}')
        
        created_count = 0
        for run_id in missing_runs:
            if not self.dry_run:
                UnifiedRunFolder.objects.create(
                    name=f'Scraping Run #{run_id}',
                    description=f'Automatically created run folder for run {run_id}',
                    folder_type='run',
                    scraping_run=run_id,
                    project_id=2  # Your project ID
                )
            created_count += 1
        
        self.stdout.write(f'  ✅ {"Would create" if self.dry_run else "Created"} {created_count} missing run folders')

    def fix_broken_folder_links(self):
        """Fix broken unified_job_folder links in platform folders"""
        self.stdout.write('🔧 Fixing broken folder links...')
        
        platform_models = [
            ('Instagram', InstagramFolder),
            ('Facebook', FacebookFolder), 
            ('LinkedIn', LinkedInFolder),
            ('TikTok', TikTokFolder)
        ]
        
        total_fixed = 0
        
        for platform_name, model in platform_models:
            # Find folders with broken unified_job_folder links
            broken_folders = model.objects.filter(
                unified_job_folder_id__isnull=False
            ).exclude(
                unified_job_folder_id__in=UnifiedRunFolder.objects.values_list('id', flat=True)
            )
            
            if self.verbose and broken_folders.exists():
                self.stdout.write(f'  Found {broken_folders.count()} broken {platform_name} folder links')
            
            for folder in broken_folders:
                # Try to find or create appropriate job folder
                job_folder = None
                
                # Look for existing job folder for this run and platform
                if folder.scraping_run:
                    job_folder = UnifiedRunFolder.objects.filter(
                        scraping_run=folder.scraping_run,
                        folder_type='job',
                        platform_code=platform_name.lower()
                    ).first()
                    
                    # Create job folder if it doesn't exist
                    if not job_folder and not self.dry_run:
                        # First ensure run folder exists
                        run_folder, _ = UnifiedRunFolder.objects.get_or_create(
                            scraping_run=folder.scraping_run,
                            folder_type='run',
                            defaults={
                                'name': f'Scraping Run #{folder.scraping_run}',
                                'description': f'Run folder for run {folder.scraping_run}',
                                'project_id': 2
                            }
                        )
                        
                        # Create job folder
                        job_folder = UnifiedRunFolder.objects.create(
                            name=f'{platform_name} Job - Run #{folder.scraping_run}',
                            description=f'{platform_name} job folder for run {folder.scraping_run}',
                            folder_type='job',
                            scraping_run=folder.scraping_run,
                            platform_code=platform_name.lower(),
                            parent_folder=run_folder,
                            project_id=2
                        )
                
                # Update the broken link
                if job_folder and not self.dry_run:
                    folder.unified_job_folder = job_folder
                    folder.save(update_fields=['unified_job_folder'])
                    
                total_fixed += 1
        
        self.stdout.write(f'  ✅ {"Would fix" if self.dry_run else "Fixed"} {total_fixed} broken folder links')

    def fix_orphaned_folders(self):
        """Clean up orphaned unified folders"""
        self.stdout.write('🔧 Fixing orphaned folders...')
        
        # Find job folders without parent run folders
        orphaned_jobs = UnifiedRunFolder.objects.filter(
            folder_type='job',
            parent_folder__isnull=True,
            scraping_run__isnull=False
        )
        
        fixed_count = 0
        for job in orphaned_jobs:
            # Find or create parent run folder
            run_folder, created = UnifiedRunFolder.objects.get_or_create(
                scraping_run=job.scraping_run,
                folder_type='run',
                defaults={
                    'name': f'Scraping Run #{job.scraping_run}',
                    'description': f'Parent run folder for run {job.scraping_run}',
                    'project_id': job.project_id or 2
                }
            )
            
            if not self.dry_run:
                job.parent_folder = run_folder
                job.save(update_fields=['parent_folder'])
            
            fixed_count += 1
        
        if self.verbose and fixed_count > 0:
            self.stdout.write(f'  Found {fixed_count} orphaned job folders')
        
        self.stdout.write(f'  ✅ {"Would fix" if self.dry_run else "Fixed"} {fixed_count} orphaned job folders')

    def validate_hierarchy(self):
        """Validate the folder hierarchy structure"""
        self.stdout.write('🔍 Validating folder hierarchy...')
        
        # Count folders by type
        run_count = UnifiedRunFolder.objects.filter(folder_type='run').count()
        job_count = UnifiedRunFolder.objects.filter(folder_type='job').count()
        
        # Count platform folders with valid links
        platform_models = [
            ('Instagram', InstagramFolder),
            ('Facebook', FacebookFolder),
            ('LinkedIn', LinkedInFolder), 
            ('TikTok', TikTokFolder)
        ]
        
        linked_platform_folders = 0
        orphaned_platform_folders = 0
        
        for platform_name, model in platform_models:
            linked = model.objects.filter(unified_job_folder__isnull=False).count()
            orphaned = model.objects.filter(unified_job_folder__isnull=True).count()
            
            linked_platform_folders += linked
            orphaned_platform_folders += orphaned
            
            if self.verbose:
                self.stdout.write(f'  {platform_name}: {linked} linked, {orphaned} orphaned')
        
        # Count BrightData posts
        brightdata_count = BrightDataScrapedPost.objects.count()
        
        self.stdout.write(f'  📊 Hierarchy Summary:')
        self.stdout.write(f'     • Run folders: {run_count}')
        self.stdout.write(f'     • Job folders: {job_count}') 
        self.stdout.write(f'     • Linked platform folders: {linked_platform_folders}')
        self.stdout.write(f'     • Orphaned platform folders: {orphaned_platform_folders}')
        self.stdout.write(f'     • BrightData posts: {brightdata_count}')
        
        # Validation checks
        issues = []
        
        if orphaned_platform_folders > 0:
            issues.append(f'{orphaned_platform_folders} platform folders without unified links')
            
        if job_count == 0 and linked_platform_folders > 0:
            issues.append('Platform folders linked but no job folders exist')
        
        if issues:
            self.stdout.write('  ⚠️  Validation Issues:')
            for issue in issues:
                self.stdout.write(f'     • {issue}')
        else:
            self.stdout.write('  ✅ No validation issues found')
'''
    
    command_file = commands_dir / "fix_folder_hierarchy.py"
    with open(command_file, 'w', encoding='utf-8') as f:
        f.write(command_content)
    
    print(f"✅ Created management command: {command_file}")
    
    return command_file

if __name__ == "__main__":
    create_management_command()