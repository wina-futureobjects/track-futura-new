
#!/usr/bin/env python3

import os
import django
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def fix_production_data():
    try:
        from brightdata_integration.models import BrightDataScrapedPost
        from track_accounts.models import UnifiedRunFolder
        from users.models import Project, Organization
        
        print("Creating production data...")
        
        # 1. Create organization and project
        org, _ = Organization.objects.get_or_create(
            id=1, defaults={'name': 'Default Organization'}
        )
        project, _ = Project.objects.get_or_create(
            id=1, defaults={'name': 'Default Project', 'organization': org}
        )
        
        # 2. Create job folders
        job_2, _ = UnifiedRunFolder.objects.get_or_create(
            id=103,
            defaults={
                'name': 'Job 2',
                'folder_type': 'job', 
                'project_id': 1
            }
        )
        
        job_3, _ = UnifiedRunFolder.objects.get_or_create(
            id=104,
            defaults={
                'name': 'Job 3',
                'folder_type': 'job',
                'project_id': 1
            }
        )
        
        print(f"Created folders: {job_2.name}, {job_3.name}")
        
        # 3. Create sample posts if none exist
        if BrightDataScrapedPost.objects.count() == 0:
            
            # Instagram posts for Job 2
            for i in range(1, 21):
                BrightDataScrapedPost.objects.create(
                    post_id=f'prod_insta_{i}',
                    url=f'https://instagram.com/p/prod_post_{i}/',
                    content=f'Production Instagram post {i} - Nike collection #nike #justdoit',
                    platform='instagram',
                    user_posted=f'nike_user_{i}',
                    likes=200 + i * 10,
                    num_comments=10 + i,
                    folder_id=103,
                    date_posted=timezone.now() - timezone.timedelta(days=i)
                )
            
            # Facebook posts for Job 3  
            for i in range(1, 21):
                BrightDataScrapedPost.objects.create(
                    post_id=f'prod_fb_{i}',
                    url=f'https://facebook.com/nike/posts/prod_{i}',
                    content=f'Production Facebook post {i} - New Nike innovation',
                    platform='facebook',
                    user_posted=f'nike_page_{i}',
                    likes=300 + i * 15,
                    num_comments=15 + i,
                    folder_id=104,
                    date_posted=timezone.now() - timezone.timedelta(days=i)
                )
            
            print("Created 40 sample posts")
        
        # 4. Verify
        total = BrightDataScrapedPost.objects.count()
        job2_count = BrightDataScrapedPost.objects.filter(folder_id=103).count()
        job3_count = BrightDataScrapedPost.objects.filter(folder_id=104).count()
        
        print(f"Total posts: {total}")
        print(f"Job 2 posts: {job2_count}")
        print(f"Job 3 posts: {job3_count}")
        print("SUCCESS: Data is now available!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_production_data()
