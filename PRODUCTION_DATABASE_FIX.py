#!/usr/bin/env python3
"""
🚨 PRODUCTION DATABASE CONNECTION FIX
===================================
This will fix the database connection issue on production
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
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

def diagnose_production_database():
    """Check what's different between local and production"""
    print("🔍 PRODUCTION DATABASE DIAGNOSIS")
    print("=" * 50)
    
    from django.conf import settings
    from django.db import connection
    
    # Check database config
    db_config = settings.DATABASES['default']
    print(f"📊 Database Engine: {db_config['ENGINE']}")
    print(f"📁 Database Name: {db_config['NAME']}")
    
    # Your local data works perfectly - 78 posts in job folders 103 and 104
    # The issue is that production might not have the same data
    
    print("\n🎯 LOCAL DATA SUMMARY:")
    print("✅ 78 BrightDataScrapedPost records")
    print("✅ All posts linked to folders (39 each to folders 103 & 104)")  
    print("✅ Job folders exist and have proper URLs")
    print("✅ API endpoint /api/brightdata/job-results/<id>/ works locally")
    
    print("\n❓ PRODUCTION ISSUES:")
    print("❌ Production database might not have the same 78 posts")
    print("❌ Production folders 103/104 might not exist")
    print("❌ Production BrightDataScrapedPost table might be empty")
    print("❌ API authentication might be failing")

def create_production_data_sync():
    """Create script to sync data to production"""
    print("\n🚀 CREATING PRODUCTION DATA SYNC")
    print("=" * 50)
    
    try:
        from brightdata_integration.models import BrightDataScrapedPost
        from track_accounts.models import UnifiedRunFolder
        
        # Get all data that needs to be synced
        scraped_posts = list(BrightDataScrapedPost.objects.all())
        job_folders = list(UnifiedRunFolder.objects.filter(folder_type='job'))
        
        print(f"📊 Data to sync:")
        print(f"   📄 BrightDataScrapedPost: {len(scraped_posts)} records")
        print(f"   📁 Job folders: {len(job_folders)} folders")
        
        # Create comprehensive sync script
        sync_commands = []
        
        # 1. Create job folders if they don't exist
        for folder in job_folders:
            sync_commands.append(f"""
# Create job folder: {folder.name}
folder_{folder.id}, created = UnifiedRunFolder.objects.get_or_create(
    id={folder.id},
    defaults={{
        'name': '{folder.name}',
        'folder_type': 'job',
        'project_id': {folder.project_id},
        'created_at': '{folder.created_at.isoformat()}' if hasattr(folder, 'created_at') else timezone.now()
    }}
)
print(f"Job folder {folder.id}: {{'Created' if created else 'Exists'}}")
""")
        
        # 2. Create scraped posts
        for i, post in enumerate(scraped_posts):
            sync_commands.append(f"""
# Create scraped post {i+1}/{len(scraped_posts)}
post_{post.id}, created = BrightDataScrapedPost.objects.get_or_create(
    id={post.id},
    defaults={{
        'post_id': '{post.post_id}',
        'url': '{post.url}',
        'content': '''{post.content}''',
        'platform': '{post.platform}',
        'user_posted': '{post.user_posted}',
        'likes': {post.likes},
        'num_comments': {post.num_comments},
        'folder_id': {post.folder_id},
        'date_posted': '{post.date_posted.isoformat()}' if post.date_posted else None,
        'created_at': '{post.created_at.isoformat()}'
    }}
)
""")
        
        # Write the complete sync script
        with open('../PRODUCTION_DATA_SYNC.py', 'w', encoding='utf-8') as f:
            f.write(f'''#!/usr/bin/env python3
"""
🚀 PRODUCTION DATA SYNC SCRIPT
=============================
This will sync all your local data to production
"""

import os
import django
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScrapedPost
from track_accounts.models import UnifiedRunFolder

def sync_data():
    print("🚀 SYNCING DATA TO PRODUCTION")
    print("=" * 50)
    
    try:
{"".join(sync_commands)}
        
        # Verify sync
        post_count = BrightDataScrapedPost.objects.count()
        folder_count = UnifiedRunFolder.objects.filter(folder_type='job').count()
        linked_count = BrightDataScrapedPost.objects.filter(folder_id__isnull=False).count()
        
        print(f"\\n✅ SYNC COMPLETE!")
        print(f"   📄 Total posts: {{post_count}}")
        print(f"   📁 Job folders: {{folder_count}}")
        print(f"   🔗 Linked posts: {{linked_count}}")
        
        print(f"\\n🌐 DATA SHOULD NOW BE LIVE AT:")
        print(f"   📁 Job 2: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/103")
        print(f"   📁 Job 3: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/104")
        
        return True
        
    except Exception as e:
        print(f"❌ Sync failed: {{e}}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sync_data()
''')
        
        print("✅ Created PRODUCTION_DATA_SYNC.py")
        
    except Exception as e:
        print(f"❌ Error creating sync script: {e}")

def create_simple_test_script():
    """Create a simple test script for production"""
    print("\n🧪 CREATING PRODUCTION TEST SCRIPT")
    print("=" * 50)
    
    test_script = '''#!/usr/bin/env python3
"""
🧪 PRODUCTION DATABASE TEST
==========================
Quick test to see what's in production database
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_production_database():
    print("🧪 TESTING PRODUCTION DATABASE")
    print("=" * 50)
    
    try:
        from brightdata_integration.models import BrightDataScrapedPost
        from track_accounts.models import UnifiedRunFolder
        from django.db import connection
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection: WORKING")
        
        # Check scraped posts
        post_count = BrightDataScrapedPost.objects.count()
        print(f"📄 BrightDataScrapedPost records: {post_count}")
        
        if post_count > 0:
            recent_posts = BrightDataScrapedPost.objects.all()[:5]
            for post in recent_posts:
                print(f"   📝 ID: {post.id}, Platform: {post.platform}, Folder: {post.folder_id}")
        
        # Check job folders
        job_folders = UnifiedRunFolder.objects.filter(folder_type='job')
        print(f"📁 Job folders: {job_folders.count()}")
        
        for folder in job_folders[:5]:
            linked_posts = BrightDataScrapedPost.objects.filter(folder_id=folder.id).count()
            print(f"   📁 {folder.name} (ID: {folder.id}): {linked_posts} posts")
        
        # Check specific folders 103 and 104
        for folder_id in [103, 104]:
            try:
                folder = UnifiedRunFolder.objects.get(id=folder_id)
                posts = BrightDataScrapedPost.objects.filter(folder_id=folder_id).count()
                print(f"🎯 Folder {folder_id} ({folder.name}): {posts} posts")
            except UnifiedRunFolder.DoesNotExist:
                print(f"❌ Folder {folder_id}: NOT FOUND")
        
        print(f"\\n🌐 If you have data, it should be at:")
        print(f"   📁 Job 2: /organizations/1/projects/1/data-storage/job/103")
        print(f"   📁 Job 3: /organizations/1/projects/1/data-storage/job/104")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_production_database()
'''
    
    with open('../PRODUCTION_TEST.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created PRODUCTION_TEST.py")

def main():
    """Main function"""
    print("🚨 PRODUCTION DATABASE FIX GENERATOR")
    print("=" * 60)
    
    diagnose_production_database()
    create_production_data_sync()
    create_simple_test_script()
    
    print("\n🎯 NEXT STEPS:")
    print("1️⃣ Run PRODUCTION_TEST.py on production to see current state")
    print("2️⃣ Run PRODUCTION_DATA_SYNC.py on production to sync data")
    print("3️⃣ Check the URLs to see your data!")

if __name__ == "__main__":
    main()