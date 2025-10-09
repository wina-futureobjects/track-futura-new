#!/usr/bin/env python3
"""
🔗 BRIGHTDATA WEBHOOK CONFIGURATION SCRIPT
==========================================

This script provides the webhook URL and configuration instructions
for BrightData dashboard to ensure automatic job creation works properly.

FIXES:
- "failed showing the scraped data" 
- "make sure it returns correct snapshot id"
- Proper webhook configuration for automatic processing
"""

def get_webhook_configuration():
    """Get the webhook configuration details"""
    
    # Production URL (from previous context)
    production_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    webhook_url = f"{production_url}/api/brightdata/webhook/"
    
    print("🔗 BRIGHTDATA WEBHOOK CONFIGURATION")
    print("=" * 40)
    print()
    print(f"📍 WEBHOOK URL TO CONFIGURE:")
    print(f"   {webhook_url}")
    print()
    print("🔧 STEPS IN BRIGHTDATA DASHBOARD:")
    print("   1. Go to your Instagram dataset (gd_lk5ns7kz21pck8jpis)")
    print("   2. Go to your Facebook dataset (gd_lkaxegm826bjpoo9m5)")
    print("   3. Find 'Notify URL' or 'Send to webhook' field")
    print("   4. Enter the webhook URL above")
    print("   5. ✅ Enable 'Send to webhook' checkbox")
    print("   6. Save the configuration")
    print()
    print("🧪 TEST THE WEBHOOK:")
    print("   1. Run a small test scrape")
    print("   2. Check that webhook receives data")
    print("   3. Verify automatic job creation happens")
    print()
    print("🎯 WHAT HAPPENS WITH WEBHOOK CONFIGURED:")
    print("   • BrightData completes scraping")
    print("   • Sends data to your webhook URL")
    print("   • System automatically creates Job folders")
    print("   • Data appears in /data-storage/job/XXX")
    print("   • No manual intervention needed!")
    print()

def show_brightdata_api_example():
    """Show the corrected API example with webhook"""
    
    print("📝 CORRECTED BRIGHTDATA API CONFIGURATION:")
    print("=" * 42)
    print()
    print("In your BrightData API Builder Dashboard:")
    print()
    print("✅ WEBHOOK FIELD:")
    print(f"   Notify URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/")
    print("   ✅ Send to webhook: ENABLED")
    print()
    print("✅ API CALL EXAMPLE:")
    print("""
curl -H "Authorization: Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb" \\
     -H "Content-Type: application/json" \\
     -d '[{
         "url":"https://www.instagram.com/marcusfaberfdp",
         "num_of_posts":10,
         "start_date":"01-01-2025",
         "end_date":"03-01-2025",
         "post_type":"Post"
     }]' \\
     "https://api.brightdata.com/datasets/v3/trigger?dataset_id=gd_lk5ns7kz21pck8jpis"
    """)
    
    print("📊 EXPECTED RESPONSE:")
    print("""
{
    "snapshot_id": "sd_abc123def456",
    "status": "running", 
    "dataset_id": "gd_lk5ns7kz21pck8jpis"
}
    """)
    
    print("🎯 WHAT HAPPENS NEXT:")
    print("   1. BrightData processes the scraping")
    print("   2. When complete, sends data to webhook")
    print("   3. System creates job folder automatically")
    print("   4. Job number follows pattern: 181, 184, 188, 191...")

def create_test_script():
    """Create a test script for the fixes"""
    
    test_script = '''
#!/usr/bin/env python3
"""
🧪 TEST BRIGHTDATA FIXES
=======================
Test the job numbering and snapshot ID fixes
"""

from django.core.management.base import BaseCommand
from brightdata_integration.services import BrightDataAutomatedBatchScraper

class Command(BaseCommand):
    help = 'Test BrightData fixes'

    def handle(self, *args, **options):
        scraper = BrightDataAutomatedBatchScraper()
        
        # Test job numbering
        self.stdout.write("🔢 Testing job numbering pattern...")
        next_job = scraper._get_next_job_number()
        self.stdout.write(f"Next job number: {next_job}")
        
        # Test snapshot ID validation  
        self.stdout.write("🔍 Testing snapshot ID validation...")
        
        test_snapshots = [
            "sd_abc123def456",      # Valid
            "system_batch_created", # Invalid
            "",                     # Invalid
            "bd_batch_1234567890"   # Valid fallback
        ]
        
        for snapshot_id in test_snapshots:
            result = scraper.fetch_brightdata_results(snapshot_id)
            self.stdout.write(f"Snapshot {snapshot_id}: {'✅' if result.get('success') else '❌'}")
'''
    
    print("🧪 TEST SCRIPT FOR FIXES:")
    print("=" * 25)
    print(test_script)
    
    with open('test_brightdata_fixes.py', 'w') as f:
        f.write(test_script)
    
    print("💾 Test script saved as: test_brightdata_fixes.py")

if __name__ == "__main__":
    print("🔧 BRIGHTDATA CONFIGURATION & FIXES")
    print("=" * 37)
    
    get_webhook_configuration()
    print("\n" + "=" * 50 + "\n")
    show_brightdata_api_example()
    print("\n" + "=" * 50 + "\n")
    create_test_script()
    
    print("\n✅ SUMMARY OF FIXES:")
    print("   1. ✅ Fixed job numbering pattern (181, 184, 188, 191...)")
    print("   2. ✅ Enhanced snapshot ID extraction and validation")
    print("   3. ✅ Provided webhook configuration instructions")
    print("   4. ✅ Added debugging for API responses")
    print()
    print("🎯 NEXT STEPS:")
    print("   1. Configure webhook URL in BrightData dashboard")
    print("   2. Test with real scraping job")
    print("   3. Verify automatic job creation with correct numbering")
    print("   4. Check that scraped data appears properly")