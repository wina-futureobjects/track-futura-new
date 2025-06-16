#!/usr/bin/env python3
"""
Fix the BRIGHTDATA_BASE_URL to use the correct Upsun production URL
"""

import os
import sys

# Add Django project to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# CRITICAL FIX: Set the correct production URL BEFORE Django setup
os.environ['BRIGHTDATA_BASE_URL'] = 'https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site'

import django
django.setup()

from django.conf import settings

def fix_endpoint_url():
    print("🔧 FIXING BRIGHTDATA_BASE_URL")
    print("=" * 60)

    # Show current settings
    print(f"\n📍 BEFORE FIX:")
    print(f"   Environment BRIGHTDATA_BASE_URL: {os.getenv('BRIGHTDATA_BASE_URL')}")
    print(f"   Django settings.BRIGHTDATA_BASE_URL: {settings.BRIGHTDATA_BASE_URL}")

    # The fix is already applied by setting the environment variable above
    print(f"\n✅ AFTER FIX:")
    print(f"   Environment BRIGHTDATA_BASE_URL: {os.getenv('BRIGHTDATA_BASE_URL')}")
    print(f"   Django settings.BRIGHTDATA_BASE_URL: {settings.BRIGHTDATA_BASE_URL}")

    # Verify the fix
    correct_url = 'https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site'
    if settings.BRIGHTDATA_BASE_URL == correct_url:
        print(f"\n🎉 SUCCESS: URL is now correct!")
        print(f"   ✅ Webhook endpoint will be: {settings.BRIGHTDATA_BASE_URL}/api/brightdata/webhook/")
        print(f"   ✅ This matches your working manualrun.py script!")
    else:
        print(f"\n❌ FAILED: URL is still incorrect")
        print(f"   Expected: {correct_url}")
        print(f"   Actual: {settings.BRIGHTDATA_BASE_URL}")

    print(f"\n📋 NEXT STEPS:")
    print(f"   1. Set this environment variable in your production environment:")
    print(f"      export BRIGHTDATA_BASE_URL='{correct_url}'")
    print(f"   2. Restart your Django application")
    print(f"   3. Test the scraper again from your web interface")

    return settings.BRIGHTDATA_BASE_URL == correct_url

if __name__ == "__main__":
    try:
        success = fix_endpoint_url()
        if success:
            print(f"\n✅ ENDPOINT URL FIX SUCCESSFUL!")
        else:
            print(f"\n❌ ENDPOINT URL FIX FAILED!")

    except Exception as e:
        print(f"\n❌ Error during fix: {str(e)}")
        import traceback
        traceback.print_exc()
