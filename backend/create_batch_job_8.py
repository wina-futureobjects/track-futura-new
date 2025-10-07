#!/usr/bin/env python3

import os
import sys

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apify_integration.models import ApifyBatchJob, ApifyScraperRequest
from users.models import Project
from datetime import datetime

try:
    # Get the first project (or create one if none exists)
    project = Project.objects.first()
    if not project:
        from django.contrib.auth.models import User
        from users.models import Organization
        
        user = User.objects.filter(username='testuser').first()
        org = Organization.objects.filter(name='Test Organization').first()
        
        if user and org:
            project = Project.objects.create(
                name='Test Project',
                description='Test project for development',
                organization=org,
                owner=user
            )
            print(f'✅ Created new project: {project.name}')
        else:
            print('❌ No user or organization found. Please run create_test_user.py first.')
            sys.exit(1)
    
    # Create batch job with ID 8
    batch_job = ApifyBatchJob.objects.create(
        id=8,  # Force ID 8
        name='Instagram Posts Collection - Job 8',
        project=project,
        platforms_to_scrape=['instagram'],
        content_types_to_scrape={'instagram': ['posts']},
        num_of_posts=20,
        auto_create_folders=True,
        status='completed',
        total_sources=1,
        processed_sources=1,
        successful_requests=1,
        failed_requests=0
    )
    
    print(f'✅ Created batch job with ID: {batch_job.id}')
    print(f'   Name: {batch_job.name}')
    print(f'   Status: {batch_job.status}')
    print(f'   Project: {batch_job.project.name}')
    
    # Create a scraper request for this batch job
    from apify_integration.models import ApifyConfig
    
    # Get or create a config for Instagram
    config, created = ApifyConfig.objects.get_or_create(
        platform='instagram_posts',
        defaults={
            'name': 'Instagram Posts Scraper',
            'api_token': 'test_token',
            'actor_id': 'apify/instagram-scraper',
            'description': 'Test configuration for Instagram posts'
        }
    )
    
    scraper_request = ApifyScraperRequest.objects.create(
        config=config,
        batch_job=batch_job,
        platform='instagram',
        content_type='posts',
        target_url='https://www.instagram.com/test_account/',
        source_name='test_account',
        status='completed'
    )
    
    print(f'✅ Created scraper request: {scraper_request.id}')
    
    # Now let's add some sample Instagram posts for this job
    from instagram_data.models import Folder, InstagramPost
    from datetime import datetime, timezone
    
    # Create a folder for this batch job
    folder = Folder.objects.create(
        name=f'{batch_job.name} - Instagram Posts - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        description=f'Posts collected from batch job {batch_job.id}',
        project=project,
        category='posts',
        folder_type='run'
    )
    
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
    print(f'✅ Created folder: {folder.name}')
    
    # Verify the setup
    print(f'\n🔍 Verification:')
    print(f'   Batch Job ID 8: ✅ EXISTS')
    print(f'   Scraper Requests: {batch_job.scraper_requests.count()}')
    print(f'   Instagram Posts: {folder.posts.count()}')
    print(f'   Folder: {folder.name}')
    
    print(f'\n🚀 You can now access: http://localhost:5174/organizations/2/projects/{project.id}/data-storage/job/8')
    
except Exception as e:
    if 'UNIQUE constraint failed' in str(e) and 'id' in str(e):
        print('ℹ️  Batch job with ID 8 already exists')
        batch_job = ApifyBatchJob.objects.get(id=8)
        print(f'   Name: {batch_job.name}')
        print(f'   Status: {batch_job.status}')
    else:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()