#!/usr/bin/env python3
"""
🔍 DATABASE INSPECTION TOOL
===========================
Let's inspect the database structure and see where your scraped data is!
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

def inspect_database_config():
    """Check database configuration"""
    print("🗄️ DATABASE CONFIGURATION")
    print("=" * 50)
    
    from django.conf import settings
    from django.db import connection
    
    db_settings = settings.DATABASES['default']
    print(f"📊 Database Engine: {db_settings['ENGINE']}")
    print(f"📁 Database Name: {db_settings['NAME']}")
    
    if 'HOST' in db_settings:
        print(f"🌐 Database Host: {db_settings['HOST']}")
    if 'PORT' in db_settings:
        print(f"🔌 Database Port: {db_settings['PORT']}")
    
    # Test connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection: WORKING")
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
    
    return True

def inspect_scraped_data_tables():
    """Check scraped data tables and content"""
    print("\n📊 SCRAPED DATA TABLES")
    print("=" * 50)
    
    try:
        from brightdata_integration.models import BrightDataScrapedPost
        from django.db import connection
        
        # Check BrightData scraped posts
        scraped_count = BrightDataScrapedPost.objects.count()
        print(f"📄 BrightDataScrapedPost table: {scraped_count} records")
        
        if scraped_count > 0:
            print("\n📋 Sample data:")
            recent_posts = BrightDataScrapedPost.objects.all()[:5]
            for post in recent_posts:
                print(f"   📝 ID: {post.id}, Platform: {post.platform}, Folder: {getattr(post, 'folder_id', 'None')}")
                print(f"      URL: {post.url[:50]}..." if post.url else "      URL: No URL")
                print(f"      Content: {post.content[:50]}..." if post.content else "      Content: No content")
        
        # Check folder assignments
        linked_posts = BrightDataScrapedPost.objects.filter(folder_id__isnull=False).count()
        unlinked_posts = BrightDataScrapedPost.objects.filter(folder_id__isnull=True).count()
        
        print(f"\n🔗 Data linking status:")
        print(f"   ✅ Linked to folders: {linked_posts}")
        print(f"   ❌ Unlinked: {unlinked_posts}")
        
        return scraped_count > 0
        
    except Exception as e:
        print(f"❌ Error checking scraped data: {e}")
        return False

def inspect_job_folders():
    """Check job folders structure"""
    print("\n📁 JOB FOLDERS STRUCTURE")
    print("=" * 50)
    
    try:
        from track_accounts.models import UnifiedRunFolder
        
        job_folders = UnifiedRunFolder.objects.filter(folder_type='job').order_by('-created_at')
        print(f"📋 Total job folders: {job_folders.count()}")
        
        for folder in job_folders[:10]:  # Show first 10
            print(f"   📁 {folder.name} (ID: {folder.id})")
            
            # Check how many posts are linked to this folder
            from brightdata_integration.models import BrightDataScrapedPost
            linked_posts = BrightDataScrapedPost.objects.filter(folder_id=folder.id).count()
            print(f"      📊 Linked posts: {linked_posts}")
            
            # Show data storage URL
            print(f"      🌐 Data URL: /organizations/1/projects/1/data-storage/job/{folder.id}")
        
        return job_folders.count() > 0
        
    except Exception as e:
        print(f"❌ Error checking job folders: {e}")
        return False

def inspect_platform_data():
    """Check platform-specific data tables"""
    print("\n🌐 PLATFORM-SPECIFIC DATA TABLES")
    print("=" * 50)
    
    platform_counts = {}
    
    try:
        # Check Instagram data
        from instagram_data.models import InstagramPost
        insta_count = InstagramPost.objects.count()
        platform_counts['Instagram'] = insta_count
        print(f"📸 Instagram posts: {insta_count}")
        
        # Check Facebook data
        from facebook_data.models import FacebookPost
        fb_count = FacebookPost.objects.count()
        platform_counts['Facebook'] = fb_count
        print(f"📘 Facebook posts: {fb_count}")
        
        # Check LinkedIn data
        try:
            from linkedin_data.models import LinkedInPost
            li_count = LinkedInPost.objects.count()
            platform_counts['LinkedIn'] = li_count
            print(f"💼 LinkedIn posts: {li_count}")
        except:
            print("💼 LinkedIn: Module not available")
        
        # Check TikTok data
        try:
            from tiktok_data.models import TikTokPost
            tt_count = TikTokPost.objects.count()
            platform_counts['TikTok'] = tt_count
            print(f"🎵 TikTok posts: {tt_count}")
        except:
            print("🎵 TikTok: Module not available")
        
        return platform_counts
        
    except Exception as e:
        print(f"❌ Error checking platform data: {e}")
        return {}

def inspect_api_endpoints():
    """Check what API endpoints the frontend calls"""
    print("\n🔗 API ENDPOINTS FOR DATA STORAGE")
    print("=" * 50)
    
    print("📋 The data storage page calls these endpoints:")
    print("   🎯 /api/brightdata/job-results/<folder_id>/")
    print("   🎯 /api/instagram-data/posts/?folder=<folder_id>")
    print("   🎯 /api/facebook-data/posts/?folder=<folder_id>")
    print("   🎯 /api/linkedin-data/posts/?folder=<folder_id>")
    print("   🎯 /api/tiktok-data/posts/?folder=<folder_id>")
    
    # Test the main BrightData endpoint locally
    try:
        import requests
        url = "http://localhost:8000/api/brightdata/job-results/103/"
        print(f"\n🧪 Testing locally: {url}")
        
        # This won't work without a running server, but shows the structure
        print("   ⚠️ Local server needed to test endpoints")
        
    except Exception as e:
        print(f"   ❌ Local test failed: {e}")

def create_data_storage_diagnosis():
    """Create a comprehensive diagnosis"""
    print("\n🔍 COMPREHENSIVE DATA STORAGE DIAGNOSIS")
    print("=" * 60)
    
    # Check database config
    db_ok = inspect_database_config()
    
    # Check scraped data
    scraped_data_ok = inspect_scraped_data_tables()
    
    # Check job folders
    job_folders_ok = inspect_job_folders()
    
    # Check platform data
    platform_data = inspect_platform_data()
    
    # Show API info
    inspect_api_endpoints()
    
    print("\n🎯 DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    if db_ok:
        print("✅ Database: Connected and working")
    else:
        print("❌ Database: Connection issues")
    
    if scraped_data_ok:
        print("✅ Scraped Data: Found in BrightDataScrapedPost table")
    else:
        print("❌ Scraped Data: No data found")
    
    if job_folders_ok:
        print("✅ Job Folders: Structure exists")
    else:
        print("❌ Job Folders: No job folders found")
    
    print(f"📊 Platform Data: {sum(platform_data.values())} total posts across platforms")
    
    print("\n💡 RECOMMENDATIONS:")
    
    if not scraped_data_ok:
        print("   🔧 Run emergency fix script to link scraped data")
    
    if not job_folders_ok:
        print("   🔧 Create test job folders")
    
    print("   🚀 Deploy fixes to production server")
    print("   🌐 Check production database for same data structure")

def main():
    """Main diagnosis function"""
    print("🔍 DATABASE & DATA STORAGE INSPECTION")
    print("=" * 60)
    
    create_data_storage_diagnosis()

if __name__ == "__main__":
    main()