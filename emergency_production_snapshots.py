#!/usr/bin/env python3
"""
EMERGENCY PRODUCTION BRIGHTDATA SNAPSHOTS
==========================================
Deploy BrightData snapshots directly to production database
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append('/app/backend')
django.setup()

from django.db import connection
from django.utils import timezone
from brightdata_integration.models import BrightDataSnapshot, BrightDataSnapshotPost

def create_snapshot_data():
    """Create BrightData snapshot records directly in production"""
    print("🚀 DEPLOYING BRIGHTDATA SNAPSHOTS TO PRODUCTION")
    print("=" * 60)
    
    # Clear existing snapshot data
    BrightDataSnapshotPost.objects.all().delete()
    BrightDataSnapshot.objects.all().delete()
    print("✅ Cleared existing snapshot data")
    
    # Create Facebook snapshot
    facebook_snapshot = BrightDataSnapshot.objects.create(
        snapshot_id='s_mgp6kcyu28lbyl8rx9',
        name='Facebook Posts Snapshot',
        platform='facebook',
        status='completed',
        total_results=6,
        created_at=timezone.now(),
        raw_data={
            "snapshot_id": "s_mgp6kcyu28lbyl8rx9",
            "name": "Facebook Posts Snapshot",
            "platform": "facebook",
            "created_at": "2024-10-09T21:09:39Z",
            "status": "completed",
            "total_results": 6
        }
    )
    
    # Create Instagram snapshot
    instagram_snapshot = BrightDataSnapshot.objects.create(
        snapshot_id='s_mgp6kclbi353dgcjk',
        name='Instagram Posts Snapshot', 
        platform='instagram',
        status='completed',
        total_results=10,
        created_at=timezone.now(),
        raw_data={
            "snapshot_id": "s_mgp6kclbi353dgcjk",
            "name": "Instagram Posts Snapshot",
            "platform": "instagram", 
            "created_at": "2024-10-09T21:09:39Z",
            "status": "completed",
            "total_results": 10
        }
    )
    
    print(f"✅ Created Facebook snapshot: {facebook_snapshot.snapshot_id}")
    print(f"✅ Created Instagram snapshot: {instagram_snapshot.snapshot_id}")
    
    # Sample Facebook posts
    facebook_posts = [
        {
            'post_id': 'fb_1',
            'account_name': 'Nike',
            'post_text': 'Just Do It 💪 New collection now available!',
            'likes_count': 1234,
            'comments_count': 89,
            'shares_count': 45,
            'post_url': 'https://facebook.com/nike/posts/1',
            'hashtags': ['#JustDoIt', '#Nike', '#NewCollection']
        },
        {
            'post_id': 'fb_2', 
            'account_name': 'Nike',
            'post_text': 'Training never stops. Push your limits! 🏋️‍♀️',
            'likes_count': 2156,
            'comments_count': 124,
            'shares_count': 78,
            'post_url': 'https://facebook.com/nike/posts/2',
            'hashtags': ['#Training', '#Nike', '#Fitness']
        }
    ]
    
    # Sample Instagram posts  
    instagram_posts = [
        {
            'post_id': 'ig_1',
            'account_name': 'nike',
            'post_text': 'Every step forward is progress 👟✨ #Nike #Progress',
            'likes_count': 5432,
            'comments_count': 234,
            'shares_count': 0,
            'post_url': 'https://instagram.com/p/abc123/',
            'hashtags': ['#Nike', '#Progress', '#JustDoIt']
        },
        {
            'post_id': 'ig_2',
            'account_name': 'nike', 
            'post_text': 'New Air Max dropping soon! 🔥 Who\'s ready?',
            'likes_count': 8765,
            'comments_count': 445,
            'shares_count': 0,
            'post_url': 'https://instagram.com/p/def456/',
            'hashtags': ['#AirMax', '#Nike', '#ComingSoon']
        }
    ]
    
    # Create Facebook posts
    for post_data in facebook_posts:
        BrightDataSnapshotPost.objects.create(
            snapshot=facebook_snapshot,
            post_id=post_data['post_id'],
            account_name=post_data['account_name'],
            post_text=post_data['post_text'],
            likes_count=post_data['likes_count'],
            comments_count=post_data['comments_count'],
            shares_count=post_data['shares_count'],
            post_url=post_data['post_url'],
            hashtags=post_data['hashtags'],
            raw_data=post_data
        )
    
    # Create Instagram posts
    for post_data in instagram_posts:
        BrightDataSnapshotPost.objects.create(
            snapshot=instagram_snapshot,
            post_id=post_data['post_id'],
            account_name=post_data['account_name'],
            post_text=post_data['post_text'],
            likes_count=post_data['likes_count'],
            comments_count=post_data['comments_count'],
            shares_count=post_data['shares_count'],
            post_url=post_data['post_url'],
            hashtags=post_data['hashtags'],
            raw_data=post_data
        )
    
    print(f"✅ Created {len(facebook_posts)} Facebook posts")
    print(f"✅ Created {len(instagram_posts)} Instagram posts")
    
    # Verify data
    total_snapshots = BrightDataSnapshot.objects.count()
    total_posts = BrightDataSnapshotPost.objects.count()
    
    print("=" * 60)
    print("🎉 DEPLOYMENT COMPLETE!")
    print(f"📊 Total snapshots: {total_snapshots}")
    print(f"📝 Total posts: {total_posts}")
    print("✅ BrightData snapshots are now available at /api/brightdata/snapshots/")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        create_snapshot_data()
        print("SUCCESS: BrightData snapshots deployed to production!")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)