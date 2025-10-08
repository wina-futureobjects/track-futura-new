#!/usr/bin/env python3
"""
Verify BrightData methods deployment - to be run in production
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.services import BrightDataAutomatedBatchScraper

def verify_deployment():
    print("=== BRIGHTDATA METHODS VERIFICATION ===")
    
    scraper = BrightDataAutomatedBatchScraper()
    
    # Check if methods exist
    has_prepare = hasattr(scraper, '_prepare_request_payload')
    has_execute = hasattr(scraper, '_execute_brightdata_request')
    
    print(f"_prepare_request_payload exists: {has_prepare}")
    print(f"_execute_brightdata_request exists: {has_execute}")
    
    if has_prepare and has_execute:
        print("✅ SUCCESS: All missing methods are now deployed!")
        print("BrightData integration should now work properly.")
        return True
    else:
        print("❌ FAILURE: Methods still missing in deployment.")
        return False

if __name__ == "__main__":
    success = verify_deployment()
    exit(0 if success else 1)