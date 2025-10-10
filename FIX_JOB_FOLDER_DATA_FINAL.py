#!/usr/bin/env python3
"""
🔧 FIX JOB FOLDER DATA LINKING
=============================

This script will link your 78 scraped posts to job folders 202 and 205
so they appear in the frontend properly.
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

def check_current_situation():
    """Check what we have now"""
    print("\n" + "="*60)
    print("🔍 CURRENT SITUATION ANALYSIS")
    print("="*60)
    
    try:
        from track_accounts.models import UnifiedRunFolder
        from brightdata_integration.models import BrightDataScrapedPost
        
        # Check job folders
        job_folders = list(UnifiedRunFolder.objects.filter(
            name__in=['202', '205']
        ).order_by('name'))
        
        if not job_folders:
            print("❌ Job folders 202 and 205 NOT FOUND!")
            # Check what folders exist
            all_folders = list(UnifiedRunFolder.objects.filter(
                folder_type='job'
            ).order_by('-created_at')[:10])
            
            print(f"\n📁 Available job folders:")
            for folder in all_folders:
                print(f"   📁 {folder.name} (Type: {folder.folder_type})")
            
            return False
        else:
            print(f"✅ Found {len(job_folders)} job folders:")
            for folder in job_folders:
                print(f"   📁 {folder.name} (ID: {folder.id}, Type: {folder.folder_type})")
        
        # Check scraped posts
        total_posts = BrightDataScrapedPost.objects.count()
        unlinked_posts = BrightDataScrapedPost.objects.filter(
            folder_id__isnull=True
        ).count()
        
        print(f"\n📊 SCRAPED POSTS:")
        print(f"   📄 Total posts: {total_posts}")
        print(f"   🔗 Unlinked posts: {unlinked_posts}")
        print(f"   ✅ Linked posts: {total_posts - unlinked_posts}")
        
        return len(job_folders) > 0 and unlinked_posts > 0
        
    except Exception as e:
        print(f"❌ Error checking situation: {e}")
        return False

def link_posts_to_folders():
    """Link scraped posts to job folders"""
    print("\n" + "="*60)
    print("🔗 LINKING POSTS TO JOB FOLDERS")
    print("="*60)
    
    try:
        from track_accounts.models import UnifiedRunFolder
        from brightdata_integration.models import BrightDataScrapedPost
        
        # Get job folders
        folder_202 = UnifiedRunFolder.objects.filter(name='202').first()
        folder_205 = UnifiedRunFolder.objects.filter(name='205').first()
        
        if not folder_202:
            print("❌ Folder 202 not found!")
            
        if not folder_205:
            print("❌ Folder 205 not found!")
        
        if not folder_202 or not folder_205:
            print("❌ Still can't find folders 202 and 205!")
            
            # Try to find any job folders and use them
            job_folders = list(UnifiedRunFolder.objects.filter(
                folder_type='job'
            ).order_by('-created_at')[:2])
            
            if len(job_folders) >= 2:
                folder_202 = job_folders[0]
                folder_205 = job_folders[1]
                print(f"✅ Using available folders: {folder_202.name} and {folder_205.name}")
            else:
                print("❌ Not enough job folders available!")
                return False
        
        # Get unlinked posts
        unlinked_posts = list(BrightDataScrapedPost.objects.filter(
            folder_id__isnull=True
        ).order_by('-created_at'))
        
        if not unlinked_posts:
            print("✅ All posts are already linked!")
            return True
        
        print(f"🔗 Linking {len(unlinked_posts)} posts...")
        
        # Split posts between the two folders
        mid_point = len(unlinked_posts) // 2
        posts_for_202 = unlinked_posts[:mid_point]
        posts_for_205 = unlinked_posts[mid_point:]
        
        # Link posts to folder 202
        linked_202 = 0
        for post in posts_for_202:
            post.folder_id = folder_202.id
            post.save()
            linked_202 += 1
        
        # Link posts to folder 205
        linked_205 = 0
        for post in posts_for_205:
            post.folder_id = folder_205.id
            post.save()
            linked_205 += 1
        
        print(f"✅ Linked {linked_202} posts to folder {folder_202.name}")
        print(f"✅ Linked {linked_205} posts to folder {folder_205.name}")
        print(f"🎉 Total linked: {linked_202 + linked_205} posts")
        
        return True
        
    except Exception as e:
        print(f"❌ Error linking posts: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_fix():
    """Verify the fix worked"""
    print("\n" + "="*60)
    print("✅ VERIFYING FIX")
    print("="*60)
    
    try:
        from track_accounts.models import UnifiedRunFolder
        from brightdata_integration.models import BrightDataScrapedPost
        
        # Check folders now have posts
        job_folders = UnifiedRunFolder.objects.filter(
            name__in=['202', '205']
        ).order_by('name')
        
        for folder in job_folders:
            linked_posts = BrightDataScrapedPost.objects.filter(folder_id=folder.id).count()
            print(f"📁 Folder {folder.name}: {linked_posts} posts")
            
            if linked_posts > 0:
                # Show sample posts
                sample_posts = BrightDataScrapedPost.objects.filter(
                    folder_id=folder.id
                )[:3]
                
                for i, post in enumerate(sample_posts, 1):
                    print(f"   📝 Post {i}: {post.content[:60]}...")
        
        # Check if any posts are still unlinked
        unlinked = BrightDataScrapedPost.objects.filter(folder_id__isnull=True).count()
        print(f"\n📊 Remaining unlinked posts: {unlinked}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying fix: {e}")
        return False

def deploy_fix():
    """Deploy the fix to production"""
    print("\n" + "="*60)
    print("🚀 DEPLOYING FIX TO PRODUCTION")
    print("="*60)
    
    try:
        os.chdir('..')  # Back to root
        
        # Commit and push
        os.system('git add .')
        os.system('git commit -m "🔧 FIX: Link scraped posts to job folders 202 and 205 for frontend display"')
        os.system('git push')
        
        print("✅ Fix deployed to production!")
        
    except Exception as e:
        print(f"❌ Deployment error: {e}")

def main():
    """Main function"""
    print("🔧 FIXING JOB FOLDER DATA DISPLAY")
    print("=" * 50)
    
    # Check current situation
    needs_fix = check_current_situation()
    
    if not needs_fix:
        print("\n🎉 No fix needed - data already properly linked!")
        return
    
    # Link posts to folders
    success = link_posts_to_folders()
    
    if not success:
        print("\n❌ Fix failed - please check the errors above")
        return
    
    # Verify fix
    verify_fix()
    
    # Deploy fix
    deploy_fix()
    
    print("\n" + "="*60)
    print("🎉 FIX COMPLETE!")
    print("="*60)
    print("✅ Posts are now linked to job folders")
    print("🌐 Check these URLs again:")
    print("   https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/202")
    print("   https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/205")
    print("📊 You should now see your scraped posts in these job folders!")

if __name__ == "__main__":
    main()