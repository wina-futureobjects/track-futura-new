#!/usr/bin/env python3

import os
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apify_integration.models import ApifyBatchJob
from instagram_data.models import Folder, InstagramPost
from datetime import datetime, timezone

try:
    # Get batch job 8
    batch_job = ApifyBatchJob.objects.get(id=8)
    print(f'Found batch job: {batch_job.name}')
    
    # Create folder for job 8
    folder, created = Folder.objects.get_or_create(
        name=f'{batch_job.name} - Instagram Posts - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        project=batch_job.project,
        defaults={
            'description': f'Posts collected from batch job {batch_job.id}',
            'category': 'posts',
            'folder_type': 'run'
        }
    )
    
    if created:
        print(f'✅ Created folder: {folder.name}')
    else:
        print(f'ℹ️  Folder exists: {folder.name}')
    
    # Check if posts already exist
    existing_posts = folder.posts.count()
    if existing_posts == 0:
        # Create sample posts
        sample_posts = [
            {
                'post_id': 'sample_post_3_job8',
                'shortcode': 'ABC123Job8',
                'url': 'https://www.instagram.com/p/ABC123Job8/',
                'user_posted': 'sample_user_job8',
                'description': 'This is a sample post for batch job 8 #instagram #test #job8',
                'hashtags': ['instagram', 'test', 'job8'],
                'likes': 150,
                'num_comments': 25,
                'views': 500,
                'content_type': 'post',
                'is_verified': True,
                'followers': 10000,
                'location': 'Test Location',
                'date_posted': datetime.now(timezone.utc)
            },
            {
                'post_id': 'sample_post_4_job8',
                'shortcode': 'DEF456Job8', 
                'url': 'https://www.instagram.com/p/DEF456Job8/',
                'user_posted': 'another_user_job8',
                'description': 'Another test post for batch job 8 with more engagement #popular #viral',
                'hashtags': ['popular', 'viral'],
                'likes': 300,
                'num_comments': 45,
                'views': 1200,
                'content_type': 'post',
                'is_verified': False,
                'followers': 5000,
                'location': 'Another Location',
                'date_posted': datetime.now(timezone.utc)
            },
            {
                'post_id': 'sample_post_5_job8',
                'shortcode': 'GHI789Job8',
                'url': 'https://www.instagram.com/p/GHI789Job8/',
                'user_posted': 'verified_account_job8',
                'description': 'Premium content for batch job 8 testing #premium #quality #content',
                'hashtags': ['premium', 'quality', 'content'],
                'likes': 500,
                'num_comments': 80,
                'views': 2000,
                'content_type': 'post',
                'is_verified': True,
                'followers': 50000,
                'location': 'Premium Location',
                'date_posted': datetime.now(timezone.utc)
            }
        ]
        
        created_posts = []
        for post_data in sample_posts:
            post = InstagramPost.objects.create(
                folder=folder,
                **post_data
            )
            created_posts.append(post)
        
        print(f'✅ Created {len(created_posts)} sample Instagram posts')
    else:
        print(f'ℹ️  Folder already has {existing_posts} posts')
    
    # Final verification
    print(f'\n🔍 Final Status:')
    print(f'   Batch Job ID 8: ✅ EXISTS')
    print(f'   Scraper Requests: {batch_job.scraper_requests.count()}')
    print(f'   Folders: {Folder.objects.filter(project=batch_job.project, name__icontains="Job 8").count()}')
    print(f'   Instagram Posts in folder: {folder.posts.count()}')
    
    print(f'\n🚀 Ready! You can now access:')
    print(f'   http://localhost:5174/organizations/2/projects/{batch_job.project.id}/data-storage/job/8')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()