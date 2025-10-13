#!/usr/bin/env python3
"""
🎯 BACKEND DATA VIEWER
Show exactly where your BrightData snapshots are stored in the backend
"""

import os
import sys
import json
import django

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def show_backend_data():
    """Show exactly where your data is saved in the backend"""
    
    print("🎯 BACKEND DATA LOCATION VIEWER")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        # Find your latest folders
        cursor.execute("""
            SELECT id, name, platform_code, project_id, created_at 
            FROM track_accounts_unifiedrunfolder 
            WHERE name LIKE '%Nike%Collection'
            ORDER BY id DESC
            LIMIT 2
        """)
        
        folders = cursor.fetchall()
        
        if not folders:
            print("❌ No Nike folders found!")
            return
        
        print(f"📁 FOUND {len(folders)} DATA FOLDERS:")
        
        for folder in folders:
            folder_id, name, platform, project_id, created_at = folder
            
            print(f"\n📂 FOLDER: {name}")
            print(f"   🆔 ID: {folder_id}")
            print(f"   📱 Platform: {platform}")
            print(f"   📅 Created: {created_at}")
            
            # Get posts in this folder
            cursor.execute("""
                SELECT post_id, user_posted, content, likes, num_comments, shares, platform, url
                FROM brightdata_integration_brightdatascrapedpost
                WHERE folder_id = %s
                ORDER BY id DESC
            """, [folder_id])
            
            posts = cursor.fetchall()
            
            print(f"   📝 POSTS: {len(posts)}")
            
            if posts:
                print(f"   📋 SAMPLE DATA:")
                for i, post in enumerate(posts[:3], 1):
                    post_id, user, content, likes, comments, shares, platform, url = post
                    print(f"      {i}. User: {user}")
                    print(f"         Content: {content[:80]}...")
                    print(f"         Engagement: {likes} likes, {comments} comments, {shares} shares")
                    print(f"         URL: {url}")
                    print()
            
            # Backend API endpoints
            print(f"   🔗 BACKEND API ENDPOINTS:")
            print(f"      • GET /api/brightdata/data-storage/run/{folder_id}/")
            print(f"      • Direct URL: http://localhost:8000/api/brightdata/data-storage/run/{folder_id}/")
            
            # Database table info
            print(f"   💾 DATABASE LOCATION:")
            print(f"      • Table: brightdata_integration_brightdatascrapedpost")
            print(f"      • Filter: folder_id = {folder_id}")
        
        # Show scraper requests
        cursor.execute("""
            SELECT id, snapshot_id, platform, status, folder_id
            FROM brightdata_integration_brightdatascraperrequest
            WHERE snapshot_id IN ('s_mgp6kcyu28lbyl8rx9', 's_mgp6kclbi353dgcjk')
            ORDER BY id DESC
            LIMIT 2
        """)
        
        requests = cursor.fetchall()
        
        print(f"\n📊 SCRAPER REQUESTS:")
        for req in requests:
            req_id, snapshot_id, platform, status, folder_id = req
            print(f"   • ID {req_id}: {snapshot_id} ({platform}) -> Folder {folder_id}")
        
        # Show total counts
        cursor.execute("""
            SELECT 
                COUNT(*) as total_posts,
                SUM(CASE WHEN platform = 'facebook' THEN 1 ELSE 0 END) as facebook_posts,
                SUM(CASE WHEN platform = 'instagram' THEN 1 ELSE 0 END) as instagram_posts
            FROM brightdata_integration_brightdatascrapedpost
            WHERE folder_id IN (514, 515)
        """)
        
        counts = cursor.fetchone()
        total, facebook, instagram = counts
        
        print(f"\n📈 DATA SUMMARY:")
        print(f"   ✅ Total Posts Saved: {total}")
        print(f"   📘 Facebook Posts: {facebook}")
        print(f"   📷 Instagram Posts: {instagram}")
        
        return folders

def test_api_endpoints():
    """Test the backend API endpoints"""
    
    print("\n🔧 BACKEND API TESTING:")
    print("-" * 40)
    
    # Start Django development server to test
    print("📡 To test your backend APIs, run:")
    print("   cd backend")
    print("   python manage.py runserver 8000")
    print()
    print("🌐 Then test these URLs in your browser:")
    print("   • http://localhost:8000/api/brightdata/data-storage/run/514/")
    print("   • http://localhost:8000/api/brightdata/data-storage/run/515/")
    print()
    
    # Show curl commands
    print("💻 Or test with curl commands:")
    print(f'   curl "http://localhost:8000/api/brightdata/data-storage/run/514/" | python -m json.tool')
    print(f'   curl "http://localhost:8000/api/brightdata/data-storage/run/515/" | python -m json.tool')

def show_raw_json_samples():
    """Show raw JSON samples of your saved data"""
    
    print("\n📄 RAW DATA SAMPLES:")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # Get Facebook sample
        cursor.execute("""
            SELECT raw_data FROM brightdata_integration_brightdatascrapedpost
            WHERE platform = 'facebook' AND folder_id = 514
            LIMIT 1
        """)
        
        fb_result = cursor.fetchone()
        if fb_result:
            raw_data = fb_result[0]
            try:
                if isinstance(raw_data, str):
                    data = json.loads(raw_data)
                else:
                    data = raw_data
                
                print("📘 FACEBOOK POST SAMPLE:")
                print(json.dumps(data, indent=2)[:500] + "...")
                
            except Exception as e:
                print(f"❌ Error parsing Facebook data: {e}")
        
        # Get Instagram sample  
        cursor.execute("""
            SELECT raw_data FROM brightdata_integration_brightdatascrapedpost
            WHERE platform = 'instagram' AND folder_id = 515
            LIMIT 1
        """)
        
        ig_result = cursor.fetchone()
        if ig_result:
            raw_data = ig_result[0]
            try:
                if isinstance(raw_data, str):
                    data = json.loads(raw_data)
                else:
                    data = raw_data
                
                print("\n📷 INSTAGRAM POST SAMPLE:")
                print(json.dumps(data, indent=2)[:500] + "...")
                
            except Exception as e:
                print(f"❌ Error parsing Instagram data: {e}")

if __name__ == "__main__":
    try:
        folders = show_backend_data()
        test_api_endpoints()
        show_raw_json_samples()
        
        print(f"\n" + "=" * 60)
        print("🎉 BACKEND DATA ACCESS SUMMARY:")
        print("✅ Your 2 latest BrightData snapshots are saved in:")
        print("   • Database: SQLite (backend/db.sqlite3)")
        print("   • Table: brightdata_integration_brightdatascrapedpost")
        print("   • Folders: 514 (Facebook), 515 (Instagram)")
        print("   • Total Posts: 16 (6 Facebook + 10 Instagram)")
        
        print(f"\n🚀 TO ACCESS VIA BACKEND:")
        print("   1. Start server: cd backend && python manage.py runserver")
        print("   2. Visit: http://localhost:8000/api/brightdata/data-storage/run/514/")
        print("   3. Visit: http://localhost:8000/api/brightdata/data-storage/run/515/")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()