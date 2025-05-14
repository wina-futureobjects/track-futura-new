import os
import django
import json

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import models after Django is set up
from users.models import Project
from instagram_data.models import Folder as InstagramFolder
from facebook_data.models import Folder as FacebookFolder
from instagram_data.serializers import FolderSerializer as InstagramFolderSerializer
from facebook_data.serializers import FolderSerializer as FacebookFolderSerializer
from linkedin_data.serializers import FolderSerializer as LinkedInFolderSerializer
from tiktok_data.serializers import FolderSerializer as TikTokFolderSerializer

# Get a project to use for testing
try:
    test_project = Project.objects.first()
    if test_project:
        print(f"Using test project: ID={test_project.id}, Name={test_project.name}")
    else:
        print("No projects found in the database. Please create a project first.")
        exit(1)
except Exception as e:
    print(f"Error getting test project: {e}")
    exit(1)

# Test creating folders using serializers
print("\n=== Testing Instagram Serializer ===")
instagram_data = {
    'name': 'Instagram Test Folder',
    'description': 'Created via serializer',
    'project': test_project.id
}
instagram_serializer = InstagramFolderSerializer(data=instagram_data)
if instagram_serializer.is_valid():
    instagram_folder = instagram_serializer.save()
    print(f"Created folder ID: {instagram_folder.id}")
    print(f"Project association: {instagram_folder.project_id}")
    print(f"Validated data: {json.dumps(instagram_serializer.validated_data, default=str)}")
else:
    print(f"Serializer validation failed: {instagram_serializer.errors}")

print("\n=== Testing Facebook Serializer ===")
facebook_data = {
    'name': 'Facebook Test Folder',
    'description': 'Created via serializer',
    'project': test_project.id
}
facebook_serializer = FacebookFolderSerializer(data=facebook_data)
if facebook_serializer.is_valid():
    facebook_folder = facebook_serializer.save()
    print(f"Created folder ID: {facebook_folder.id}")
    print(f"Project association: {facebook_folder.project_id}")
    print(f"Validated data: {json.dumps(facebook_serializer.validated_data, default=str)}")
else:
    print(f"Serializer validation failed: {facebook_serializer.errors}")

print("\n=== Testing LinkedIn Serializer ===")
linkedin_data = {
    'name': 'LinkedIn Test Folder',
    'description': 'Created via serializer',
    'project': test_project.id
}
linkedin_serializer = LinkedInFolderSerializer(data=linkedin_data)
if linkedin_serializer.is_valid():
    linkedin_folder = linkedin_serializer.save()
    print(f"Created folder ID: {linkedin_folder.id}")
    print(f"Project association: {linkedin_folder.project_id}")
    print(f"Validated data: {json.dumps(linkedin_serializer.validated_data, default=str)}")
else:
    print(f"Serializer validation failed: {linkedin_serializer.errors}")

print("\n=== Testing TikTok Serializer ===")
tiktok_data = {
    'name': 'TikTok Test Folder',
    'description': 'Created via serializer',
    'project': test_project.id
}
tiktok_serializer = TikTokFolderSerializer(data=tiktok_data)
if tiktok_serializer.is_valid():
    tiktok_folder = tiktok_serializer.save()
    print(f"Created folder ID: {tiktok_folder.id}")
    print(f"Project association: {tiktok_folder.project_id}")
    print(f"Validated data: {json.dumps(tiktok_serializer.validated_data, default=str)}")
else:
    print(f"Serializer validation failed: {tiktok_serializer.errors}")

# Check folder status
print("\n=== Summary of Created Folders ===")
print("Instagram Folders:")
for folder in InstagramFolder.objects.filter(name__contains="Test Folder"):
    print(f"Folder ID: {folder.id}, Name: {folder.name}, Project: {folder.project_id}")

print("\nFacebook Folders:")
for folder in FacebookFolder.objects.filter(name__contains="Test Folder"):
    print(f"Folder ID: {folder.id}, Name: {folder.name}, Project: {folder.project_id}") 