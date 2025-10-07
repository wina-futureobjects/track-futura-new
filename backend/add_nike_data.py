#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyBatchJob, ApifyScraperRequest
from instagram_data.models import Folder, InstagramPost
from track_accounts.models import Project
from django.utils import timezone

# Nike Instagram data in the correct format
nike_data = [
    {
        "caption": "Introducing NikeSKIMS. Designed to sculpt. Engineered to perform. A new brand for those who refuse to compromise. Arrives September 26 at 7am PT at nike.com, skims.com, and select Nike and SKIMS retail locations.",
        "ownerFullName": "Nike",
        "ownerUsername": "nike",
        "url": "https://www.instagram.com/p/DO58Q6hDiW7/",
        "commentsCount": 1516,
        "firstComment": "CHRIST IS KING ✝️",
        "likesCount": 78755,
        "timestamp": "2025-09-22T13:00:04.000Z",
        "post_id": "DO58Q6hDiW7"
    },
    {
        "caption": "Momentum lives in the collective. @ucla and @uscedu athletes take center stage in NikeSKIMS. NikeSKIMS arrives September 26 at 7am PT at nike.com, skims.com, and select Nike and SKIMS retail locations.",
        "ownerFullName": "Nike",
        "ownerUsername": "nike",
        "url": "https://www.instagram.com/p/DO6KTM7Drl1/",
        "commentsCount": 375,
        "firstComment": "STRONG!!!",
        "likesCount": 44153,
        "timestamp": "2025-09-22T15:00:10.000Z",
        "post_id": "DO6KTM7Drl1"
    },
    {
        "caption": "A win worth waiting for, what broke you then, built you now. @zoeharrison123 kicks help her side to victory on home soil.",
        "ownerFullName": "Nike",
        "ownerUsername": "nike",
        "url": "https://www.instagram.com/p/DPHPbgLDwpd/",
        "commentsCount": 101,
        "firstComment": "🙌",
        "likesCount": 18453,
        "timestamp": "2025-09-27T16:55:07.000Z",
        "post_id": "DPHPbgLDwpd"
    },
    {
        "caption": "Big stakes. Biggest stage. One way to find out. #JustDoIt",
        "ownerFullName": "Nike",
        "ownerUsername": "nike",
        "url": "https://www.instagram.com/p/DPIbjeAjlR9/",
        "commentsCount": 227,
        "firstComment": "🔥🔥🔥",
        "likesCount": 123249,
        "timestamp": "2025-09-28T04:00:18.000Z",
        "post_id": "DPIbjeAjlR9"
    },
    {
        "caption": "Every round earned. Every punch answered. @rorymcilroy, @officialtommyfleetwood, @robertmacintyre and Team Europe take home the Ryder Cup at Bethpage Black.",
        "ownerFullName": "Nike",
        "ownerUsername": "nike",
        "url": "https://www.instagram.com/p/DPKVkHmEhlc/",
        "commentsCount": 89,
        "firstComment": "🔥🔥🔥",
        "likesCount": 24973,
        "timestamp": "2025-09-28T21:47:24.000Z",
        "post_id": "DPKVkHmEhlc"
    }
]

def update_batch_job_with_nike_data():
    """Update batch job 8 with Nike Instagram data"""
    print("🚀 Updating batch job 8 with Nike Instagram data...")
    
    try:
        # Get batch job 8
        batch_job = ApifyBatchJob.objects.get(id=8)
        print(f"✅ Found batch job: {batch_job.name}")
        
        # Get or create a project
        project = batch_job.project
        print(f"✅ Using project: {project.name}")
        
        # Create or get Instagram folder for this batch job
        folder_name = f"Nike Instagram Data - {batch_job.name}"
        folder, created = Folder.objects.get_or_create(
            name=folder_name,
            project=project,
            defaults={
                'description': 'Nike Instagram posts from Apify',
                'category': 'posts',
            }
        )
        
        if created:
            print(f"✅ Created new folder: {folder.name}")
        else:
            print(f"✅ Using existing folder: {folder.name}")
        
        # Clear existing posts in this folder
        folder.posts.all().delete()
        print("🗑️ Cleared existing posts")
        
        # Add Nike posts to the folder
        for i, nike_post in enumerate(nike_data, 1):
            post = InstagramPost.objects.create(
                folder=folder,
                post_id=nike_post['post_id'],
                shortcode=nike_post['post_id'],
                url=nike_post['url'],
                user_posted=nike_post['ownerUsername'],
                description=nike_post['caption'],
                likes=nike_post['likesCount'],
                num_comments=nike_post['commentsCount'],
                date_posted=timezone.datetime.fromisoformat(nike_post['timestamp'].replace('Z', '+00:00')),
                content_type='post',
                is_verified=True,  # Nike is verified
                hashtags=['JustDoIt', 'Nike'] if 'JustDoIt' in nike_post['caption'] else ['Nike'],
                location='',
                thumbnail='',
                views=None,
                followers=100000000  # Nike has ~100M followers
            )
            print(f"✅ Created post {i}: {post.post_id}")
        
        print(f"🎉 Successfully added {len(nike_data)} Nike Instagram posts to batch job 8!")
        print("📊 Data can now be viewed at: http://localhost:5173/job-folders/8")
        
    except ApifyBatchJob.DoesNotExist:
        print("❌ Batch job 8 not found")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update_batch_job_with_nike_data()