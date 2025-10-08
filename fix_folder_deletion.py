
# Fix for UnifiedRunFolder deletion
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from track_accounts.models import UnifiedRunFolder
from rest_framework.response import Response
from rest_framework import status

print("=== FOLDER DELETION FIX ===")

# Get all failed/problematic folders
failed_folders = UnifiedRunFolder.objects.filter(folder_type="job").order_by("-created_at")
print(f"Found {failed_folders.count()} job folders")

# Show details of failed folders
for folder in failed_folders[:10]:  # Show first 10
    print(f"  - {folder.name} (ID: {folder.id})")
    print(f"    Type: {folder.folder_type}, Platform: {folder.platform_code}")
    print(f"    Created: {folder.created_at}")
    
    # Check if folder has associated platform folders
    platform_folder_count = 0
    
    if folder.platform_code == "instagram":
        from instagram_data.models import Folder as InstagramFolder
        platform_folder_count = InstagramFolder.objects.filter(unified_job_folder=folder).count()
    elif folder.platform_code == "facebook":
        from facebook_data.models import Folder as FacebookFolder
        platform_folder_count = FacebookFolder.objects.filter(unified_job_folder=folder).count()
    elif folder.platform_code == "linkedin":
        from linkedin_data.models import Folder as LinkedInFolder
        platform_folder_count = LinkedInFolder.objects.filter(unified_job_folder=folder).count()
    elif folder.platform_code == "tiktok":
        from tiktok_data.models import Folder as TikTokFolder
        platform_folder_count = TikTokFolder.objects.filter(unified_job_folder=folder).count()
    
    print(f"    Platform folders: {platform_folder_count}")

print("\nFolder analysis complete!")

# Create a cleanup function that can be called
def cleanup_failed_folders():
    """Clean up failed folders that are blocking deletion"""
    
    # Find folders that are likely failed (no associated posts and old)
    from datetime import datetime, timedelta
    cutoff_date = datetime.now() - timedelta(hours=2)  # 2 hours old with no data
    
    failed_candidates = UnifiedRunFolder.objects.filter(
        folder_type="job",
        created_at__lt=cutoff_date
    )
    
    cleaned_count = 0
    
    for folder in failed_candidates:
        try:
            # Check if folder has any posts
            has_posts = False
            
            if folder.platform_code == "instagram":
                from instagram_data.models import Folder as InstagramFolder, InstagramPost
                platform_folders = InstagramFolder.objects.filter(unified_job_folder=folder)
                for pf in platform_folders:
                    if InstagramPost.objects.filter(folder=pf).exists():
                        has_posts = True
                        break
                        
            elif folder.platform_code == "facebook":
                from facebook_data.models import Folder as FacebookFolder, FacebookPost
                platform_folders = FacebookFolder.objects.filter(unified_job_folder=folder)
                for pf in platform_folders:
                    if FacebookPost.objects.filter(folder=pf).exists():
                        has_posts = True
                        break
            
            # If no posts, it's likely a failed folder
            if not has_posts:
                print(f"Cleaning failed folder: {folder.name}")
                folder.delete()
                cleaned_count += 1
                
        except Exception as e:
            print(f"Error processing folder {folder.id}: {str(e)}")
    
    print(f"Cleaned up {cleaned_count} failed folders")

# Run the cleanup
cleanup_failed_folders()

print("Fix complete!")
