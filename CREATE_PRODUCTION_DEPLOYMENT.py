#!/usr/bin/env python3
"""
🚀 PRODUCTION DEPLOYMENT: BRIGHTDATA SNAPSHOTS
Deploy your saved snapshots to production Upsun environment
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

def create_production_deployment_script():
    """Create a script to deploy snapshots to production"""
    
    print("🚀 PRODUCTION DEPLOYMENT: BRIGHTDATA SNAPSHOTS")
    print("=" * 60)
    
    # Export your snapshot data for production deployment
    with connection.cursor() as cursor:
        # Get the saved snapshots data
        cursor.execute("""
            SELECT 
                p.post_id, p.platform, p.folder_id, p.url, p.user_posted, 
                p.content, p.likes, p.num_comments, p.shares, p.hashtags, 
                p.mentions, p.is_verified, p.raw_data, p.date_posted,
                r.snapshot_id, r.source_name,
                f.name as folder_name, f.platform_code
            FROM brightdata_integration_brightdatascrapedpost p
            JOIN brightdata_integration_brightdatascraperrequest r ON p.scraper_request_id = r.id
            JOIN track_accounts_unifiedrunfolder f ON p.folder_id = f.id
            WHERE p.folder_id IN (514, 515)
            ORDER BY p.platform, p.id
        """)
        
        rows = cursor.fetchall()
        
    if not rows:
        print("❌ No snapshot data found to deploy!")
        return
    
    # Organize data by platform
    facebook_posts = []
    instagram_posts = []
    
    for row in rows:
        post_data = {
            'post_id': row[0],
            'platform': row[1],
            'folder_id': row[2],
            'url': row[3],
            'user_posted': row[4],
            'content': row[5],
            'likes': row[6],
            'num_comments': row[7],
            'shares': row[8],
            'hashtags': json.loads(row[9]) if row[9] else [],
            'mentions': json.loads(row[10]) if row[10] else [],
            'is_verified': row[11],
            'raw_data': json.loads(row[12]) if row[12] else {},
            'date_posted': row[13],
            'snapshot_id': row[14],
            'source_name': row[15],
            'folder_name': row[16],
            'platform_code': row[17]
        }
        
        if row[1] == 'facebook':
            facebook_posts.append(post_data)
        else:
            instagram_posts.append(post_data)
    
    print(f"📊 DATA TO DEPLOY:")
    print(f"   📘 Facebook Posts: {len(facebook_posts)}")
    print(f"   📷 Instagram Posts: {len(instagram_posts)}")
    
    # Create production deployment script
    deployment_script = f"""#!/usr/bin/env python3
'''
🚀 PRODUCTION BRIGHTDATA DEPLOYMENT
Deploy BrightData snapshots to Upsun production environment
'''

import os
import sys
import json
import django
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection, transaction
from django.utils import timezone

# Your snapshot data
FACEBOOK_POSTS = {json.dumps(facebook_posts, indent=2, default=str)}

INSTAGRAM_POSTS = {json.dumps(instagram_posts, indent=2, default=str)}

