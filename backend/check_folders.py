import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from facebook_data.models import Folder as FacebookFolder
from instagram_data.models import Folder as InstagramFolder

print("=== CHECKING FOLDER STRUCTURE ===")
print("Facebook folders:")
for f in FacebookFolder.objects.all():
    folder_type = getattr(f, 'folder_type', 'None')
    posts_count = f.posts.count()
    print(f"  ID {f.id}: {f.name} (type: {folder_type}, posts: {posts_count})")

print("\nInstagram folders:")
for f in InstagramFolder.objects.all():
    folder_type = getattr(f, 'folder_type', 'None') 
    posts_count = f.posts.count()
    print(f"  ID {f.id}: {f.name} (type: {folder_type}, posts: {posts_count})")

# Check if folders have folder_type field
print("\n=== CHECKING FOLDER MODEL FIELDS ===")
fb_fields = [field.name for field in FacebookFolder._meta.get_fields()]
ig_fields = [field.name for field in InstagramFolder._meta.get_fields()]
print(f"Facebook Folder fields: {fb_fields}")
print(f"Instagram Folder fields: {ig_fields}")
print(f"Facebook has folder_type: {'folder_type' in fb_fields}")
print(f"Instagram has folder_type: {'folder_type' in ig_fields}")

# Fix folder_type if missing
print("\n=== FIXING FOLDER TYPES ===")
nike_fb = FacebookFolder.objects.filter(name__icontains='Nike').first()
adidas_fb = FacebookFolder.objects.filter(name__icontains='Adidas').first()

if nike_fb:
    if hasattr(nike_fb, 'folder_type'):
        nike_fb.folder_type = 'company'
        nike_fb.save()
        print(f"✅ Set Nike folder type to 'company'")
    else:
        print("❌ Facebook Folder model doesn't have folder_type field")

if adidas_fb:
    if hasattr(adidas_fb, 'folder_type'):
        adidas_fb.folder_type = 'competitor' 
        adidas_fb.save()
        print(f"✅ Set Adidas folder type to 'competitor'")
    else:
        print("❌ Facebook Folder model doesn't have folder_type field")
