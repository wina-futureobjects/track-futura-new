from track_accounts.models import SourceFolder
from facebook_data.models import Folder as FacebookFolder
from users.models import Project

print("=== CREATING SOURCE FOLDERS FOR BRAND DATA ===")

# Get project (assuming project ID 1)
project = Project.objects.first()
if not project:
    print("❌ No project found!")
    exit()

print(f"📋 Using project: {project.name} (ID: {project.id})")

# Get Nike and Adidas Facebook folders
nike_folder = FacebookFolder.objects.filter(name__icontains='Nike', folder_type='company').first()
adidas_folder = FacebookFolder.objects.filter(name__icontains='Adidas', folder_type='competitor').first()

if not nike_folder:
    print("❌ Nike folder not found!")
    exit()

if not adidas_folder:
    print("❌ Adidas folder not found!")
    exit()

print(f"✅ Found Nike folder: {nike_folder.name} (ID: {nike_folder.id})")
print(f"✅ Found Adidas folder: {adidas_folder.name} (ID: {adidas_folder.id})")

# Create or update Nike SourceFolder
nike_source_folder, created = SourceFolder.objects.get_or_create(
    name="Nike Brand Sources",
    project=project,
    defaults={
        'folder_type': 'company',
        'description': 'Nike brand social media data sources for competitive analysis'
    }
)

if created:
    print(f"✅ Created Nike SourceFolder: {nike_source_folder.name}")
else:
    print(f"📁 Nike SourceFolder exists: {nike_source_folder.name}")

# Set the folder_type to ensure it's correct
nike_source_folder.folder_type = 'company'
nike_source_folder.save()

# Create or update Adidas SourceFolder
adidas_source_folder, created = SourceFolder.objects.get_or_create(
    name="Adidas Competitor Sources",
    project=project,
    defaults={
        'folder_type': 'competitor',
        'description': 'Adidas competitor social media data sources for competitive analysis'
    }
)

if created:
    print(f"✅ Created Adidas SourceFolder: {adidas_source_folder.name}")
else:
    print(f"📁 Adidas SourceFolder exists: {adidas_source_folder.name}")

# Set the folder_type to ensure it's correct
adidas_source_folder.folder_type = 'competitor'
adidas_source_folder.save()

# Add source count information
nike_posts_count = nike_folder.posts.count()
adidas_posts_count = adidas_folder.posts.count()

print(f"\n📊 BRAND DATA SUMMARY:")
print(f"  Nike SourceFolder ID: {nike_source_folder.id} ({nike_posts_count} posts)")
print(f"  Adidas SourceFolder ID: {adidas_source_folder.id} ({adidas_posts_count} posts)")

# Store the mapping for the backend to use
print(f"\n🔧 CONFIGURATION MAPPING:")
print(f"  Frontend will see:")
print(f"    - Nike Brand Sources (SourceFolder ID: {nike_source_folder.id})")
print(f"    - Adidas Competitor Sources (SourceFolder ID: {adidas_source_folder.id})")
print(f"  Backend should map to:")
print(f"    - Nike: FacebookFolder ID {nike_folder.id}")
print(f"    - Adidas: FacebookFolder ID {adidas_folder.id}")

print(f"\n✅ SOURCE FOLDERS READY FOR SENTIMENT ANALYSIS!")
print(f"🎯 Users can now select Nike and Adidas sources in Report Marketplace")

# Verify the API will return these
all_source_folders = SourceFolder.objects.filter(project=project)
print(f"\n📋 ALL SOURCE FOLDERS FOR PROJECT:")
for sf in all_source_folders:
    print(f"  - {sf.name} (ID: {sf.id}, Type: {sf.folder_type})")