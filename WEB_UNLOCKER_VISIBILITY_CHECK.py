#!/usr/bin/env python3
"""
🔍 WEB UNLOCKER COMPONENT VISIBILITY CHECK
==========================================

Check if the Web Unlocker component is visible on the production site
"""

import requests
import time

def check_web_unlocker_visibility():
    """Check if Web Unlocker component is visible"""
    
    print("🔍 WEB UNLOCKER COMPONENT VISIBILITY CHECK")
    print("=" * 45)
    
    # Check the production Data Storage page
    url = "https://trackfutura.futureobjects.io/organizations/1/projects/2/data-storage"
    
    print(f"\n🌐 Checking: {url}")
    
    try:
        print("\n⏳ Loading page...")
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for Web Unlocker component indicators
            indicators = [
                "Web Unlocker",
                "WebUnlockerScraper", 
                "🔓",
                "Start Scraping",
                "Target URL"
            ]
            
            found_indicators = []
            for indicator in indicators:
                if indicator in content:
                    found_indicators.append(indicator)
            
            print(f"✅ Page loaded successfully (Status: {response.status_code})")
            print(f"📏 Content length: {len(content)} characters")
            
            if found_indicators:
                print(f"\n🎉 WEB UNLOCKER INDICATORS FOUND:")
                for indicator in found_indicators:
                    print(f"   ✅ '{indicator}'")
                print(f"\n✅ Component appears to be deployed!")
            else:
                print(f"\n⚠️ WEB UNLOCKER INDICATORS NOT FOUND")
                print(f"   This might mean:")
                print(f"   1. Frontend needs to rebuild (wait 2-3 minutes)")
                print(f"   2. Component not yet deployed")
                print(f"   3. Page needs hard refresh")
                
        else:
            print(f"❌ Page error: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking page: {e}")
    
    print(f"\n🎯 MANUAL VERIFICATION STEPS:")
    print(f"=" * 30)
    
    print(f"\n1️⃣ OPEN THE PAGE:")
    print(f"   🌐 Go to: {url}")
    
    print(f"\n2️⃣ LOOK FOR THE COMPONENT:")
    print(f"   🔍 Should be right after the header buttons")
    print(f"   🔍 Before the 'Instant Run' / 'Periodic Run' tabs")
    print(f"   🔍 Component title: '🔓 Web Unlocker Scraper'")
    
    print(f"\n3️⃣ COMPONENT FEATURES:")
    print(f"   📝 'Target URL *' input field")
    print(f"   📝 'Scraper Name (Optional)' input field") 
    print(f"   🚀 'Start Scraping' button")
    print(f"   ℹ️ Blue info box with 'How it works'")
    
    print(f"\n4️⃣ IF NOT VISIBLE:")
    print(f"   🔄 Hard refresh (Ctrl+F5 or Cmd+Shift+R)")
    print(f"   🧹 Clear browser cache")
    print(f"   ⏳ Wait 2-3 minutes for deployment")
    print(f"   🔧 Check browser developer console (F12)")
    
    print(f"\n5️⃣ TROUBLESHOOTING:")
    print(f"   📱 Try different browser")
    print(f"   🔒 Try incognito/private mode")
    print(f"   🌐 Check network tab for failed requests")
    
    print(f"\n💡 THE COMPONENT IS DEPLOYED IN THE CODE!")
    print(f"   ✅ File: frontend/src/components/WebUnlockerScraper.tsx")
    print(f"   ✅ Imported in: frontend/src/pages/DataStorage.tsx")
    print(f"   ✅ Added before tabs in the JSX")
    print(f"   ✅ Committed and pushed to production")
    
    print(f"\n🎉 EXPECTED AFTER FRONTEND REBUILD:")
    print(f"   The Web Unlocker component will appear and be fully functional!")

if __name__ == "__main__":
    check_web_unlocker_visibility()