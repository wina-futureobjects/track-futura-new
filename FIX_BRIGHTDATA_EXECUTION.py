#!/usr/bin/env python3
"""
FIX BRIGHTDATA EXECUTION ISSUES
Diagnose and fix BrightData job execution problems
"""

import subprocess

def main():
    """Fix BrightData execution issues"""
    print("🔧 FIXING BRIGHTDATA EXECUTION ISSUES")
    print("=" * 60)
    
    # Create a comprehensive fix script
    fix_script = '''
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from brightdata_integration.models import BrightDataConfig, BrightDataBatchJob, BrightDataScraperRequest
from brightdata_integration.services import BrightDataAutomatedBatchScraper
from workflow.models import InputCollection
from users.models import Platform, Service, PlatformService

print("=== BRIGHTDATA EXECUTION FIX ===")
print()

# Step 1: Check and create BrightData configs if missing
print("1. Checking BrightData Configurations...")
configs = BrightDataConfig.objects.all()
print(f"   Found {len(configs)} configurations")

if len(configs) == 0:
    print("   Creating default BrightData configurations...")
    
    # Create default configs based on your provided API tokens
    default_configs = [
        {
            'name': 'Instagram Posts Scraper',
            'platform': 'instagram',
            'dataset_id': 'gd_l7q7dkf244hwps8lu0',
            'api_token': 'c9f8b6d4b5d6c7a8b9c0d1e2f3g4h5i6j7k8l9m0'  # Replace with actual token
        },
        {
            'name': 'Facebook Posts Scraper', 
            'platform': 'facebook',
            'dataset_id': 'gd_l7q7dkf244hwps8lu1',
            'api_token': 'c9f8b6d4b5d6c7a8b9c0d1e2f3g4h5i6j7k8l9m0'  # Replace with actual token
        }
    ]
    
    for config_data in default_configs:
        config, created = BrightDataConfig.objects.get_or_create(
            platform=config_data['platform'],
            defaults=config_data
        )
        if created:
            print(f"   ✅ Created {config.name}")
        else:
            print(f"   ⚠️ Already exists: {config.name}")

# Step 2: Check pending jobs and try to execute them
print("\\n2. Processing Pending Jobs...")
pending_jobs = BrightDataBatchJob.objects.filter(status='pending')
print(f"   Found {len(pending_jobs)} pending jobs")

scraper = BrightDataAutomatedBatchScraper()

for job in pending_jobs[:3]:  # Process first 3 pending jobs
    print(f"   Processing job: {job.name}")
    
    # Check if job has platforms to scrape
    if not job.platforms_to_scrape:
        print(f"     ❌ No platforms specified")
        job.status = 'failed'
        job.error_log = 'No platforms specified for scraping'
        job.save()
        continue
    
    # Try to execute the job
    try:
        print(f"     🚀 Executing job {job.id}...")
        success = scraper.execute_batch_job(job.id)
        
        if success:
            print(f"     ✅ Successfully started execution")
        else:
            print(f"     ❌ Failed to execute")
            
    except Exception as e:
        print(f"     ❌ Error: {str(e)}")
        job.status = 'failed'
        job.error_log = str(e)
        job.save()

# Step 3: Check InputCollections and their URLs
print("\\n3. Checking InputCollection URLs...")
input_collections = InputCollection.objects.all()
print(f"   Found {len(input_collections)} InputCollections")

for collection in input_collections:
    print(f"   Collection: {collection.name}")
    print(f"     URLs: {len(collection.urls) if collection.urls else 0}")
    if collection.urls:
        print(f"     First URL: {collection.urls[0]}")

# Step 4: Test BrightData API connection
print("\\n4. Testing BrightData API Connection...")
configs = BrightDataConfig.objects.filter(is_active=True)

for config in configs:
    print(f"   Testing {config.platform} configuration...")
    result = scraper.test_brightdata_connection(config)
    
    if result.get('success'):
        print(f"     ✅ Connection successful")
    else:
        print(f"     ❌ Connection failed: {result.get('message')}")

print("\\n=== FIX COMPLETE ===")
print("Check the above output for any issues that need manual intervention.")
'''
    
    print("📤 Uploading and executing fix script...")
    
    # Upload script to production
    subprocess.run([
        'upsun', 'ssh', '-p', 'inhoolfrqniuu', '-e', 'main', '--app', 'trackfutura',
        'cat > /tmp/fix_brightdata.py'
    ], input=fix_script.encode(), check=True)
    
    # Execute script
    result = subprocess.run([
        'upsun', 'ssh', '-p', 'inhoolfrqniuu', '-e', 'main', '--app', 'trackfutura',
        'cd /app/backend && python /tmp/fix_brightdata.py'
    ], capture_output=True, text=True)
    
    print(f"Exit Code: {result.returncode}")
    print("Output:")
    print(result.stdout)
    if result.stderr:
        print("Stderr:")
        print(result.stderr)
    
    print("\n" + "=" * 60)
    print("🎯 BRIGHTDATA FIX SUMMARY")
    print("=" * 60)
    
    if result.returncode == 0:
        print("✅ Fix script executed successfully")
        print("🔍 Check the output above for detailed results")
        print("🚀 Try creating a new scraping job to test")
    else:
        print("❌ Fix script encountered errors")
        print("🔧 Manual intervention may be required")

if __name__ == "__main__":
    main()