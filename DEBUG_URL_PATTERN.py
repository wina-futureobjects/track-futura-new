"""
Debug URL Pattern Matching

This script helps debug why the URL /data-storage/Job%203/1 is not working
"""

# URL Test
test_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/Job%203/1"

print("🔍 URL PATTERN DEBUG")
print("=" * 50)

print(f"Full URL: {test_url}")

# Break down the URL parts
from urllib.parse import urlparse, unquote
parsed = urlparse(test_url)
path_parts = parsed.path.split('/')

print(f"Path: {parsed.path}")
print(f"Path parts: {path_parts}")

# Extract expected parameters
if len(path_parts) >= 8:
    org_id = path_parts[2]
    project_id = path_parts[4] 
    folder_name_encoded = path_parts[6]
    scrape_number = path_parts[7]
    
    folder_name_decoded = unquote(folder_name_encoded)
    
    print(f"\nExtracted parameters:")
    print(f"  organizationId: {org_id}")
    print(f"  projectId: {project_id}")
    print(f"  folderName (encoded): {folder_name_encoded}")
    print(f"  folderName (decoded): {folder_name_decoded}")
    print(f"  scrapeNumber: {scrape_number}")
    
    # Expected API endpoint
    expected_api = f"/api/brightdata/data-storage/{folder_name_encoded}/{scrape_number}/"
    print(f"\nExpected API call: {expected_api}")
    
    # What should happen
    print(f"\nExpected behavior:")
    print(f"1. Route should match: /organizations/:organizationId/projects/:projectId/data-storage/:folderName/:scrapeNumber")
    print(f"2. folderName param = '{folder_name_encoded}'")
    print(f"3. scrapeNumber param = '{scrape_number}'")
    print(f"4. Frontend decodes folderName: '{folder_name_encoded}' → '{folder_name_decoded}'")
    print(f"5. API call: {expected_api}")
    print(f"6. Backend decodes folderName and finds folder: '{folder_name_decoded}'")

print(f"\n✅ URL pattern should work if routing is correct!")