import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db.models import Q
from apify_integration.models import ApifyScraperRequest
from track_accounts.models import UnifiedRunFolder
from instagram_data.models import Folder as IGFolder, InstagramPost
from facebook_data.models import Folder as FBFolder, FacebookPost
from datetime import datetime

print("\n=== RECREATING FOLDERS FOR PROJECT 6 ===")

# Get all completed Apify scraper requests
requests = ApifyScraperRequest.objects.filter(
    batch_job__project_id=6,
    status='completed'
).order_by('started_at')

print(f"Found {requests.count()} completed scraper requests")

for req in requests:
    print(f"\n--- Processing Request {req.id} ---")
    print(f"Platform: {req.platform}")
    print(f"Target URL: {req.target_url}")
    print(f"Started: {req.started_at}")

    # Extract username from URL
    target_url = req.target_url or ''
    username = target_url.split('/')[-1] if target_url else ''
    print(f"Username: {username}")

    platform = req.platform

    # Find the unified job folder for this request
    if 'instagram' in platform.lower():
        platform_name = 'Instagram'
        FolderModel = IGFolder
        PostModel = InstagramPost
    elif 'facebook' in platform.lower():
        platform_name = 'Facebook'
        FolderModel = FBFolder
        PostModel = FacebookPost
    else:
        print(f"Unknown platform: {platform}, skipping")
        continue

    # Find unified job folder by matching username in name
    unified_job_folder = None
    if username:
        unified_job_folder = UnifiedRunFolder.objects.filter(
            Q(project_id=6) &
            Q(folder_type='job') &
            Q(name__icontains=platform_name) &
            Q(name__icontains=username)
        ).first()

    if not unified_job_folder:
        # Fallback: find most recent job folder for this platform
        unified_job_folder = UnifiedRunFolder.objects.filter(
            Q(project_id=6) &
            Q(folder_type='job') &
            Q(name__icontains=platform_name)
        ).order_by('-created_at').first()

    if unified_job_folder:
        print(f"Found unified job folder: {unified_job_folder.name} (ID: {unified_job_folder.id})")
    else:
        print(f"WARNING: No unified job folder found!")
        continue

    # Create folder name
    folder_name = f"{platform_name} Scrape - {req.started_at.strftime('%d/%m/%Y %H:%M:%S')}"

    # Create or get folder
    folder, created = FolderModel.objects.get_or_create(
        name=folder_name,
        defaults={
            'project_id': 6,
            'description': f'Results from Apify run {req.request_id}',
            'category': 'posts',
            'folder_type': 'content',
            'unified_job_folder': unified_job_folder
        }
    )

    if created:
        print(f"[+] Created new folder: {folder.name} (ID: {folder.id})")
    else:
        print(f"[+] Found existing folder: {folder.name} (ID: {folder.id})")
        # Update the unified_job_folder link if it wasn't set
        if not folder.unified_job_folder:
            folder.unified_job_folder = unified_job_folder
            folder.save()
            print(f"  Updated unified_job_folder link")

    # Find orphaned posts for this scraper request
    # Match posts by creation time - posts created within 5 minutes of request completion
    orphaned_posts = PostModel.objects.filter(folder__isnull=True)

    if orphaned_posts.exists() and req.completed_at:
        from datetime import timedelta

        # Match posts created within 5 minutes of request completion
        time_window_start = req.completed_at - timedelta(minutes=5)
        time_window_end = req.completed_at + timedelta(minutes=5)

        matched_posts = orphaned_posts.filter(
            created_at__gte=time_window_start,
            created_at__lte=time_window_end
        )

        if matched_posts.exists():
            count = matched_posts.count()
            matched_posts.update(folder=folder)
            print(f"[+] Assigned {count} orphaned posts to folder {folder.id}")
        else:
            print(f"  No matching orphaned posts found in time window")
    elif orphaned_posts.exists() and not req.completed_at:
        # If no completion time, just assign all orphaned posts of this platform
        count = orphaned_posts.count()
        orphaned_posts.update(folder=folder)
        print(f"[+] Assigned {count} orphaned posts to folder {folder.id} (no time filter)")

print("\n\n=== FINAL VERIFICATION ===")

# Check Instagram folders
ig_folders = IGFolder.objects.all().order_by('-created_at')
print(f"\nInstagram Folders: {ig_folders.count()}")
for igf in ig_folders:
    post_count = InstagramPost.objects.filter(folder=igf).count()
    print(f"  Folder {igf.id}: {igf.name}")
    print(f"    Posts: {post_count}")
    print(f"    Unified Job Folder: {igf.unified_job_folder_id}")

# Check Facebook folders
fb_folders = FBFolder.objects.all().order_by('-created_at')
print(f"\nFacebook Folders: {fb_folders.count()}")
for fbf in fb_folders:
    post_count = FacebookPost.objects.filter(folder=fbf).count()
    print(f"  Folder {fbf.id}: {fbf.name}")
    print(f"    Posts: {post_count}")
    print(f"    Unified Job Folder: {fbf.unified_job_folder_id}")

# Check orphaned posts
orphaned_ig = InstagramPost.objects.filter(folder__isnull=True).count()
orphaned_fb = FacebookPost.objects.filter(folder__isnull=True).count()
print(f"\nOrphaned Instagram posts: {orphaned_ig}")
print(f"Orphaned Facebook posts: {orphaned_fb}")
