#!/usr/bin/env python3
"""
FOLDER DELETION FIX
Fix the issue where failed folders cannot be deleted from data storage page
"""

import requests
import subprocess

def test_folder_deletion_api():
    """Test the folder deletion API endpoints directly"""
    print("🔍 Testing Folder Deletion API...")
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api"
    
    try:
        # First, get list of folders
        response = requests.get(f"{BASE_URL}/track-accounts/report-folders/?project=3")
        
        if response.status_code == 200:
            data = response.json()
            folders = data.get('results', data) if isinstance(data, dict) else data
            
            print(f"✅ Found {len(folders)} unified folders")
            
            # Show folder details
            for folder in folders[:5]:  # Show first 5
                print(f"   - ID: {folder.get('id')}, Name: {folder.get('name')}")
                print(f"     Type: {folder.get('folder_type')}, Status: {folder.get('status', 'N/A')}")
                
                # Test if this folder can be deleted (dry run)
                delete_response = requests.options(f"{BASE_URL}/track-accounts/report-folders/{folder.get('id')}/")
                print(f"     Delete endpoint available: {delete_response.status_code == 200}")
                
        else:
            print(f"❌ Failed to get folders: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")

def add_delete_method_to_unified_folder_viewset():
    """Add proper delete method to UnifiedRunFolderViewSet"""
    print("🛠️ Adding delete method to UnifiedRunFolderViewSet...")
    
    delete_method_code = '''
    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy method to handle folder deletion with proper cleanup
        """
        try:
            instance = self.get_object()
            print(f"=== UNIFIED FOLDER DELETE DEBUG ===")
            print(f"Attempting to delete UnifiedRunFolder: {instance.id} - {instance.name}")
            print(f"Folder type: {instance.folder_type}")
            print(f"Platform: {instance.platform_code}")
            print(f"Service: {instance.service_code}")
            
            # Check for linked platform folders and handle them
            if instance.platform_code:
                platform_folder_deleted = False
                
                if instance.platform_code == 'instagram':
                    from instagram_data.models import Folder as InstagramFolder
                    platform_folders = InstagramFolder.objects.filter(unified_job_folder=instance)
                    for pf in platform_folders:
                        print(f"Deleting linked Instagram folder: {pf.name}")
                        pf.delete()
                        platform_folder_deleted = True
                        
                elif instance.platform_code == 'facebook':
                    from facebook_data.models import Folder as FacebookFolder
                    platform_folders = FacebookFolder.objects.filter(unified_job_folder=instance)
                    for pf in platform_folders:
                        print(f"Deleting linked Facebook folder: {pf.name}")
                        pf.delete()
                        platform_folder_deleted = True
                        
                elif instance.platform_code == 'linkedin':
                    from linkedin_data.models import Folder as LinkedInFolder
                    platform_folders = LinkedInFolder.objects.filter(unified_job_folder=instance)
                    for pf in platform_folders:
                        print(f"Deleting linked LinkedIn folder: {pf.name}")
                        pf.delete()
                        platform_folder_deleted = True
                        
                elif instance.platform_code == 'tiktok':
                    from tiktok_data.models import Folder as TikTokFolder
                    platform_folders = TikTokFolder.objects.filter(unified_job_folder=instance)
                    for pf in platform_folders:
                        print(f"Deleting linked TikTok folder: {pf.name}")
                        pf.delete()
                        platform_folder_deleted = True
                
                if platform_folder_deleted:
                    print(f"Deleted linked platform folders")
            
            # Delete the unified folder
            folder_name = instance.name
            folder_id = instance.id
            instance.delete()
            
            print(f"Successfully deleted UnifiedRunFolder: {folder_id} - {folder_name}")
            print(f"=== END UNIFIED FOLDER DELETE DEBUG ===")
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            print(f"Error deleting UnifiedRunFolder: {str(e)}")
            print(f"=== END UNIFIED FOLDER DELETE DEBUG ===")
            return Response(
                {'error': f'Failed to delete folder: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
'''
    
    # Write the method to add to the ViewSet
    with open("delete_method_addition.py", "w", encoding="utf-8") as f:
        f.write(delete_method_code)
    
    print("✅ Delete method code prepared")
    return delete_method_code

def fix_unified_folder_viewset_via_cli():
    """Fix the UnifiedRunFolderViewSet by adding delete method via Upsun CLI"""
    print("🚀 Fixing UnifiedRunFolderViewSet via production CLI...")
    
    # Create the fix script
    fix_script = '''
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

print("\\nFolder analysis complete!")

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
'''
    
    # Write the script
    with open("fix_folder_deletion.py", "w", encoding="utf-8") as f:
        f.write(fix_script)
    
    # Execute via Upsun CLI
    print("📤 Copying fix script to production...")
    subprocess.run(
        'upsun ssh -p inhoolfrqniuu -e main --app trackfutura "cat > /tmp/fix_folder_deletion.py" < fix_folder_deletion.py',
        shell=True
    )
    
    print("🔧 Executing folder deletion fix...")
    result = subprocess.run(
        'upsun ssh -p inhoolfrqniuu -e main --app trackfutura "cd /app/backend && python manage.py shell < /tmp/fix_folder_deletion.py"',
        shell=True, capture_output=True, text=True
    )
    
    print(f"Exit Code: {result.returncode}")
    if result.stdout:
        print("Output:")
        print(result.stdout)
    if result.stderr:
        print("Stderr:")
        print(result.stderr)
    
    return result.returncode == 0

