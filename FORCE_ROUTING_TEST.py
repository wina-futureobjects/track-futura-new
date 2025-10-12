"""
FORCE CORRECT URL ROUTING - Direct Override

This creates a direct override to force the correct routing behavior
"""

# Create a simple test to verify our logic
test_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/Job%203/1"

print("🔧 DIRECT URL ROUTING TEST")
print("=" * 50)

# Simulate the URL parsing
from urllib.parse import unquote

path = "/organizations/1/projects/1/data-storage/Job%203/1"
parts = path.split('/')

print(f"URL Path: {path}")
print(f"Path Parts: {parts}")

if len(parts) >= 8:
    data_storage_idx = parts.index('data-storage')  
    segment1 = parts[data_storage_idx + 1]   # 'Job%203'
    segment2 = parts[data_storage_idx + 2]   # '1'
    
    print(f"Segment 1 (raw): {segment1}")
    print(f"Segment 1 (decoded): {unquote(segment1)}")
    print(f"Segment 2: {segment2}")
    
    # Check if segment2 is number
    is_number = segment2.isdigit()
    print(f"Segment 2 is number: {is_number}")
    
    if is_number:
        print("✅ SHOULD route to JobFolderView")
        print(f"✅ SHOULD call: /api/brightdata/data-storage/{segment1}/{segment2}/")
    else:
        print("❌ Would route to FolderContents")
        print(f"❌ Would call: /api/{segment1}/data/folders/{segment2}/")

print("\n🎯 EXPECTED BEHAVIOR:")
print("1. SmartDataStorageRouter should detect '1' as number")
print("2. Should route to JobFolderView") 
print("3. JobFolderView should call BrightData API")
print("4. Should NOT call /api/Job%203-data/folders/1/")