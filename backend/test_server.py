#!/usr/bin/env python3

import os
import sys

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

# Test imports
try:
    from apify_integration.models import ApifyBatchJob, ApifyScraperRequest
    from instagram_data.models import Folder, InstagramPost
    print("✅ Models imported successfully")
    
    # Test the API endpoints
    from apify_integration.views import ApifyBatchJobViewSet
    print("✅ Views imported successfully")
    
    # Test basic database queries
    jobs = ApifyBatchJob.objects.all()
    print(f"✅ Found {jobs.count()} batch jobs")
    
    folders = Folder.objects.all()
    posts = InstagramPost.objects.all()
    print(f"✅ Found {folders.count()} folders and {posts.count()} posts")
    
    print("🎉 Backend test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()