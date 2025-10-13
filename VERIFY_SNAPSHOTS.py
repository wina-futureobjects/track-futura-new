#!/usr/bin/env python3
"""
🎯 VERIFY SNAPSHOTS SAVED
Direct SQL verification that snapshots were saved successfully
"""

import os
import sys
import django

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def verify_saved_snapshots():
    """Verify snapshots using direct SQL"""
    
    print("🎯 VERIFYING SAVED SNAPSHOTS")
    print("=" * 50)
    
    with connection.cursor() as cursor:
        # Check folders
        cursor.execute("""
            SELECT id, name, platform_code, project_id 
            FROM track_accounts_unifiedrunfolder 
            WHERE name LIKE '%Nike%Collection'
            ORDER BY id DESC
            LIMIT 5
        """)
        
        folders = cursor.fetchall()
        print(f"📁 FOLDERS CREATED: {len(folders)}")
        
        for folder in folders:
            folder_id, name, platform, project_id = folder
            print(f"\n📂 {name}")
            print(f"   ID: {folder_id}")
            print(f"   Platform: {platform}")
            print(f"   Project: {project_id}")
            
            # Count posts in this folder
            cursor.execute("""
                SELECT COUNT(*) FROM brightdata_integration_brightdatascrapedpost
                WHERE folder_id = %s
            """, [folder_id])
            
            post_count = cursor.fetchone()[0]
            print(f"   Posts: {post_count}")
            
            # Show sample posts
            if post_count > 0:
                cursor.execute("""
                    SELECT post_id, user_posted, content, likes, num_comments
                    FROM brightdata_integration_brightdatascrapedpost
                    WHERE folder_id = %s
                    LIMIT 3
                """, [folder_id])
                
                posts = cursor.fetchall()
                print(f"   📝 Sample Posts:")
                for post in posts:
                    post_id, user, content, likes, comments = post
                    print(f"      • {user}: {content[:50]}... ({likes} likes, {comments} comments)")
            
            # URLs
            api_url = f"/api/brightdata/data-storage/run/{folder_id}/"
            frontend_url = f"https://trackfutura.futureobjects.io/organizations/1/projects/{project_id}/data-storage"
            
            print(f"   🔗 API: {api_url}")
            print(f"   🌐 Frontend: {frontend_url}")
        
        # Check scraper requests  
        cursor.execute("""
            SELECT id, snapshot_id, platform, status, folder_id
            FROM brightdata_integration_brightdatascraperrequest
            WHERE snapshot_id IN ('s_mgp6kcyu28lbyl8rx9', 's_mgp6kclbi353dgcjk')
        """)
        
        requests = cursor.fetchall()
        print(f"\n📊 SCRAPER REQUESTS: {len(requests)}")
        for req in requests:
            req_id, snapshot_id, platform, status, folder_id = req
            print(f"   {platform}: {snapshot_id} -> Folder {folder_id} ({status})")
        
        # Total posts
        cursor.execute("""
            SELECT COUNT(*) FROM brightdata_integration_brightdatascrapedpost
            WHERE scraper_request_id IN (
                SELECT id FROM brightdata_integration_brightdatascraperrequest
                WHERE snapshot_id IN ('s_mgp6kcyu28lbyl8rx9', 's_mgp6kclbi353dgcjk')
            )
        """)
        
        total_posts = cursor.fetchone()[0]
        
        print(f"\n🎉 VERIFICATION SUMMARY:")
        print(f"   ✅ Folders Created: {len(folders)}")
        print(f"   ✅ Scraper Requests: {len(requests)}")
        print(f"   ✅ Total Posts Saved: {total_posts}")
        
        # Main access URL
        main_url = "https://trackfutura.futureobjects.io/organizations/1/projects/1/data-storage"
        print(f"\n🎯 MAIN ACCESS URL:")
        print(f"   {main_url}")
        print(f"   📁 Navigate to 'Data Storage' to view your saved snapshots")
        
        return main_url, folders

if __name__ == "__main__":
    try:
        url, folders = verify_saved_snapshots()
        print(f"\n✅ VERIFICATION COMPLETE!")
        print(f"🔗 Access your snapshots at: {url}")
        if folders:
            print(f"\n📂 Folder IDs for direct access:")
            for folder in folders:
                folder_id, name, platform, project_id = folder
                print(f"   • {name}: /organizations/1/projects/{project_id}/data-storage/run/{folder_id}/")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()