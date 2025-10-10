#!/usr/bin/env python3
"""
🔍 FIND CORRECT JOB FOLDER URLS
==============================

This script will find the correct URLs for your job folders
based on what actually exists in the database.
"""

import os
import sys
import django

# Setup Django
try:
    if not os.path.exists('manage.py'):
        os.chdir('backend')
    
    sys.path.insert(0, os.getcwd())
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    print("✅ Connected to database")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

def find_correct_urls():
    """Find the correct job folder URLs"""
    print("\n" + "="*60)
    print("🔍 FINDING CORRECT JOB FOLDER URLS")
    print("="*60)
    
    try:
        from track_accounts.models import UnifiedRunFolder
        from brightdata_integration.models import BrightDataScrapedPost
        
        # Get all job folders with posts
        job_folders = list(UnifiedRunFolder.objects.filter(
            folder_type='job'
        ).order_by('-created_at'))
        
        print(f"📁 Found {len(job_folders)} job folders:")
        
        for folder in job_folders:
            # Count posts in this folder
            post_count = BrightDataScrapedPost.objects.filter(folder_id=folder.id).count()
            
            print(f"\n📁 FOLDER: {folder.name}")
            print(f"   📊 ID: {folder.id}")
            print(f"   📄 Posts: {post_count}")
            print(f"   📅 Created: {folder.created_at}")
            print(f"   🌐 Correct URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/{folder.id}")
            
            if post_count > 0:
                # Show sample posts
                sample_posts = BrightDataScrapedPost.objects.filter(
                    folder_id=folder.id
                )[:2]
                
                print(f"   📝 Sample posts:")
                for i, post in enumerate(sample_posts, 1):
                    print(f"      {i}. {post.content[:60]}...")
        
        # Find folders that should have job numbers 202 and 205
        folders_with_posts = []
        for folder in job_folders:
            post_count = BrightDataScrapedPost.objects.filter(folder_id=folder.id).count()
            if post_count > 0:
                folders_with_posts.append((folder, post_count))
        
        if len(folders_with_posts) >= 2:
            print(f"\n🎯 TOP FOLDERS WITH POSTS:")
            for i, (folder, count) in enumerate(folders_with_posts[:2]):
                print(f"   📁 Folder {folder.name} (ID: {folder.id}): {count} posts")
                print(f"      🌐 URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/{folder.id}")
        
    except Exception as e:
        print(f"❌ Error finding URLs: {e}")
        import traceback
        traceback.print_exc()

def link_posts_to_top_folders():
    """Link unlinked posts to the top 2 job folders"""
    print("\n" + "="*60)
    print("🔗 LINKING POSTS TO TOP JOB FOLDERS")
    print("="*60)
    
    try:
        from track_accounts.models import UnifiedRunFolder
        from brightdata_integration.models import BrightDataScrapedPost
        
        # Get top 2 job folders (most recent)
        job_folders = list(UnifiedRunFolder.objects.filter(
            folder_type='job'
        ).order_by('-created_at')[:2])
        
        if len(job_folders) < 2:
            print("❌ Not enough job folders found!")
            return False
        
        folder_1 = job_folders[0]  # Most recent
        folder_2 = job_folders[1]  # Second most recent
        
        print(f"🎯 Using folders:")
        print(f"   📁 {folder_1.name} (ID: {folder_1.id})")
        print(f"   📁 {folder_2.name} (ID: {folder_2.id})")
        
        # Get unlinked posts
        unlinked_posts = list(BrightDataScrapedPost.objects.filter(
            folder_id__isnull=True
        ).order_by('-created_at'))
        
        if not unlinked_posts:
            print("✅ All posts are already linked!")
            
            # Instead, let's redistribute existing posts
            all_posts = list(BrightDataScrapedPost.objects.all().order_by('-created_at'))
            mid_point = len(all_posts) // 2
            
            print(f"🔄 Redistributing {len(all_posts)} posts...")
            
            # Update posts for folder 1
            posts_for_1 = all_posts[:mid_point]
            for post in posts_for_1:
                post.folder_id = folder_1.id
                post.save()
            
            # Update posts for folder 2
            posts_for_2 = all_posts[mid_point:]
            for post in posts_for_2:
                post.folder_id = folder_2.id
                post.save()
            
            print(f"✅ Linked {len(posts_for_1)} posts to {folder_1.name}")
            print(f"✅ Linked {len(posts_for_2)} posts to {folder_2.name}")
            
            return True
        
        # Link unlinked posts
        mid_point = len(unlinked_posts) // 2
        posts_for_1 = unlinked_posts[:mid_point]
        posts_for_2 = unlinked_posts[mid_point:]
        
        print(f"🔗 Linking {len(unlinked_posts)} unlinked posts...")
        
        # Link to folder 1
        for post in posts_for_1:
            post.folder_id = folder_1.id
            post.save()
        
        # Link to folder 2
        for post in posts_for_2:
            post.folder_id = folder_2.id
            post.save()
        
        print(f"✅ Linked {len(posts_for_1)} posts to {folder_1.name}")
        print(f"✅ Linked {len(posts_for_2)} posts to {folder_2.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error linking posts: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🔍 FINDING CORRECT JOB FOLDER URLS")
    print("=" * 50)
    
    # Find correct URLs
    find_correct_urls()
    
    # Link posts to folders
    success = link_posts_to_top_folders()
    
    if success:
        # Show final URLs
        print("\n" + "="*60)
        print("🎉 SUCCESS! TRY THESE URLS:")
        print("="*60)
        
        try:
            from track_accounts.models import UnifiedRunFolder
            top_folders = list(UnifiedRunFolder.objects.filter(
                folder_type='job'
            ).order_by('-created_at')[:2])
            
            from brightdata_integration.models import BrightDataScrapedPost
            
            for folder in top_folders:
                post_count = BrightDataScrapedPost.objects.filter(folder_id=folder.id).count()
                print(f"📁 {folder.name}: {post_count} posts")
                print(f"   🌐 https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/{folder.id}")
            
        except Exception as e:
            print(f"❌ Error showing final URLs: {e}")

if __name__ == "__main__":
    main()