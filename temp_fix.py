from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from track_accounts.models import UnifiedRunFolder  
from users.models import Project

# Get Project 2
try:
    project = Project.objects.get(id=2)
    print("Found Project 2:", project.name)
except Project.DoesNotExist:
    print("Project 2 not found, using Project 1")
    project = Project.objects.get(id=1)

# Process your snapshots
snapshots = ["s_mgp6kcyu28lbyl8rx9", "s_mgp6kclbi353dgcjk"]

for snapshot_id in snapshots:
    print(f"Processing {snapshot_id}")
    
    # Get or create scraper request
    scraper_request, created = BrightDataScraperRequest.objects.get_or_create(
        snapshot_id=snapshot_id,
        defaults={
            "platform": "facebook" if "kcyu" in snapshot_id else "instagram",  
            "status": "completed",
            "target_url": "https://brightdata.com"
        }
    )
    
    if created:
        print(f"  Created scraper request {scraper_request.id}")
    else:
        print(f"  Found existing request {scraper_request.id}")
    
    # Check if job folder exists
    if scraper_request.folder_id:
        folder_exists = UnifiedRunFolder.objects.filter(id=scraper_request.folder_id).exists()
        if folder_exists:
            folder = UnifiedRunFolder.objects.get(id=scraper_request.folder_id)
            print(f"  Job folder exists: {folder.name} (ID {folder.id})")
            continue
    
    # Create job folder
    existing_jobs = UnifiedRunFolder.objects.filter(
        project=project,
        folder_type="job",
        name__startswith="BrightData"
    ).count()
    job_number = existing_jobs + 1
    
    job_folder = UnifiedRunFolder.objects.create(
        name=f"BrightData Job {job_number} ({snapshot_id})",
        project=project,
        folder_type="job",
        platform_code="facebook" if "kcyu" in snapshot_id else "instagram",
        service_code="brightdata"
    )
    
    print(f"  Created job folder: {job_folder.name} (ID {job_folder.id})")
    
    # Link scraper request
    scraper_request.folder_id = job_folder.id
    scraper_request.save()
    
    # Update scraped posts
    posts_updated = BrightDataScrapedPost.objects.filter(
        scraper_request=scraper_request
    ).update(folder_id=job_folder.id)
    
    print(f"  Linked {posts_updated} posts to folder")
    print(f"  Data Storage URL: /organizations/1/projects/2/data-storage/job/{job_folder.id}")

print("DONE! Your snapshots should now appear in data storage.")