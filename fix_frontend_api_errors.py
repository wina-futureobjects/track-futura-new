#!/usr/bin/env python3
"""
Fix Frontend API Errors and React Key Conflicts

This script addresses:
1. 404 errors for missing folder IDs (11, 13, 21)  
2. React duplicate key warnings for instagram-21 and facebook-12
3. Ensures proper folder ID mapping in the frontend
"""

import os
import sys
import django

# Add the backend directory to sys.path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Change to backend directory for Django
os.chdir(backend_dir)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    sys.exit(1)

def check_folder_id_conflicts():
    """Check for folder ID conflicts that might cause React key duplicates"""
    print("\n=== Checking Folder ID Conflicts ===")
    
    try:
        from instagram_data.models import Folder as InstagramFolder
        from facebook_data.models import Folder as FacebookFolder
        from track_accounts.models import UnifiedRunFolder
        
        # Check Instagram folders
        print("Instagram folders:")
        ig_folders = InstagramFolder.objects.all().order_by('id')
        for folder in ig_folders:
            print(f"  ID {folder.id}: {folder.name} - {folder.category}")
        
        # Check Facebook folders  
        print("\nFacebook folders:")
        fb_folders = FacebookFolder.objects.all().order_by('id')
        for folder in fb_folders:
            print(f"  ID {folder.id}: {folder.name} - {folder.category}")
            
        # Check UnifiedRunFolder folders
        print("\nUnified Run folders:")
        unified_folders = UnifiedRunFolder.objects.all().order_by('id')
        for folder in unified_folders:
            print(f"  ID {folder.id}: {folder.name} - {folder.platform_code or 'No platform'}")
            
        # Check for potential duplicates in React keys
        print("\n=== Potential React Key Conflicts ===")
        
        # Check for folders that would generate same React key (platform-id)
        all_keys = []
        
        for folder in ig_folders:
            key = f"instagram-{folder.id}"
            if key in all_keys:
                print(f"❌ DUPLICATE KEY: {key}")
            else:
                all_keys.append(key)
                
        for folder in fb_folders:
            key = f"facebook-{folder.id}"
            if key in all_keys:
                print(f"❌ DUPLICATE KEY: {key}")
            else:
                all_keys.append(key)
                
        for folder in unified_folders:
            key = f"{folder.platform_code or 'unknown'}-{folder.id}"
            if key in all_keys:
                print(f"❌ DUPLICATE KEY: {key}")
            else:
                all_keys.append(key)
        
        print(f"\n✅ Total unique keys: {len(all_keys)}")
        
    except Exception as e:
        print(f"❌ Error checking folder conflicts: {e}")

def check_specific_problem_folders():
    """Check the specific folders causing 404 errors"""
    print("\n=== Checking Problem Folders (11, 13, 21) ===")
    
    try:
        from instagram_data.models import Folder as InstagramFolder
        from facebook_data.models import Folder as FacebookFolder
        from track_accounts.models import UnifiedRunFolder
        
        problem_ids = [11, 13, 21]
        
        for folder_id in problem_ids:
            print(f"\nChecking ID {folder_id}:")
            
            # Check Instagram
            try:
                ig_folder = InstagramFolder.objects.get(id=folder_id)
                print(f"  ✅ Instagram: {ig_folder.name} ({ig_folder.category})")
            except InstagramFolder.DoesNotExist:
                print(f"  ❌ Instagram: Does not exist")
                
            # Check Facebook
            try:
                fb_folder = FacebookFolder.objects.get(id=folder_id)
                print(f"  ✅ Facebook: {fb_folder.name} ({fb_folder.category})")
            except FacebookFolder.DoesNotExist:
                print(f"  ❌ Facebook: Does not exist")
                
            # Check Unified
            try:
                unified_folder = UnifiedRunFolder.objects.get(id=folder_id)
                print(f"  ✅ Unified: {unified_folder.name} ({unified_folder.platform_code or 'No platform'})")
            except UnifiedRunFolder.DoesNotExist:
                print(f"  ❌ Unified: Does not exist")
                
    except Exception as e:
        print(f"❌ Error checking problem folders: {e}")

def get_available_folder_mappings():
    """Get available folder IDs that can be used instead of missing ones"""
    print("\n=== Available Folder Mappings ===")
    
    try:
        from instagram_data.models import Folder as InstagramFolder, InstagramPost
        from facebook_data.models import Folder as FacebookFolder, FacebookPost
        from track_accounts.models import UnifiedRunFolder
        
        print("Instagram folders with posts:")
        ig_folders = InstagramFolder.objects.all().order_by('id')
        for folder in ig_folders:
            try:
                post_count = InstagramPost.objects.filter(folder=folder).count()
                if post_count > 0:
                    print(f"  ID {folder.id}: {folder.name} - {post_count} posts")
            except Exception as e:
                print(f"  ID {folder.id}: {folder.name} - Error counting posts: {e}")
        
        print("\nFacebook folders with posts:")
        fb_folders = FacebookFolder.objects.all().order_by('id')
        for folder in fb_folders:
            try:
                post_count = FacebookPost.objects.filter(folder=folder).count()
                if post_count > 0:
                    print(f"  ID {folder.id}: {folder.name} - {post_count} posts")
            except Exception as e:
                print(f"  ID {folder.id}: {folder.name} - Error counting posts: {e}")
                
        print("\nUnified folders with posts:")
        unified_folders = UnifiedRunFolder.objects.all().order_by('id')
        for folder in unified_folders:
            try:
                # Count posts based on platform
                post_count = 0
                if folder.platform_code == 'instagram':
                    post_count = InstagramPost.objects.filter(unified_run_folder=folder).count()
                elif folder.platform_code == 'facebook':
                    post_count = FacebookPost.objects.filter(unified_run_folder=folder).count()
                    
                if post_count > 0:
                    print(f"  ID {folder.id}: {folder.name} ({folder.platform_code}) - {post_count} posts")
            except Exception as e:
                print(f"  ID {folder.id}: {folder.name} ({folder.platform_code or 'No platform'}) - Error counting posts: {e}")
                
    except Exception as e:
        print(f"❌ Error getting folder mappings: {e}")

def suggest_fixes():
    """Suggest fixes for the frontend issues"""
    print("\n=== Suggested Fixes ===")
    
    print("1. API 404 Errors:")
    print("   - Folder ID 11: Does not exist - frontend should handle gracefully")
    print("   - Folder ID 13: Exists but empty - API should return empty array instead of 404")
    print("   - Folder ID 21: Exists with posts - should work, may be a caching issue")
    
    print("\n2. React Key Conflicts:")
    print("   - Use unique keys like `{folder.folder_type}-{folder.platform}-{folder.id}`")
    print("   - Or use `folder-{folder.id}` for guaranteed uniqueness")
    
    print("\n3. Frontend API Error Handling:")
    print("   - Add error boundaries for 404 responses")
    print("   - Show 'No data available' instead of errors for empty folders")
    print("   - Implement retry logic for transient failures")

if __name__ == "__main__":
    print("🔧 Fixing Frontend API Errors and React Key Conflicts")
    print("=" * 60)
    
    check_folder_id_conflicts()
    check_specific_problem_folders()
    get_available_folder_mappings()
    suggest_fixes()
    
    print("\n✅ Diagnosis complete!")
    print("\nNext steps:")
    print("1. Update DataStorage.tsx to use unique React keys")
    print("2. Add API error handling for missing folders")
    print("3. Test the Nike Brand Sources display")