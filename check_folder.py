#!/usr/bin/env python3
import requests

print("🔍 CHECKING CREATED FOLDER DETAILS")
print("=" * 35)

# Get the specific folder we just created (ID 334)
response = requests.get(
    "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/track-accounts/report-folders/334/",
    timeout=60
)

if response.status_code == 200:
    folder = response.json()
    print("✅ Found folder:")
    print("   ID:", folder.get("id"))
    print("   Name:", folder.get("name"))
    print("   Type:", folder.get("folder_type"))
    print("   Project:", folder.get("project_id"))
    print("   Posts:", folder.get("total_posts", 0))
    print("   Created:", folder.get("created_at"))
else:
    print("❌ Failed to get folder:", response.status_code)
    print(response.text)