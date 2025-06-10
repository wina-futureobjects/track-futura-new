#!/bin/bash

echo "🚨 UPSUN EMERGENCY FIX - Folder 46 Data Assignment"
echo "=================================================="

echo ""
echo "1. 🖥️  SSH into Upsun (run this command):"
echo "upsun ssh"

echo ""
echo "2. 🐍 Once in Upsun SSH, run Django shell:"
echo "cd /app && python manage.py shell"

echo ""
echo "3. 📝 In Django shell, run this Python code:"
echo ""
echo "# === COPY AND PASTE THIS INTO DJANGO SHELL ==="
cat << 'EOF'
from instagram_data.models import Folder, InstagramPost
from brightdata_integration.models import ScraperRequest, BrightdataConfig

print("🔍 Checking folder 46...")
try:
    folder = Folder.objects.get(id=46)
    print(f"✅ Found folder: {folder.name}")
    print(f"   Created: {folder.created_at}")
    print(f"   Current posts: {folder.instagrampost_set.count()}")
except:
    print("❌ Folder 46 not found!")
    exit()

print("\n🔍 Checking BrightData config...")
config = BrightdataConfig.objects.first()
if not config:
    print("❌ No BrightData config found!")
    print("Creating default config...")
    config = BrightdataConfig.objects.create(
        name="Default Config",
        config_id="default_config"
    )
    print(f"✅ Created config: {config.name}")
else:
    print(f"✅ Found config: {config.name}")

print("\n🔍 Checking existing ScraperRequests...")
existing_requests = ScraperRequest.objects.filter(folder=folder)
print(f"Found {existing_requests.count()} existing ScraperRequests for folder 46")

print("\n🔧 Creating emergency ScraperRequest...")
# Using a generic request_id - replace with actual BrightData job ID
emergency_request = ScraperRequest.objects.create(
    config=config,
    folder=folder,
    request_id=f"emergency_fix_folder_46_{folder.id}",
    platform="instagram",
    status="completed"
)
print(f"✅ Created emergency ScraperRequest: {emergency_request.id}")
print(f"   Request ID: {emergency_request.request_id}")
print(f"   Folder: {emergency_request.folder.name}")

print("\n🎯 NEXT: Update this request_id in BrightData webhook!")
print(f"   Use this X-Snapshot-Id in BrightData: {emergency_request.request_id}")

print("\n📊 Summary:")
print(f"   Folder 46: {folder.name}")
print(f"   Current posts: {folder.instagrampost_set.count()}")
print(f"   ScraperRequest ID: {emergency_request.request_id}")
EOF

echo ""
echo "4. 🎯 After creating ScraperRequest, update BrightData:"
echo "   - Go to your BrightData dashboard"
echo "   - Find the scraper that should send data to folder 46"
echo "   - Set X-Snapshot-Id header to the request_id shown above"

echo ""
echo "5. 🧪 Test the webhook:"
echo "   - Run another Instagram scraping job"
echo "   - Check if data appears in folder 46"

echo ""
echo "6. 📋 Alternative: Use actual BrightData job ID"
echo "   - Find your actual BrightData job ID from the dashboard"
echo "   - Update the ScraperRequest:"
echo ""
echo "   emergency_request.request_id = 'YOUR_ACTUAL_BRIGHTDATA_JOB_ID'"
echo "   emergency_request.save()"
echo "   print(f'Updated request_id to: {emergency_request.request_id}')"

echo ""
echo "🎉 EXPECTED RESULT:"
echo "   - Webhook will receive data with X-Snapshot-Id"
echo "   - Match ScraperRequest by request_id"
echo "   - Assign InstagramPost objects to folder 46"
echo "   - Data appears in your folder!"
