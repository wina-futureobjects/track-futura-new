#!/bin/bash

# BRIGHTDATA STORAGE FIX DEPLOYMENT
# This script deploys the fix that ensures scraped data appears in Data Storage

echo "🚀 Deploying BrightData Storage Fix..."
echo ""
echo "This fix ensures that:"
echo "  ✅ UnifiedRunFolder is created BEFORE scraping"
echo "  ✅ BrightDataScraperRequest links to folder_id"
echo "  ✅ Webhook can save posts to correct folder"
echo "  ✅ Data appears in Data Storage page"
echo ""

# Check if we have uncommitted changes
if ! git diff --quiet backend/workflow/views.py; then
    echo "📝 Detected changes in backend/workflow/views.py"

    # Show what changed
    echo ""
    echo "Changes to be committed:"
    git diff --stat backend/workflow/views.py
    echo ""

    # Stage the changes
    git add backend/workflow/views.py
    echo "✅ Staged workflow/views.py"

    # Commit with descriptive message
    git commit -m "FIX: Create UnifiedRunFolder before BrightData scraping

- Create UnifiedRunFolder with proper folder_type and platform_code
- Create BrightDataScraperRequest with folder_id for each URL
- Link webhook results to folder via folder_id
- Add cleanup on error (delete folder if scrape fails)
- Return folder_id and data_storage_url in response

This fixes the issue where scraped data from BrightData
was not appearing in the Data Storage page because no
UnifiedRunFolder was created to store the results."

    echo "✅ Committed changes"
else
    echo "⚠️ No changes detected in backend/workflow/views.py"
    echo "   The fix may already be deployed or needs to be applied first."
    exit 1
fi

echo ""
echo "📤 Pushing to Upsun production..."
git push upsun main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ DEPLOYMENT SUCCESSFUL!"
    echo ""
    echo "🧪 Next Steps:"
    echo "1. Wait 1-2 minutes for deployment to complete"
    echo "2. Test workflow: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/workflow-management"
    echo "3. Start a scrape and note the folder_id in response"
    echo "4. Wait 2-5 minutes for BrightData webhook"
    echo "5. Check Data Storage: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage"
    echo "6. Verify scraped posts appear in the folder"
    echo ""
    echo "📊 Monitor logs with: upsun log --app backend --tail"
else
    echo ""
    echo "❌ DEPLOYMENT FAILED"
    echo "Please check your git configuration and Upsun remote."
    exit 1
fi