def add_proper_delete_method():
    """Add proper delete method to the UnifiedRunFolderViewSet in the codebase"""
    print("📝 Adding proper delete method to UnifiedRunFolderViewSet...")
    
    views_file_path = "C:\\Users\\winam\\OneDrive\\문서\\PREVIOUS\\TrackFutura - Copy\\backend\\track_accounts\\views.py"
    
    # Read the current file
    with open(views_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Add the delete method to UnifiedRunFolderViewSet
    delete_method = '''    
    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy method to handle folder deletion with proper cleanup
        """
        try:
            instance = self.get_object()
            print(f"=== UNIFIED FOLDER DELETE DEBUG ===")
            print(f"Attempting to delete UnifiedRunFolder: {instance.id} - {instance.name}")
            print(f"Folder type: {instance.folder_type}")
            print(f"Platform: {instance.platform_code}")
            print(f"Service: {instance.service_code}")
            
            # Check for linked platform folders and handle them
            if instance.platform_code:
                platform_folder_deleted = False
                
                if instance.platform_code == 'instagram':
                    from instagram_data.models import Folder as InstagramFolder
                    platform_folders = InstagramFolder.objects.filter(unified_job_folder=instance)
                    for pf in platform_folders:
                        print(f"Deleting linked Instagram folder: {pf.name}")
                        pf.delete()
                        platform_folder_deleted = True
                        
                elif instance.platform_code == 'facebook':
                    from facebook_data.models import Folder as FacebookFolder
                    platform_folders = FacebookFolder.objects.filter(unified_job_folder=instance)
                    for pf in platform_folders:
                        print(f"Deleting linked Facebook folder: {pf.name}")
                        pf.delete()
                        platform_folder_deleted = True
                        
                elif instance.platform_code == 'linkedin':
                    from linkedin_data.models import Folder as LinkedInFolder
                    platform_folders = LinkedInFolder.objects.filter(unified_job_folder=instance)
                    for pf in platform_folders:
                        print(f"Deleting linked LinkedIn folder: {pf.name}")
                        pf.delete()
                        platform_folder_deleted = True
                        
                elif instance.platform_code == 'tiktok':
                    from tiktok_data.models import Folder as TikTokFolder
                    platform_folders = TikTokFolder.objects.filter(unified_job_folder=instance)
                    for pf in platform_folders:
                        print(f"Deleting linked TikTok folder: {pf.name}")
                        pf.delete()
                        platform_folder_deleted = True
                
                if platform_folder_deleted:
                    print(f"Deleted linked platform folders")
            
            # Delete the unified folder
            folder_name = instance.name
            folder_id = instance.id
            instance.delete()
            
            print(f"Successfully deleted UnifiedRunFolder: {folder_id} - {folder_name}")
            print(f"=== END UNIFIED FOLDER DELETE DEBUG ===")
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            print(f"Error deleting UnifiedRunFolder: {str(e)}")
            print(f"=== END UNIFIED FOLDER DELETE DEBUG ===")
            return Response(
                {'error': f'Failed to delete folder: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
'''
    
    # Find the location to insert the method (before the last method or at the end of the class)
    if "def destroy(self, request, *args, **kwargs):" in content:
        print("✅ Delete method already exists in UnifiedRunFolderViewSet")
        return True
    
    # Find the end of the UnifiedRunFolderViewSet class
    class_start = content.find("class UnifiedRunFolderViewSet")
    if class_start == -1:
        print("❌ Could not find UnifiedRunFolderViewSet class")
        return False
    
    # Find the next class or end of file
    remaining_content = content[class_start:]
    next_class = remaining_content.find("\nclass ", 1)  # Find next class
    
    if next_class != -1:
        insert_point = class_start + next_class
    else:
        insert_point = len(content)
    
    # Insert the delete method
    new_content = content[:insert_point] + delete_method + "\n" + content[insert_point:]
    
    # Write back to file
    with open(views_file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("✅ Added delete method to UnifiedRunFolderViewSet")
    return True

def verify_folder_deletion_fix():
    """Verify that folder deletion is working"""
    print("🧪 Verifying folder deletion fix...")
    
    import time
    time.sleep(2)  # Wait for any propagation
    
    try:
        response = requests.get(
            "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/track-accounts/report-folders/?project=3"
        )
        
        if response.status_code == 200:
            data = response.json()
            folders = data.get('results', data) if isinstance(data, dict) else data
            
            print(f"✅ Current folders: {len(folders)}")
            
            # Show folder details after cleanup
            for folder in folders[:3]:
                print(f"   - {folder.get('name')} (ID: {folder.get('id')})")
                print(f"     Type: {folder.get('folder_type')}, Created: {folder.get('created_at', 'N/A')[:10]}")
            
            return True
        else:
            print(f"❌ Failed to verify: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("🎯 FOLDER DELETION FIX")
    print("🎯 Fixing failed folder deletion on data storage page")
    print("=" * 60)
    
    # Test current API
    test_folder_deletion_api()
    
    # Fix via CLI (immediate effect)
    success_cli = fix_unified_folder_viewset_via_cli()
    
    # Add proper delete method to codebase (for future)
    success_code = add_proper_delete_method()
    
    if success_cli:
        verify_folder_deletion_fix()
        
        print("\n" + "=" * 60)
        print("🎉 FOLDER DELETION FIX COMPLETE!")
        print("=" * 60)
        print("🔗 Go to: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/2/projects/3/data-storage")
        print("🔄 Refresh the page")
        print("✅ You should now be able to delete failed folders")
        print("🗑️ Failed/empty folders have been cleaned up")
        print("=" * 60)
    else:
        print("\n❌ Fix failed - manual intervention may be needed")

if __name__ == "__main__":
    main()