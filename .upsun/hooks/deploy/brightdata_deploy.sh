#!/bin/bash
# 🚀 Upsun Post Deploy Hook - Deploy BrightData Snapshots to Production
set -e

echo "🚀 POST-DEPLOY: Deploying BrightData Snapshots to Production"

# Change to app directory
cd /app

# Run the BrightData deployment command
python manage.py deploy_brightdata_production

echo "✅ BrightData Production Deployment Complete!"