def deploy_snapshots_to_production():
    '''Deploy snapshots to production database'''
    
    print("🚀 DEPLOYING BRIGHTDATA SNAPSHOTS TO PRODUCTION")
    print("=" * 60)
    
    with transaction.atomic():
        with connection.cursor() as cursor:
            
            # Create folders first
            print("📁 Creating production folders...")
            
            # Facebook folder
            cursor.execute('''
                INSERT OR IGNORE INTO track_accounts_unifiedrunfolder 
                (id, name, project_id, folder_type, platform_code, service_code, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [
                514,
                'Nike Facebook Collection (Production)',
                1,
                'job',
                'facebook',
                'posts',
                'BrightData Facebook snapshot s_mgp6kcyu28lbyl8rx9',
                timezone.now(),
                timezone.now()
            ])
            
            # Instagram folder
            cursor.execute('''
                INSERT OR IGNORE INTO track_accounts_unifiedrunfolder 
                (id, name, project_id, folder_type, platform_code, service_code, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [
                515,
                'Nike Instagram Collection (Production)',
                1,
                'job',
                'instagram',
                'posts',
                'BrightData Instagram snapshot s_mgp6kclbi353dgcjk',
                timezone.now(),
                timezone.now()
            ])
            
            print("✅ Production folders created")
            
            # Create scraper requests
            print("📊 Creating production scraper requests...")
            
            cursor.execute('''
                INSERT OR IGNORE INTO brightdata_integration_brightdatascraperrequest
                (id, snapshot_id, platform, content_type, target_url, source_name, folder_id, 
                 status, scrape_number, created_at, updated_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [
                511, 's_mgp6kcyu28lbyl8rx9', 'facebook', 'posts',
                'BrightData Production s_mgp6kcyu28lbyl8rx9', 'Nike Facebook Production',
                514, 'completed', 1, timezone.now(), timezone.now(), timezone.now()
            ])
            
            cursor.execute('''
                INSERT OR IGNORE INTO brightdata_integration_brightdatascraperrequest
                (id, snapshot_id, platform, content_type, target_url, source_name, folder_id,
                 status, scrape_number, created_at, updated_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [
                512, 's_mgp6kclbi353dgcjk', 'instagram', 'posts',
                'BrightData Production s_mgp6kclbi353dgcjk', 'Nike Instagram Production',
                515, 'completed', 1, timezone.now(), timezone.now(), timezone.now()
            ])
            
            print("✅ Production scraper requests created")
            
            # Deploy Facebook posts
            print("📘 Deploying Facebook posts...")
            fb_count = 0
            
            for post in FACEBOOK_POSTS:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO brightdata_integration_brightdatascrapedpost
                        (post_id, platform, scraper_request_id, folder_id, url, user_posted, content,
                         likes, num_comments, shares, hashtags, mentions, is_verified, follower_count,
                         raw_data, date_posted, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', [
                        post['post_id'], 'facebook', 511, 514, post['url'], post['user_posted'],
                        post['content'], post['likes'], post['num_comments'], post['shares'],
                        json.dumps(post['hashtags']), json.dumps(post['mentions']), post['is_verified'],
                        39000000, json.dumps(post['raw_data']), timezone.now(), timezone.now(), timezone.now()
                    ])
                    fb_count += 1
                except Exception as e:
                    print(f"⚠️ Facebook post error: {{e}}")
            
            # Deploy Instagram posts
            print("📷 Deploying Instagram posts...")
            ig_count = 0
            
            for post in INSTAGRAM_POSTS:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO brightdata_integration_brightdatascrapedpost
                        (post_id, platform, scraper_request_id, folder_id, url, user_posted, content,
                         likes, num_comments, shares, hashtags, mentions, is_verified, follower_count,
                         raw_data, date_posted, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', [
                        post['post_id'], 'instagram', 512, 515, post['url'], post['user_posted'],
                        post['content'], post['likes'], post['num_comments'], post['shares'],
                        json.dumps(post['hashtags']), json.dumps(post['mentions']), post['is_verified'],
                        46000000, json.dumps(post['raw_data']), timezone.now(), timezone.now(), timezone.now()
                    ])
                    ig_count += 1
                except Exception as e:
                    print(f"⚠️ Instagram post error: {{e}}")
            
            print(f"🎉 PRODUCTION DEPLOYMENT COMPLETE!")
            print(f"   ✅ Facebook Posts: {{fb_count}}")
            print(f"   ✅ Instagram Posts: {{ig_count}}")
            print(f"   📊 Total Posts: {{fb_count + ig_count}}")
            
            print(f"\\n🌐 PRODUCTION API ENDPOINTS:")
            print(f"   • https://trackfutura.futureobjects.io/api/brightdata/data-storage/run/514/")
            print(f"   • https://trackfutura.futureobjects.io/api/brightdata/data-storage/run/515/")
            
            print(f"\\n🎯 FRONTEND ACCESS:")
            print(f"   • https://trackfutura.futureobjects.io/organizations/1/projects/1/data-storage")

if __name__ == "__main__":
    deploy_snapshots_to_production()
"""
    
    # Save the deployment script
    script_path = "DEPLOY_SNAPSHOTS_TO_PRODUCTION.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(deployment_script)
    
    print(f"✅ Created deployment script: {script_path}")
    
    return script_path

if __name__ == "__main__":
    try:
        script_path = create_production_deployment_script()
        print(f"\\n🚀 NEXT STEPS FOR PRODUCTION DEPLOYMENT:")
        print(f"   1. Upload script to production: scp {script_path} production:/")
        print(f"   2. Run on production server")
        print(f"   3. Verify production API endpoints")
    except Exception as e:
        print(f"\\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()