#!/usr/bin/env python3
"""
BrightData Integration Troubleshooting Guide
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dotenv import load_dotenv

def brightdata_troubleshooting_guide():
    print("=== BRIGHTDATA INTEGRATION TROUBLESHOOTING ===")
    print()
    
    # Load environment
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(env_file)
    
    api_key = os.getenv('BRIGHTDATA_API_KEY')
    webhook_token = os.getenv('BRIGHTDATA_WEBHOOK_TOKEN')
    
    print("🔍 CURRENT CONFIGURATION:")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else api_key}")
    print(f"   Webhook Token: {webhook_token[:10]}...{webhook_token[-4:] if webhook_token and len(webhook_token) > 14 else webhook_token}")
    print()
    
    print("❌ ISSUE IDENTIFIED:")
    print("   The BrightData API endpoints are returning 404 errors.")
    print("   This suggests one of the following problems:")
    print()
    
    print("🔧 POSSIBLE CAUSES & SOLUTIONS:")
    print()
    
    print("1. 📋 INCORRECT API ENDPOINT FORMAT:")
    print("   - BrightData may use a different API base URL")
    print("   - Common formats:")
    print("     * https://api.brightdata.com/")
    print("     * https://api.brightdata.com/v1/")
    print("     * https://api.brightdata.io/")
    print("     * https://brightdata.com/api/")
    print()
    
    print("2. 🔑 API KEY FORMAT ISSUE:")
    print("   - Your API key might be in the wrong format")
    print("   - BrightData might require:")
    print("     * Username:Password format")
    print("     * Zone credentials instead of API key")
    print("     * Different authentication header")
    print()
    
    print("3. 📊 DATASET/COLLECTOR CONFIGURATION:")
    print("   - You might need to create collectors in BrightData dashboard first")
    print("   - Dataset IDs might be in a different format")
    print("   - BrightData might use 'collector' instead of 'dataset'")
    print()
    
    print("🎯 IMMEDIATE ACTION REQUIRED:")
    print()
    print("Please check your BrightData dashboard and:")
    print()
    print("1. ✅ VERIFY API CREDENTIALS:")
    print("   - Log into your BrightData account")
    print("   - Go to Settings > API Access")
    print("   - Check if your API key format is correct")
    print("   - Look for any API documentation or examples")
    print()
    
    print("2. ✅ CHECK COLLECTOR SETUP:")
    print("   - Go to Data Collection > Collectors")
    print("   - Create collectors for Instagram, Facebook, etc. if they don't exist")
    print("   - Note down the collector IDs")
    print()
    
    print("3. ✅ FIND CORRECT API ENDPOINTS:")
    print("   - Check BrightData documentation for correct API URLs")
    print("   - Look for 'trigger' or 'collect' endpoints")
    print("   - Verify authentication method (Bearer token vs Basic auth)")
    print()
    
    print("4. ✅ UPDATE CONFIGURATION:")
    print("   Once you have the correct information, update with:")
    print("   ```")
    print("   python manage.py shell")
    print("   from brightdata_integration.models import BrightDataConfig")
    print("   config = BrightDataConfig.objects.first()")
    print("   config.api_token = 'your_correct_api_token'")
    print("   config.dataset_id = 'your_correct_collector_id'")
    print("   config.save()")
    print("   ```")
    print()
    
    print("🔗 BRIGHTDATA RESOURCES:")
    print("   - Documentation: https://docs.brightdata.com/")
    print("   - API Reference: https://docs.brightdata.com/api-reference")
    print("   - Support: Contact BrightData support for API endpoint clarification")
    print()
    
    print("⚠️  CURRENT STATUS:")
    print("   - ❌ BrightData integration is NOT working")
    print("   - ❌ Scraping jobs will not appear in BrightData dashboard")
    print("   - ✅ TrackFutura system is otherwise functional")
    print("   - 🔧 Requires BrightData account configuration")

if __name__ == "__main__":
    brightdata_troubleshooting_guide()