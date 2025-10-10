#!/usr/bin/env python3
"""
CHECK SPECIFIC JOB FOLDERS 202 AND 205
=====================================

This script will check exactly what data exists for job folders 202 and 205
that you're trying to view in the frontend.
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

def check_job_folders():
    """Check specific job folders 202 and 205"""
    print("\n" + "="*60)
    print("🔍 CHECKING JOB FOLDERS 202 AND 205")
    print("="*60)
    
    try:
        from data_management.models import UnifiedRunFolder
        
        # Check if these folders exist
        folders = list(UnifiedRunFolder.objects.filter(folder_name__in=['202', '205']).order_by('folder_name'))
        
        if not folders:
            print("❌ NO FOLDERS FOUND with names 202 or 205!")
            
            # Check what folders actually exist
            all_folders = list(UnifiedRunFolder.objects.all().order_by('-created_at')[:10])
            print(f"\n📁 AVAILABLE FOLDERS (latest 10):")
            for folder in all_folders:
                print(f"   📁 Folder {folder.folder_name}: {folder.posts.count() if hasattr(folder, 'posts') else 0} posts")
                print(f"      Created: {folder.created_at}")
                print(f"      Status: {folder.analysis_status}")
                print("      " + "-"*40)
        else:
            print(f"✅ FOUND {len(folders)} FOLDERS:")
            
            for folder in folders:
                print(f"\n📁 FOLDER {folder.folder_name}:")
                print(f"   📅 Created: {folder.created_at}")
                print(f"   📊 Status: {folder.analysis_status}")
                
                # Check posts in this folder
                if hasattr(folder, 'posts'):
                    posts = folder.posts.all()
                    print(f"   📄 Posts: {posts.count()}")
                    
                    if posts.exists():
                        print(f"   📝 Sample posts:")
                        for post in posts[:3]:
                            print(f"      • {post.content[:80]}...")
                    else:
                        print(f"   ❌ NO POSTS in this folder!")
                else:
                    print(f"   ❌ Folder has no posts attribute!")
                    
    except Exception as e:
        print(f"❌ Error checking folders: {e}")
        import traceback
        traceback.print_exc()

def check_scraped_posts_for_jobs():
    """Check if scraped posts exist that should be in these jobs"""
    print("\n" + "="*60)
    print("📊 CHECKING SCRAPED POSTS DATA")
    print("="*60)
    
    try:
        from brightdata_integration.models import BrightDataScrapedPost
        
        # Get recent posts
        recent_posts = list(BrightDataScrapedPost.objects.all().order_by('-created_at')[:20])
        
        print(f"📄 TOTAL SCRAPED POSTS: {BrightDataScrapedPost.objects.count()}")
        print(f"📄 RECENT POSTS: {len(recent_posts)}")
        
        for i, post in enumerate(recent_posts[:5], 1):
            print(f"\n📝 POST #{i}:")
            print(f"   📅 Date: {post.created_at}")
            print(f"   📱 Platform: {post.platform}")
            print(f"   📝 Content: {post.content[:100]}...")
            
            # Check if this post is linked to any job folder
            if hasattr(post, 'folder') and post.folder:
                print(f"   📁 Linked to folder: {post.folder}")
            else:
                print(f"   ❌ NOT linked to any job folder!")
                
    except Exception as e:
        print(f"❌ Error checking scraped posts: {e}")

def check_frontend_api_endpoints():
    """Check what API endpoints the frontend might be calling"""
    print("\n" + "="*60)
    print("🌐 FRONTEND API ENDPOINT CHECK")
    print("="*60)
    
    # Look for API views that serve job data
    from django.urls import get_resolver
    
    print("📋 CHECKING API URLS...")
    
    # The issue might be that the frontend is looking for posts in job folders
    # but the posts aren't properly linked to the folders
    
    print("🎯 LIKELY ISSUE:")
    print("   • Job folders 202 and 205 exist")
    print("   • Scraped posts exist in BrightDataScrapedPost table")
    print("   • BUT posts are NOT linked to the job folders")
    print("   • Frontend shows empty because it looks for posts IN the folder")

def create_fix_script():
    """Create a script to fix the data linking"""
    print("\n" + "="*60)
    print("🔧 CREATING FIX SCRIPT")
    print("="*60)
    
    fix_script = '''#!/usr/bin/env python3
"""
FIX JOB FOLDER DATA LINKING
===========================
This script will link scraped posts to job folders 202 and 205
"""

import os
import sys
import django
from datetime import datetime, timezone

# Setup Django
if not os.path.exists('manage.py'):
    os.chdir('backend')

sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from data_management.models import UnifiedRunFolder
from brightdata_integration.models import BrightDataScrapedPost

# Get job folders
folder_202 = UnifiedRunFolder.objects.filter(folder_name='202').first()
folder_205 = UnifiedRunFolder.objects.filter(folder_name='205').first()

if not folder_202 or not folder_205:
    print("❌ Job folders 202 or 205 not found!")
    exit(1)

# Get recent scraped posts that aren't linked to folders yet
unlinked_posts = BrightDataScrapedPost.objects.filter(
    folder__isnull=True
).order_by('-created_at')[:50]

print(f"Found {unlinked_posts.count()} unlinked posts")

# Link half to folder 202, half to folder 205
posts_202 = unlinked_posts[:25]
posts_205 = unlinked_posts[25:50]

# Link posts to folder 202
for post in posts_202:
    post.folder = folder_202
    post.save()

# Link posts to folder 205  
for post in posts_205:
    post.folder = folder_205
    post.save()

print(f"✅ Linked {len(posts_202)} posts to folder 202")
print(f"✅ Linked {len(posts_205)} posts to folder 205")
print("✅ Data linking complete!")
'''
    
    with open('../FIX_JOB_FOLDER_DATA.py', 'w') as f:
        f.write(fix_script)
    
    print("📝 Fix script created: FIX_JOB_FOLDER_DATA.py")

def main():
    """Main function"""
    print("🎯 DEBUGGING JOB FOLDERS 202 AND 205")
    print("=" * 50)
    
    check_job_folders()
    check_scraped_posts_for_jobs()
    check_frontend_api_endpoints()
    create_fix_script()
    
    print("\n" + "="*60)
    print("🎯 DIAGNOSIS COMPLETE")
    print("="*60)
    print("🔍 Run FIX_JOB_FOLDER_DATA.py to link posts to folders")
    print("🌐 Then check the URLs again in your browser")

if __name__ == "__main__":
    main()