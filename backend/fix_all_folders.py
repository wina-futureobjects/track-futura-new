import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from instagram_data.models import InstagramPost, Folder as IGFolder
from facebook_data.models import FacebookPost, Folder as FBFolder
from track_accounts.models import UnifiedRunFolder, SourceFolder
from apify_integration.models import ApifyScraperRequest

print("=" * 80)
print("FIXING ALL PLATFORM FOLDERS FOR PROJECT 6")
print("=" * 80)

# Get all Apify requests for project 6
requests = ApifyScraperRequest.objects.filter(
    batch_job__project_id=6
).order_by('created_at')

for req in requests:
    print(f"\nProcessing Request {req.id}: {req.platform}")
    print(f"  Run ID: {req.request_id}")
    print(f"  Target: {req.target_url}")
    print(f"  Status: {req.status}")

    batch_job = req.batch_job

    # Get source folder names
    source_folder_names = []
    if batch_job.source_folder_ids:
        source_folders = SourceFolder.objects.filter(id__in=batch_job.source_folder_ids)
        source_folder_names = [sf.name for sf in source_folders]

    if source_folder_names:
        folder_base_name = ", ".join(source_folder_names)
    else:
        folder_base_name = f"{req.platform.split('_')[0].title()} Scrape"

    folder_name = f"{folder_base_name} - {req.started_at.strftime('%d/%m/%Y %H:%M:%S')}"

    # Find unified job folder by username
    target_url = req.target_url or ''
    username = target_url.split('/')[-1] if target_url else ''

    platform_name = req.platform.split('_')[0].title()  # 'instagram' -> 'Instagram'

    unified_job_folder = None
    if username:
        # Use Q objects to combine multiple icontains filters
        from django.db.models import Q
        unified_job_folder = UnifiedRunFolder.objects.filter(
            Q(project_id=6) &
            Q(folder_type='job') &
            Q(name__icontains=platform_name) &
            Q(name__icontains=username)
        ).first()

    if not unified_job_folder:
        unified_job_folder = UnifiedRunFolder.objects.filter(
            project_id=6,
            folder_type='job',
            name__icontains=platform_name
        ).order_by('-created_at').first()

    if unified_job_folder:
        print(f"  Found unified job folder: {unified_job_folder.name} (ID {unified_job_folder.id})")

    # Create or get folder based on platform
    if req.platform.startswith('instagram'):
        folder, created = IGFolder.objects.get_or_create(
            name=folder_name,
            project_id=6,
            defaults={
                'description': f'Results from Apify run {req.request_id}',
                'category': 'posts',
                'folder_type': 'content',
                'unified_job_folder': unified_job_folder
            }
        )

        if not created and not folder.unified_job_folder and unified_job_folder:
            folder.unified_job_folder = unified_job_folder
            folder.save()

        # Count and assign orphaned Instagram posts
        orphaned_ig = InstagramPost.objects.filter(folder__isnull=True)
        if orphaned_ig.exists():
            # For now, assign all orphaned to this folder
            # In production, you'd match by username or other criteria
            pass  # Already done in previous script

        print(f"  [OK] Instagram folder: {folder.name} (ID {folder.id})")
        print(f"      Posts in folder: {InstagramPost.objects.filter(folder_id=folder.id).count()}")

    elif req.platform.startswith('facebook'):
        folder, created = FBFolder.objects.get_or_create(
            name=folder_name,
            project_id=6,
            defaults={
                'description': f'Results from Apify run {req.request_id}',
                'category': 'posts',
                'folder_type': 'content',
                'unified_job_folder': unified_job_folder
            }
        )

        if not created and not folder.unified_job_folder and unified_job_folder:
            folder.unified_job_folder = unified_job_folder
            folder.save()

        # Assign orphaned Facebook posts to this folder
        # Match posts by checking if user_posted contains the username
        orphaned_fb = FacebookPost.objects.filter(folder__isnull=True)

        # Extract username from user_posted JSON field
        posts_assigned = 0
        for post in orphaned_fb:
            user_data = post.user_posted
            if isinstance(user_data, dict):
                profile_url = user_data.get('profileUrl', '')
                if username and username.lower() in profile_url.lower():
                    post.folder = folder
                    post.save()
                    posts_assigned += 1
            elif isinstance(user_data, str) and username and username.lower() in user_data.lower():
                post.folder = folder
                post.save()
                posts_assigned += 1

        if created:
            print(f"  [OK] Created Facebook folder: {folder.name} (ID {folder.id})")
        else:
            print(f"  [OK] Found Facebook folder: {folder.name} (ID {folder.id})")

        if posts_assigned > 0:
            print(f"      Assigned {posts_assigned} posts to this folder")
        print(f"      Total posts in folder: {FacebookPost.objects.filter(folder_id=folder.id).count()}")

print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

print("\nInstagram Folders:")
ig_folders = IGFolder.objects.filter(project_id=6)
for f in ig_folders:
    post_count = InstagramPost.objects.filter(folder_id=f.id).count()
    print(f"  ID {f.id}: {f.name}")
    print(f"    Unified Job: {f.unified_job_folder_id} ({f.unified_job_folder.name if f.unified_job_folder else 'None'})")
    print(f"    Posts: {post_count}")

print("\nFacebook Folders:")
fb_folders = FBFolder.objects.filter(project_id=6)
for f in fb_folders:
    post_count = FacebookPost.objects.filter(folder_id=f.id).count()
    print(f"  ID {f.id}: {f.name}")
    print(f"    Unified Job: {f.unified_job_folder_id} ({f.unified_job_folder.name if f.unified_job_folder else 'None'})")
    print(f"    Posts: {post_count}")

orphaned_ig = InstagramPost.objects.filter(folder__isnull=True).count()
orphaned_fb = FacebookPost.objects.filter(folder__isnull=True).count()
print(f"\nRemaining orphaned Instagram posts: {orphaned_ig}")
print(f"Remaining orphaned Facebook posts: {orphaned_fb}")

print("\n" + "=" * 80)
