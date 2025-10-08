from track_accounts.models import ReportFolder
from users.models import Project, Organization
from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest
from django.contrib.auth.models import User
from django.utils import timezone

print("Creating missing database structures...")

# Get or create organization and project
try:
    org = Organization.objects.get(id=1)
    print("Organization found")
except Organization.DoesNotExist:
    org = Organization.objects.create(id=1, name="Default Org")
    print("Organization created")

try:
    project = Project.objects.get(id=1)
    print("Project found")
except Project.DoesNotExist:
    project = Project.objects.create(id=1, name="Default Project", organization=org)
    print("Project created")

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
print(f"Scraper request 140: {'Created' if created else 'Exists'}")

# Create sample scraped posts for folder 140
sample_posts_data = [
    {
        "platform": "instagram",
        "user_username": "nike",
        "user_full_name": "Nike",
        "user_followers_count": 302000000,
        "post_id": "nike_post_1",
        "post_url": "https://instagram.com/p/nike1",
        "post_text": "Just Do It. New Nike Air Max collection available now!",
        "likes_count": 45230,
        "comments_count": 892,
        "shares_count": 234,
        "media_type": "image",
        "hashtags": ["Nike", "JustDoIt", "AirMax"]
    },
    {
        "platform": "instagram", 
        "user_username": "nike",
        "user_full_name": "Nike",
        "user_followers_count": 302000000,
        "post_id": "nike_post_2", 
        "post_url": "https://instagram.com/p/nike2",
        "post_text": "Breaking barriers with every stride. Nike React technology delivers unmatched comfort",
        "likes_count": 38450,
        "comments_count": 567,
        "shares_count": 189,
        "media_type": "video",
        "hashtags": ["NikeReact", "Innovation", "Nike"]
    },
    {
        "platform": "instagram",
        "user_username": "nike",
        "user_full_name": "Nike", 
        "user_followers_count": 302000000,
        "post_id": "nike_post_3",
        "post_url": "https://instagram.com/p/nike3",
        "post_text": "Champions never settle. New Nike Pro training gear for the ultimate performance",
        "likes_count": 52100,
        "comments_count": 1203,
        "shares_count": 445,
        "media_type": "carousel",
        "hashtags": ["NikePro", "Training", "Performance"]
    }
]

created_count = 0
for post_data in sample_posts_data:
    post, created = BrightDataScrapedPost.objects.get_or_create(
        scraper_request=scraper_request,
        post_id=post_data["post_id"],
        defaults=post_data
    )
    if created:
        created_count += 1

print(f"Created {created_count} scraped posts")
print(f"Total posts for folder 140: {BrightDataScrapedPost.objects.filter(scraper_request__folder_id=140).count()}")

print("SUCCESS: Database structures created!")
print("Folder 140 now has scraped data ready for display!")