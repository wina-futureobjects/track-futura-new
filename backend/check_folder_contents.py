import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder
from instagram_data.models import Folder as IGFolder, InstagramPost
from facebook_data.models import Folder as FBFolder, FacebookPost

print("\n=== UNIFIED RUN FOLDERS (PROJECT 6) ===")
run_folders = UnifiedRunFolder.objects.filter(project_id=6, folder_type='run').order_by('-created_at')
for rf in run_folders:
    print(f"\nRun Folder: {rf.name} (ID: {rf.id})")

    # Get platform folders under this run
    platform_folders = UnifiedRunFolder.objects.filter(parent_folder=rf, folder_type='platform')
    for pf in platform_folders:
        print(f"  Platform: {pf.name} (ID: {pf.id})")

        # Get service folders under this platform
        service_folders = UnifiedRunFolder.objects.filter(parent_folder=pf, folder_type='service')
        for sf in service_folders:
            print(f"    Service: {sf.name} (ID: {sf.id})")

            # Get job folders under this service
            job_folders = UnifiedRunFolder.objects.filter(parent_folder=sf, folder_type='job')
            for jf in job_folders:
                print(f"      Job: {jf.name} (ID: {jf.id})")

                # Check Instagram folders linked to this job
                ig_folders = IGFolder.objects.filter(unified_job_folder=jf)
                print(f"        Instagram folders linked: {ig_folders.count()}")
                for igf in ig_folders:
                    post_count = InstagramPost.objects.filter(folder=igf).count()
                    print(f"          - {igf.name} (ID: {igf.id}): {post_count} posts")

                # Check Facebook folders linked to this job
                fb_folders = FBFolder.objects.filter(unified_job_folder=jf)
                print(f"        Facebook folders linked: {fb_folders.count()}")
                for fbf in fb_folders:
                    post_count = FacebookPost.objects.filter(folder=fbf).count()
                    print(f"          - {fbf.name} (ID: {fbf.id}): {post_count} posts")

print("\n\n=== ALL INSTAGRAM FOLDERS (PROJECT 6) ===")
ig_folders_all = IGFolder.objects.filter(project_id=6).order_by('-created_at')
for igf in ig_folders_all:
    post_count = InstagramPost.objects.filter(folder=igf).count()
    unified_link = igf.unified_job_folder_id if hasattr(igf, 'unified_job_folder_id') else None
    print(f"Instagram Folder {igf.id}: {igf.name}")
    print(f"  Posts: {post_count}")
    print(f"  Unified Job Folder ID: {unified_link}")
    if unified_link:
        ujf = UnifiedRunFolder.objects.get(id=unified_link)
        print(f"  Unified Job Folder Name: {ujf.name}")

print("\n\n=== ALL FACEBOOK FOLDERS (PROJECT 6) ===")
fb_folders_all = FBFolder.objects.filter(project_id=6).order_by('-created_at')
for fbf in fb_folders_all:
    post_count = FacebookPost.objects.filter(folder=fbf).count()
    unified_link = fbf.unified_job_folder_id if hasattr(fbf, 'unified_job_folder_id') else None
    print(f"Facebook Folder {fbf.id}: {fbf.name}")
    print(f"  Posts: {post_count}")
    print(f"  Unified Job Folder ID: {unified_link}")
    if unified_link:
        ujf = UnifiedRunFolder.objects.get(id=unified_link)
        print(f"  Unified Job Folder Name: {ujf.name}")
