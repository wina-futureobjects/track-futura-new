import os
import django

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import models after Django is set up
from users.models import Project
from instagram_data.models import Folder as InstagramFolder
from facebook_data.models import Folder as FacebookFolder
from linkedin_data.models import Folder as LinkedInFolder
from tiktok_data.models import Folder as TikTokFolder

# Get the default project to assign (first project in the database)
# You can change this to any project ID you want to use
try:
    default_project = Project.objects.first()
    if default_project:
        print(f"Using default project: ID={default_project.id}, Name={default_project.name}")
    else:
        print("No projects found in the database. Please create a project first.")
        exit(1)
except Exception as e:
    print(f"Error getting default project: {e}")
    exit(1)

# Fix Instagram folders
print("\n=== Fixing Instagram Folders ===")
instagram_folders = InstagramFolder.objects.filter(project__isnull=True)
count = 0
for folder in instagram_folders:
    folder.project = default_project
    folder.save()
    count += 1
    print(f"Fixed Folder ID: {folder.id}, Name: {folder.name}")
print(f"Fixed {count} Instagram folders")

# Fix Facebook folders
print("\n=== Fixing Facebook Folders ===")
facebook_folders = FacebookFolder.objects.filter(project__isnull=True)
count = 0
for folder in facebook_folders:
    folder.project = default_project
    folder.save()
    count += 1
    print(f"Fixed Folder ID: {folder.id}, Name: {folder.name}")
print(f"Fixed {count} Facebook folders")

# Fix LinkedIn folders
print("\n=== Fixing LinkedIn Folders ===")
linkedin_folders = LinkedInFolder.objects.filter(project__isnull=True)
count = 0
for folder in linkedin_folders:
    folder.project = default_project
    folder.save()
    count += 1
    print(f"Fixed Folder ID: {folder.id}, Name: {folder.name}")
print(f"Fixed {count} LinkedIn folders")

# Fix TikTok folders
print("\n=== Fixing TikTok Folders ===")
tiktok_folders = TikTokFolder.objects.filter(project__isnull=True)
count = 0
for folder in tiktok_folders:
    folder.project = default_project
    folder.save()
    count += 1
    print(f"Fixed Folder ID: {folder.id}, Name: {folder.name}")
print(f"Fixed {count} TikTok folders")

print("\n=== All Done ===")
print("All folders have been updated with a project reference.") 