import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from instagram_data.models import InstagramPost, Folder
from track_accounts.models import UnifiedRunFolder
from apify_integration.models import ApifyScraperRequest, ApifyBatchJob

print("=" * 80)
print("FIXING INSTAGRAM FOLDER LINKS")
print("=" * 80)

# Get orphaned Instagram posts
orphaned_posts = InstagramPost.objects.filter(folder__isnull=True)
print(f"\nFound {orphaned_posts.count()} orphaned Instagram posts")

# Get the Apify requests for Instagram
instagram_requests = ApifyScraperRequest.objects.filter(
    platform__startswith='instagram',
    batch_job__project_id=6
).order_by('created_at')

print(f"\nFound {instagram_requests.count()} Instagram scraper requests for project 6:")
for req in instagram_requests:
    print(f"  Request ID {req.id}: {req.platform}, Batch {req.batch_job_id}, Status: {req.status}")
    batch_job = req.batch_job
    print(f"    Batch Job: {batch_job.name}")

    # Find the corresponding unified job folder from the batch job's job_folder field
    unified_job_folder = None
    if hasattr(batch_job, 'job_folder') and batch_job.job_folder:
        unified_job_folder = batch_job.job_folder
        print(f"    Found unified job folder from batch: ID {unified_job_folder.id}: {unified_job_folder.name}")
    else:
        # Try to find by looking for job folders with matching platform
        job_folders = UnifiedRunFolder.objects.filter(
            project_id=6,
            folder_type='job',
            name__icontains='Instagram'
        ).order_by('-created_at')

        print(f"    Found {job_folders.count()} unified job folders for Instagram:")
        for jf in job_folders:
            print(f"      - ID {jf.id}: {jf.name}")

        if job_folders.exists():
            unified_job_folder = job_folders.first()

    # Get or create Instagram folder linked to unified job folder
    if unified_job_folder:

        # Create Instagram folder name with source folder names + date/time
        from track_accounts.models import SourceFolder
        source_folder_names = []
        if batch_job.source_folder_ids:
            source_folders = SourceFolder.objects.filter(id__in=batch_job.source_folder_ids)
            source_folder_names = [sf.name for sf in source_folders]

        if source_folder_names:
            folder_base_name = ", ".join(source_folder_names)
        else:
            folder_base_name = "Instagram Scrape"

        folder_name = f"{folder_base_name} - {req.started_at.strftime('%d/%m/%Y %H:%M:%S')}"

        # Create or get Instagram folder
        instagram_folder, created = Folder.objects.get_or_create(
            name=folder_name,
            project_id=6,
            defaults={
                'description': f'Results from Apify run {req.request_id}',
                'category': 'posts',
                'folder_type': 'content',
                'unified_job_folder': unified_job_folder
            }
        )

        if created:
            print(f"\n  [OK] Created Instagram folder: {folder_name} (ID {instagram_folder.id})")
            print(f"    Linked to unified job folder: {unified_job_folder.name} (ID {unified_job_folder.id})")
        else:
            print(f"\n  [OK] Found existing Instagram folder: {folder_name} (ID {instagram_folder.id})")
            # Update unified job folder link if missing
            if not instagram_folder.unified_job_folder:
                instagram_folder.unified_job_folder = unified_job_folder
                instagram_folder.save()
                print(f"    Updated link to unified job folder: {unified_job_folder.name}")

        # Assign ALL orphaned posts to this folder (since they belong to this batch)
        if orphaned_posts.exists():
            updated = orphaned_posts.update(folder=instagram_folder)
            print(f"    Assigned {updated} posts to this folder")
            orphaned_posts = InstagramPost.objects.filter(folder__isnull=True)  # Refresh query

print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

# Verify Instagram folders now have unified_job_folder links
instagram_folders = Folder.objects.filter(project_id=6)
print(f"\nInstagram folders for project 6:")
for folder in instagram_folders:
    print(f"  ID {folder.id}: {folder.name}")
    print(f"    Unified Job Folder: {folder.unified_job_folder_id} ({folder.unified_job_folder.name if folder.unified_job_folder else 'None'})")
    print(f"    Post Count: {folder.get_content_count()}")

# Check remaining orphaned posts
remaining_orphaned = InstagramPost.objects.filter(folder__isnull=True)
print(f"\nRemaining orphaned posts: {remaining_orphaned.count()}")

print("\n" + "=" * 80)
