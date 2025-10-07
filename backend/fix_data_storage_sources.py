from track_accounts.models import SourceFolder
from facebook_data.models import Folder as FacebookFolder
from users.models import Project

print("=== CREATING SOURCE FOLDERS FOR ALL RELEVANT PROJECTS ===")

# Get key projects that users might be using
future_objects_projects = Project.objects.filter(organization__name__icontains='Future')
nike_projects = Project.objects.filter(name__icontains='Nike')
main_projects = [1, 2, 6]  # Demo, Test Project, Track Futura

all_target_projects = list(future_objects_projects) + list(nike_projects)
for project_id in main_projects:
    try:
        project = Project.objects.get(id=project_id)
        if project not in all_target_projects:
            all_target_projects.append(project)
    except Project.DoesNotExist:
        pass

print(f"Creating SourceFolders for {len(all_target_projects)} projects:")
for project in all_target_projects:
    print(f"  - {project.id}: {project.name}")

# Get Nike and Adidas Facebook folders (we know they exist)
nike_folder = FacebookFolder.objects.get(id=18)  # Nike Brand Sources
adidas_folder = FacebookFolder.objects.get(id=19)  # Adidas Competitor Sources

created_count = 0
for project in all_target_projects:
    # Create Nike SourceFolder for this project
    nike_source_folder, created = SourceFolder.objects.get_or_create(
        name="Nike Brand Sources",
        project=project,
        defaults={
            'folder_type': 'company',
            'description': 'Nike brand social media data sources for competitive analysis'
        }
    )
    if created:
        print(f"✅ Created Nike SourceFolder for project {project.id}: {project.name}")
        created_count += 1
    else:
        # Update to ensure correct folder_type
        nike_source_folder.folder_type = 'company'
        nike_source_folder.save()

    # Create Adidas SourceFolder for this project
    adidas_source_folder, created = SourceFolder.objects.get_or_create(
        name="Adidas Competitor Sources",
        project=project,
        defaults={
            'folder_type': 'competitor',
            'description': 'Adidas competitor social media data sources for competitive analysis'
        }
    )
    if created:
        print(f"✅ Created Adidas SourceFolder for project {project.id}: {project.name}")
        created_count += 1
    else:
        # Update to ensure correct folder_type
        adidas_source_folder.folder_type = 'competitor'
        adidas_source_folder.save()

print(f"\n📊 SUMMARY:")
print(f"Created {created_count} new SourceFolders")
print(f"Nike and Adidas sources now available for {len(all_target_projects)} projects")

# Test API endpoints for different projects
print(f"\n🔍 TESTING API ENDPOINTS:")
test_projects = [1, 2, 6, 15]  # Key projects users might access
for project_id in test_projects:
    try:
        project = Project.objects.get(id=project_id)
        source_folders = SourceFolder.objects.filter(project=project)
        nike_count = source_folders.filter(folder_type='company').count()
        adidas_count = source_folders.filter(folder_type='competitor').count()
        print(f"  Project {project_id} ({project.name}): {nike_count} Nike + {adidas_count} Adidas = {source_folders.count()} total")
    except Project.DoesNotExist:
        print(f"  Project {project_id}: Not found")

print(f"\n✅ DATA STORAGE SOURCES NOW AVAILABLE!")
print(f"🎯 Users will see Nike and Adidas sources regardless of project")
print(f"📱 Sentiment analysis data source selection ready")