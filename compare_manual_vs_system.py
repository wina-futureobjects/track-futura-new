#!/usr/bin/env python3
"""
Comprehensive comparison between manualrun.py and web system scraper
"""

import os
import sys
import json
from urllib.parse import urlencode

# Add Django project to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from brightdata_integration.models import BrightdataConfig
from django.conf import settings

def analyze_manual_vs_system():
    print("🔍 COMPREHENSIVE COMPARISON: manualrun.py vs Web System")
    print("=" * 80)

    # ===== MANUAL RUN SCRIPT ANALYSIS =====
    print("\n📄 MANUAL RUN SCRIPT (manualrun.py):")
    print("-" * 50)

    manual_script = {
        "url": "https://api.brightdata.com/datasets/v3/trigger",
        "headers": {
            "Authorization": "Bearer c20a28d5-5c6c-43c3-9567-a6d7c193e727",
            "Content-Type": "application/json",
        },
        "params": {
            "dataset_id": "gd_lk5ns7kz21pck8jpis",
            "endpoint": "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/",
            "format": "json",
            "uncompressed_webhook": "true",
            "include_errors": "true",
            "type": "discover_new",
            "discover_by": "url",
        },
        "data": [
            {
                "url": "https://www.instagram.com/oneshift",
                "num_of_posts": 2,
                "start_date": "01-01-2025",
                "end_date": "06-16-2025",
                "post_type": "Post"
            }
        ]
    }

    print(f"URL: {manual_script['url']}")
    print(f"Authorization: {manual_script['headers']['Authorization']}")
    print(f"Dataset ID: {manual_script['params']['dataset_id']}")
    print(f"Endpoint: {manual_script['params']['endpoint']}")
    print(f"Parameters: {len(manual_script['params'])} total")
    print(f"Data payload: {len(manual_script['data'])} items")

    # ===== WEB SYSTEM ANALYSIS =====
    print("\n🌐 WEB SYSTEM CONFIGURATION:")
    print("-" * 50)

    # Check database configuration
    config = BrightdataConfig.objects.filter(platform='instagram_posts', is_active=True).first()

    if not config:
        print("❌ NO ACTIVE INSTAGRAM CONFIGURATION FOUND!")
        print("   This is likely the main issue.")
        return

    print(f"Config Name: {config.name}")
    print(f"Config ID: {config.id}")
    print(f"Platform: {config.platform}")
    print(f"Dataset ID: {config.dataset_id}")
    print(f"API Token: {config.api_token[:20]}...{config.api_token[-4:]}")
    print(f"Is Active: {config.is_active}")

    # Check Django settings
    base_url = getattr(settings, 'BRIGHTDATA_BASE_URL', 'http://localhost:8000')
    webhook_token = getattr(settings, 'BRIGHTDATA_WEBHOOK_TOKEN', 'your-webhook-secret-token')

    print(f"\nDjango Settings:")
    print(f"BRIGHTDATA_BASE_URL: {base_url}")
    print(f"BRIGHTDATA_WEBHOOK_TOKEN: {webhook_token}")

    # Simulate web system request
    web_system = {
        "url": "https://api.brightdata.com/datasets/v3/trigger",
        "headers": {
            "Authorization": f"Bearer {config.api_token}",
            "Content-Type": "application/json",
        },
        "params": {
            "dataset_id": config.dataset_id,
            "endpoint": f"{base_url}/api/brightdata/webhook/",
            "format": "json",
            "uncompressed_webhook": "true",
            "include_errors": "true",
            "type": "discover_new",
            "discover_by": "url",
        },
        "data": [
            {
                "url": "https://www.instagram.com/someaccount",  # Example
                "num_of_posts": 10,  # Default
                "start_date": "01-01-2025",
                "end_date": "06-16-2025",
                "post_type": "Post",
                "posts_to_not_include": []  # Extra field
            }
        ]
    }

    # ===== DETAILED COMPARISON =====
    print("\n🔍 DETAILED COMPARISON:")
    print("=" * 80)

    # 1. URL Comparison
    print("\n1. API URL:")
    if manual_script['url'] == web_system['url']:
        print("   ✅ IDENTICAL")
    else:
        print("   ❌ DIFFERENT")
        print(f"   Manual: {manual_script['url']}")
        print(f"   System: {web_system['url']}")

    # 2. Headers Comparison
    print("\n2. HEADERS:")
    manual_auth = manual_script['headers']['Authorization']
    system_auth = web_system['headers']['Authorization']

    if manual_auth == system_auth:
        print("   ✅ Authorization tokens IDENTICAL")
    else:
        print("   ❌ Authorization tokens DIFFERENT")
        print(f"   Manual: {manual_auth}")
        print(f"   System: {system_auth}")

    # 3. Parameters Comparison
    print("\n3. PARAMETERS:")
    param_differences = []

    for key in set(list(manual_script['params'].keys()) + list(web_system['params'].keys())):
        manual_val = manual_script['params'].get(key, "MISSING")
        system_val = web_system['params'].get(key, "MISSING")

        if manual_val != system_val:
            param_differences.append({
                'key': key,
                'manual': manual_val,
                'system': system_val
            })
            print(f"   ❌ {key}:")
            print(f"      Manual: {manual_val}")
            print(f"      System: {system_val}")
        else:
            print(f"   ✅ {key}: IDENTICAL")

    # 4. Data Payload Comparison
    print("\n4. DATA PAYLOAD:")
    manual_data = manual_script['data'][0]
    system_data = web_system['data'][0]

    data_differences = []

    for key in set(list(manual_data.keys()) + list(system_data.keys())):
        manual_val = manual_data.get(key, "MISSING")
        system_val = system_data.get(key, "MISSING")

        if manual_val != system_val:
            data_differences.append({
                'key': key,
                'manual': manual_val,
                'system': system_val
            })
            print(f"   ⚠️  {key}:")
            print(f"      Manual: {manual_val}")
            print(f"      System: {system_val}")
        else:
            print(f"   ✅ {key}: IDENTICAL")

    # ===== SUMMARY AND RECOMMENDATIONS =====
    print("\n" + "=" * 80)
    print("📋 SUMMARY AND RECOMMENDATIONS")
    print("=" * 80)

    critical_issues = []
    minor_issues = []

    # Check critical issues
    if manual_auth != system_auth:
        critical_issues.append("API Token mismatch")

    if manual_script['params']['dataset_id'] != web_system['params']['dataset_id']:
        critical_issues.append("Dataset ID mismatch")

    if manual_script['params']['endpoint'] != web_system['params']['endpoint']:
        critical_issues.append("Endpoint URL mismatch")

    # Check minor issues
    if len(param_differences) > len(critical_issues):
        minor_issues.append(f"{len(param_differences) - len(critical_issues)} parameter differences")

    if len(data_differences) > 0:
        minor_issues.append(f"{len(data_differences)} data payload differences")

    print(f"\n🚨 CRITICAL ISSUES ({len(critical_issues)}):")
    if critical_issues:
        for issue in critical_issues:
            print(f"   ❌ {issue}")
    else:
        print("   ✅ No critical issues found!")

    print(f"\n⚠️  MINOR ISSUES ({len(minor_issues)}):")
    if minor_issues:
        for issue in minor_issues:
            print(f"   ⚠️  {issue}")
    else:
        print("   ✅ No minor issues found!")

    # ===== SPECIFIC FIXES =====
    print("\n🛠️  SPECIFIC FIXES NEEDED:")
    print("-" * 40)

    if critical_issues:
        if "API Token mismatch" in critical_issues:
            print("1. Fix API Token in database:")
            print(f"   UPDATE: config.api_token = 'c20a28d5-5c6c-43c3-9567-a6d7c193e727'")

        if "Dataset ID mismatch" in critical_issues:
            print("2. Fix Dataset ID in database:")
            print(f"   UPDATE: config.dataset_id = 'gd_lk5ns7kz21pck8jpis'")

        if "Endpoint URL mismatch" in critical_issues:
            print("3. Fix Django settings:")
            print(f"   UPDATE: BRIGHTDATA_BASE_URL = 'https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site'")
    else:
        print("✅ No critical fixes needed! The configurations match.")
        print("\n🤔 If the scraper still doesn't work, the issue might be:")
        print("   1. Network connectivity to BrightData")
        print("   2. Instagram account URLs in your system")
        print("   3. Webhook processing on your server")
        print("   4. Database write permissions")

    return {
        'critical_issues': critical_issues,
        'minor_issues': minor_issues,
        'config': config,
        'manual_script': manual_script,
        'web_system': web_system
    }

if __name__ == "__main__":
    try:
        result = analyze_manual_vs_system()

        print("\n" + "=" * 80)
        print("🏁 ANALYSIS COMPLETE")
        print("=" * 80)

        if result and result['critical_issues']:
            print("\n❌ CRITICAL ISSUES FOUND - These must be fixed for the scraper to work!")
        elif result:
            print("\n✅ NO CRITICAL ISSUES - Configuration looks correct!")

    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        print("   Make sure Django is properly configured.")
        import traceback
        traceback.print_exc()
