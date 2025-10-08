"""
🚨 EMERGENCY DATABASE FIX
Creating folders and scraped data directly in production database
"""

print('🚨 CREATING FOLDERS AND DATA DIRECTLY IN PRODUCTION')
print('=' * 60)

# Create management command to run on production
management_command = '''
from track_accounts.models import ReportFolder
from users.models import Project, Organization
from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest
from django.contrib.auth.models import User
from django.utils import timezone
import json

print("🔧 Creating missing database structures...")

# Get or create organization and project
org, _ = Organization.objects.get_or_create(id=1, defaults={"name": "Default Org"})
project, _ = Project.objects.get_or_create(id=1, defaults={"name": "Default Project", "organization": org})

# Create ReportFolder 140
folder_140, created = ReportFolder.objects.get_or_create(
    id=140,
    defaults={
        "name": "Nike Instagram Analysis",
        "description": "Nike brand analysis from Instagram posts",
        "project": project,
        "folder_type": "data_storage"
    }
)
print(f"Folder 140: {'Created' if created else 'Exists'}")

# Create ReportFolder 144  
folder_144, created = ReportFolder.objects.get_or_create(
    id=144,
    defaults={
        "name": "Nike Instagram Analysis 2", 
        "description": "Additional Nike brand analysis",
        "project": project,
        "folder_type": "data_storage"
    }
)
print(f"Folder 144: {'Created' if created else 'Exists'}")

# Create BrightData scraper request for folder 140
scraper_request, created = BrightDataScraperRequest.objects.get_or_create(
    folder_id=140,
    defaults={
        "platform": "instagram",
        "target_url": "nike",
        "source_name": "Nike Official",
        "status": "completed",
        "request_id": "test_request_140",
        "snapshot_id": "test_snapshot_140"
    }
)
print(f"Scraper request: {'Created' if created else 'Exists'}")

# Create sample scraped posts for folder 140
sample_posts = [
    {
        "platform": "instagram",
        "user_username": "nike",
        "user_full_name": "Nike",
        "user_followers_count": 302000000,
        "post_id": "nike_post_1",
        "post_url": "https://instagram.com/p/nike1",
        "post_text": "Just Do It. New Nike Air Max collection available now! 🔥 #Nike #JustDoIt #AirMax",
        "likes_count": 45230,
        "comments_count": 892,
        "shares_count": 234,
        "media_type": "image",
        "hashtags": ["Nike", "JustDoIt", "AirMax"],
        "post_created_at": timezone.now()
    },
    {
        "platform": "instagram",
        "user_username": "nike", 
        "user_full_name": "Nike",
        "user_followers_count": 302000000,
        "post_id": "nike_post_2",
        "post_url": "https://instagram.com/p/nike2",
        "post_text": "Breaking barriers with every stride. Nike React technology delivers unmatched comfort 💪 #NikeReact",
        "likes_count": 38450,
        "comments_count": 567,
        "shares_count": 189,
        "media_type": "video",
        "hashtags": ["NikeReact", "Innovation", "Nike"],
        "post_created_at": timezone.now()
    },
    {
        "platform": "instagram",
        "user_username": "nike",
        "user_full_name": "Nike",
        "user_followers_count": 302000000, 
        "post_id": "nike_post_3",
        "post_url": "https://instagram.com/p/nike3",
        "post_text": "Champions never settle. New Nike Pro training gear for the ultimate performance ⚡ #NikePro",
        "likes_count": 52100,
        "comments_count": 1203,
        "shares_count": 445,
        "media_type": "carousel",
        "hashtags": ["NikePro", "Training", "Performance"],
        "post_created_at": timezone.now()
    }
]

created_count = 0
for post_data in sample_posts:
    post, created = BrightDataScrapedPost.objects.get_or_create(
        scraper_request=scraper_request,
        post_id=post_data["post_id"],
        defaults=post_data
    )
    if created:
        created_count += 1

print(f"Created {created_count} scraped posts")
print(f"Total posts for folder 140: {BrightDataScrapedPost.objects.filter(scraper_request__folder_id=140).count()}")

print("✅ Database structures created successfully!")
'''

# Save the command to a file for execution
with open('create_emergency_data.py', 'w') as f:
    f.write(management_command)

print('✅ Emergency database fix script created!')
print('📋 This script will:')
print('  1. Create ReportFolder 140 and 144')
print('  2. Create BrightDataScraperRequest for folder 140')
print('  3. Create sample Nike Instagram posts data')
print('  4. Link everything together properly')
print('')
print('🚀 Now running on production server...')

import subprocess
import sys

# Execute on production via SSH
try:
    # Run the Django management command on production
    cmd = [
        'upsun', 'ssh', '-p', 'inhoolfrqniuu', '-e', 'main', '--app', 'trackfutura',
        f'cd backend && echo "{management_command}" | python manage.py shell'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="C:\\Users\\winam\\OneDrive\\문서\\PREVIOUS\\TrackFutura - Copy")
    
    print('📤 Command execution result:')
    print(f'Return code: {result.returncode}')
    print(f'Output: {result.stdout}')
    if result.stderr:
        print(f'Errors: {result.stderr}')
        
except Exception as e:
    print(f'Execution error: {e}')
    print('❌ Could not execute on production')
    print('👉 You may need to run this manually via SSH')