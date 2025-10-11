"""
🔍 FOLDER ID ENDPOINT CREATION ANALYSIS
Analyze how folder IDs are created in Workflow Management and connected to Data Storage endpoints
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder, TrackSource
from workflow.models import ScrapingRun, ScrapingJob
from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from users.models import Project, Organization
from django.utils import timezone
import json

def analyze_folder_creation_flow():
    """Analyze the complete folder creation flow from workflow to data storage"""
    
    print("🔍 FOLDER ID ENDPOINT CREATION ANALYSIS")
    print("=" * 80)
    
    # 1. Check current UnifiedRunFolders (these become the endpoints)
    print("\n📁 CURRENT UNIFIED RUN FOLDERS (These become /data-storage/job/{ID} endpoints):")
    print("-" * 60)
    
    unified_folders = UnifiedRunFolder.objects.all().order_by('-created_at')[:20]
    
    for folder in unified_folders:
        print(f"🔗 ID {folder.id}: {folder.name}")
        print(f"   Type: {folder.folder_type}")
        print(f"   Platform: {folder.platform_code}")
        print(f"   Service: {folder.service_code}")
        print(f"   Project: {folder.project_id}")
        print(f"   Created: {folder.created_at}")
        print(f"   📊 Data Storage URL: /organizations/1/projects/1/data-storage/job/{folder.id}")
        print()
    
    # 2. Check how folders are linked to BrightData scraped posts
    print("\n🔗 BRIGHTDATA INTEGRATION - Folder Linking:")
    print("-" * 60)
    
    scraped_posts = BrightDataScrapedPost.objects.values('folder_id').distinct()
    
    print(f"📊 BrightDataScrapedPost records are linked to these folder IDs:")
    for post in scraped_posts:
        folder_id = post['folder_id']
        count = BrightDataScrapedPost.objects.filter(folder_id=folder_id).count()
        
        # Check if this folder exists in UnifiedRunFolder
        unified_exists = UnifiedRunFolder.objects.filter(id=folder_id).exists()
        
        print(f"   Folder {folder_id}: {count} posts (UnifiedRunFolder exists: {unified_exists})")
        
        if unified_exists:
            folder = UnifiedRunFolder.objects.get(id=folder_id)
            print(f"      → Folder Name: {folder.name}")
            print(f"      → Data Storage URL: /organizations/1/projects/1/data-storage/job/{folder_id}")
    
    # 3. Analyze workflow creation process
    print("\n🔄 WORKFLOW CREATION PROCESS:")
    print("-" * 60)
    
    # Check recent scraping runs
    recent_runs = ScrapingRun.objects.all().order_by('-created_at')[:5]
    
    for run in recent_runs:
        print(f"🏃 Scraping Run {run.id}: {run.name}")
        print(f"   Project: {run.project_id}")
        print(f"   Status: {run.status}")
        print(f"   Created: {run.created_at}")
        
        # Check associated UnifiedRunFolders
        associated_folders = UnifiedRunFolder.objects.filter(scraping_run=run)
        print(f"   📁 Associated Folders: {associated_folders.count()}")
        
        for folder in associated_folders:
            print(f"      → {folder.folder_type} folder {folder.id}: {folder.name}")
            
            # Check if this folder has data
            post_count = BrightDataScrapedPost.objects.filter(folder_id=folder.id).count()
            if post_count > 0:
                print(f"         💾 Has {post_count} scraped posts")
                print(f"         🌐 Data Storage URL: /organizations/1/projects/1/data-storage/job/{folder.id}")
        print()
    
    # 4. Check BrightData scraper requests and their folder linking
    print("\n📡 BRIGHTDATA SCRAPER REQUESTS:")
    print("-" * 60)
    
    scraper_requests = BrightDataScraperRequest.objects.all().order_by('-created_at')[:10]
    
    for request in scraper_requests:
        print(f"📡 Request {request.id}: {request.platform}")
        print(f"   Target: {request.target_url}")
        print(f"   Status: {request.status}")
        print(f"   Folder ID: {request.folder_id}")
        print(f"   Snapshot ID: {request.snapshot_id}")
        
        if request.folder_id:
            # Check if this folder_id exists as UnifiedRunFolder
            unified_exists = UnifiedRunFolder.objects.filter(id=request.folder_id).exists()
            print(f"   🔗 UnifiedRunFolder exists: {unified_exists}")
            
            if unified_exists:
                folder = UnifiedRunFolder.objects.get(id=request.folder_id)
                print(f"      → {folder.name}")
                print(f"      → Data Storage URL: /organizations/1/projects/1/data-storage/job/{request.folder_id}")
            
            # Check scraped posts linked to this folder
            post_count = BrightDataScrapedPost.objects.filter(folder_id=request.folder_id).count()
            print(f"   💾 Scraped Posts: {post_count}")
        print()
    
    return True

def analyze_folder_creation_pattern():
    """Analyze the pattern of how folder IDs are created"""
    
    print("\n🔢 FOLDER ID CREATION PATTERN ANALYSIS:")
    print("-" * 60)
    
    # Get all UnifiedRunFolders by creation order
    folders = UnifiedRunFolder.objects.all().order_by('created_at')
    
    print(f"📊 Total UnifiedRunFolders: {folders.count()}")
    
    # Analyze ID patterns
    folder_ids = list(folders.values_list('id', flat=True))
    print(f"🔢 Folder IDs: {folder_ids}")
    
    # Check for gaps or patterns
    if folder_ids:
        min_id = min(folder_ids)
        max_id = max(folder_ids)
        expected_range = list(range(min_id, max_id + 1))
        missing_ids = [id for id in expected_range if id not in folder_ids]
        
        print(f"📈 ID Range: {min_id} to {max_id}")
        if missing_ids:
            print(f"❌ Missing IDs: {missing_ids}")
        else:
            print(f"✅ No missing IDs in range")
    
    # Analyze by folder type
    print(f"\n📂 FOLDERS BY TYPE:")
    folder_types = folders.values('folder_type').distinct()
    
    for folder_type in folder_types:
        type_name = folder_type['folder_type']
        type_folders = folders.filter(folder_type=type_name)
        type_ids = list(type_folders.values_list('id', flat=True))
        
        print(f"   {type_name}: {type_folders.count()} folders (IDs: {type_ids})")
        
        # For job folders, these are the ones that become data storage endpoints
        if type_name == 'job':
            print(f"   🌐 These become /data-storage/job/ID endpoints:")
            for folder in type_folders:
                print(f"      → Job {folder.id}: {folder.name}")
                print(f"         URL: /organizations/1/projects/1/data-storage/job/{folder.id}")

def predict_next_folder_creation():
    """Predict how the next folder creation will work"""
    
    print("\n🔮 NEXT FOLDER CREATION PREDICTION:")
    print("-" * 60)
    
    # Get the latest job folder
    latest_job_folder = UnifiedRunFolder.objects.filter(folder_type='job').order_by('-id').first()
    
    if latest_job_folder:
        next_id = latest_job_folder.id + 1
        print(f"📊 Latest job folder: ID {latest_job_folder.id} - {latest_job_folder.name}")
        print(f"🔮 Next job folder will likely be: ID {next_id}")
        print(f"🌐 Next data storage URL: /organizations/1/projects/1/data-storage/job/{next_id}")
    else:
        print(f"❌ No job folders found")
    
    # Check the BrightData automatic job creation pattern
    print(f"\n🤖 AUTOMATIC JOB CREATION PATTERN:")
    
    # From the services.py analysis, jobs follow a pattern: 181, 184, 188, 191, 194, 198...
    job_folders = UnifiedRunFolder.objects.filter(folder_type='job').order_by('id')
    
    import re
    job_numbers = []
    for folder in job_folders:
        match = re.search(r'(\d+)', folder.name)
        if match:
            job_numbers.append(int(match.group(1)))
    
    if job_numbers:
        print(f"📊 Current job numbers: {job_numbers}")
        
        # Predict next number based on pattern
        max_number = max(job_numbers)
        
        # The pattern from services.py: +3 or +4 increment
        if max_number >= 181:  # Business pattern
            # Pattern: 181, 184, 188, 191, 194, 198...
            position_from_start = max_number - 181
            if position_from_start % 7 in [1, 4]:  # Positions where +4 occurs
                increment = 4
            else:
                increment = 3
            next_number = max_number + increment
        else:
            next_number = max_number + 1
        
        print(f"🔮 Next job number will be: {next_number}")
        print(f"🔮 Folder name: 'Job {next_number}'")
        
        # Find what the actual folder ID will be
        next_folder_id = UnifiedRunFolder.objects.aggregate(models.Max('id'))['id__max'] + 1 if UnifiedRunFolder.objects.exists() else 1
        print(f"🔮 Next folder ID: {next_folder_id}")
        print(f"🌐 Data storage URL: /organizations/1/projects/1/data-storage/job/{next_folder_id}")

def check_data_storage_integration():
    """Check how data storage URLs are integrated"""
    
    print("\n🌐 DATA STORAGE INTEGRATION CHECK:")
    print("-" * 60)
    
    # Test the job-results API endpoints that we know work
    working_folders = [216, 219]  # From user's working URLs
    
    for folder_id in working_folders:
        print(f"✅ Working endpoint: /api/brightdata/job-results/{folder_id}/")
        print(f"   Frontend URL: /organizations/1/projects/1/data-storage/job/{folder_id}")
        
        # Check if folder exists
        folder_exists = UnifiedRunFolder.objects.filter(id=folder_id).exists()
        print(f"   UnifiedRunFolder exists: {folder_exists}")
        
        if folder_exists:
            folder = UnifiedRunFolder.objects.get(id=folder_id)
            print(f"   Folder: {folder.name} ({folder.folder_type})")
        
        # Check scraped data
        post_count = BrightDataScrapedPost.objects.filter(folder_id=folder_id).count()
        print(f"   Scraped posts: {post_count}")
        
        print()

if __name__ == "__main__":
    print("🚀 Starting folder ID endpoint creation analysis...")
    print()
    
    try:
        # Run all analyses
        analyze_folder_creation_flow()
        analyze_folder_creation_pattern()
        predict_next_folder_creation()
        check_data_storage_integration()
        
        print("\n" + "=" * 80)
        print("🎯 KEY FINDINGS:")
        print("1. UnifiedRunFolder IDs become /data-storage/job/{ID} endpoints")
        print("2. BrightData scraped posts link to folder_id")
        print("3. Workflow management creates UnifiedRunFolders with auto-increment IDs")
        print("4. BrightData service creates job folders with business pattern numbers")
        print("5. The job-results API uses folder_id to fetch scraped data")
        print()
        print("💡 INTEGRATION FLOW:")
        print("Workflow → ScrapingRun → UnifiedRunFolder → BrightData scraper → folder_id linking → Data Storage endpoint")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()