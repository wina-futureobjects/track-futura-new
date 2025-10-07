#!/usr/bin/env python3
"""
BrightData Integration Fix Guide based on API analysis
"""

def brightdata_fix_guide():
    print("=== BRIGHTDATA INTEGRATION FIX GUIDE ===")
    print()
    
    print("✅ GOOD NEWS: Your API key is ACTIVE!")
    print("❌ ISSUE: Zone configuration missing")
    print()
    
    print("🔍 WHAT WE DISCOVERED:")
    print("   • API Key: 8af6995e-3baa-4b69-9df7-8d7671e621eb")
    print("   • Status: ACTIVE")
    print("   • Customer ID: hl_f7614f18")
    print("   • Problem: 'zone_not_found'")
    print()
    
    print("💡 EXPLANATION:")
    print("   BrightData (formerly Luminati) uses a 'Zone' system where:")
    print("   • Each zone has specific settings (Static/Rotating proxy, Country, etc.)")
    print("   • Data collection requires a properly configured zone")
    print("   • You need zone-specific credentials, not just the API key")
    print()
    
    print("🔧 HOW TO FIX:")
    print()
    print("STEP 1: Access Your BrightData Dashboard")
    print("   1. Go to https://brightdata.com/")
    print("   2. Log into your account")
    print("   3. Navigate to your control panel")
    print()
    
    print("STEP 2: Check/Create Zones")
    print("   1. Look for 'Zones' or 'Proxy Zones' in the menu")
    print("   2. Check if you have any existing zones")
    print("   3. If no zones exist, create a new zone:")
    print("      • Zone Type: 'Data Collection' or 'Web Scraping'")
    print("      • Target: Instagram, Facebook, etc.")
    print("      • Settings: Rotating IPs, appropriate country")
    print()
    
    print("STEP 3: Get Zone Credentials")
    print("   1. For each zone, note down:")
    print("      • Zone Name (e.g., 'data_collection_1')")
    print("      • Zone Password")
    print("      • Port number")
    print("      • Endpoint URL")
    print()
    
    print("STEP 4: Common BrightData Authentication Formats")
    print("   Instead of just the API key, you typically need:")
    print("   • Username: customer_id-zone_name")
    print("   • Password: zone_password")
    print("   • Example: 'hl_f7614f18-zone1:zone_password'")
    print()
    
    print("STEP 5: Look for Data Collection APIs")
    print("   BrightData might have separate APIs for:")
    print("   • Proxy service (what we tested)")
    print("   • Data collection/scraping")
    print("   • Collector management")
    print("   Look for sections like:")
    print("   • 'Data Collection'")
    print("   • 'Web Scraping'")
    print("   • 'Collectors'")
    print("   • 'API Documentation'")
    print()
    
    print("📋 INFORMATION TO COLLECT:")
    print("   When you access your dashboard, please note:")
    print("   ✓ Do you have any existing zones?")
    print("   ✓ What are the zone names and passwords?")
    print("   ✓ Is there a 'Data Collection' section?")
    print("   ✓ Are there any pre-built collectors for Instagram/Facebook?")
    print("   ✓ What does the API documentation show for authentication?")
    print()
    
    print("🎯 ONCE YOU HAVE THE ZONE INFO:")
    print("   I can help you update the TrackFutura configuration with:")
    print("   • Correct authentication format")
    print("   • Proper API endpoints")
    print("   • Zone-specific settings")
    print()
    
    print("⚠️  IMPORTANT:")
    print("   Your current API key works for account status,")
    print("   but data collection requires zone-specific credentials.")
    print("   This is normal for BrightData's architecture.")

if __name__ == "__main__":
    brightdata_fix_guide()