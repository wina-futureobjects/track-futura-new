import os
import django

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import models after Django is set up
from instagram_data.models import Folder as InstagramFolder
from facebook_data.models import Folder as FacebookFolder
from linkedin_data.models import Folder as LinkedInFolder
from tiktok_data.models import Folder as TikTokFolder

# Check Instagram folders
print("=== Instagram Folders ===")
instagram_folders = InstagramFolder.objects.all()
for folder in instagram_folders:
    print(f"Folder ID: {folder.id}, Name: {folder.name}, Project: {folder.project_id}")

# Check Facebook folders
print("\n=== Facebook Folders ===")
facebook_folders = FacebookFolder.objects.all()
for folder in facebook_folders:
    print(f"Folder ID: {folder.id}, Name: {folder.name}, Project: {folder.project_id}")

# Check LinkedIn folders
print("\n=== LinkedIn Folders ===")
linkedin_folders = LinkedInFolder.objects.all()
for folder in linkedin_folders:
    print(f"Folder ID: {folder.id}, Name: {folder.name}, Project: {folder.project_id}")

# Check TikTok folders
print("\n=== TikTok Folders ===")
tiktok_folders = TikTokFolder.objects.all()
for folder in tiktok_folders:
    print(f"Folder ID: {folder.id}, Name: {folder.name}, Project: {folder.project_id}")

# Summary
print("\n=== Summary ===")
print(f"Instagram folders with null project: {InstagramFolder.objects.filter(project__isnull=True).count()}")
print(f"Facebook folders with null project: {FacebookFolder.objects.filter(project__isnull=True).count()}")
print(f"LinkedIn folders with null project: {LinkedInFolder.objects.filter(project__isnull=True).count()}")
print(f"TikTok folders with null project: {TikTokFolder.objects.filter(project__isnull=True).count()}") 