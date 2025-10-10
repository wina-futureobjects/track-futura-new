#!/bin/bash
# URGENT DEPLOYMENT SCRIPT
# Run this on your production server to deploy the fix immediately

echo "🚨 URGENT DEPLOYMENT STARTING..."

# Pull latest changes
cd /app
git pull origin main

# Run the urgent fix
cd backend
python urgent_fix.py

echo "🎉 URGENT DEPLOYMENT COMPLETE!"
echo "✅ Check your URLs now:"
echo "   - Workflow Management: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/workflow-management"
echo "   - Job 104: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/104"
echo "   - Job 103: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/103"