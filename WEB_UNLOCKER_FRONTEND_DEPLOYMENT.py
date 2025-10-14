#!/usr/bin/env python3
"""
🚀 WEB UNLOCKER FRONTEND DEPLOYMENT
===================================

Deploy the Web Unlocker component to production frontend
"""

import subprocess
import os

def deploy_web_unlocker_frontend():
    """Deploy Web Unlocker frontend component"""
    
    print("🚀 WEB UNLOCKER FRONTEND DEPLOYMENT")
    print("=" * 40)
    
    print("\n📋 DEPLOYMENT STEPS:")
    print("=" * 20)
    
    print("\n1️⃣ BUILD FRONTEND:")
    print("   Building React app with Web Unlocker component...")
    
    # Change to frontend directory
    frontend_dir = "frontend"
    if os.path.exists(frontend_dir):
        os.chdir(frontend_dir)
        print(f"   📁 Changed to: {os.getcwd()}")
        
        # Install dependencies
        print("\n   📦 Installing dependencies...")
        try:
            subprocess.run(["npm", "install"], check=True, capture_output=True)
            print("   ✅ Dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️ npm install warning: {e}")
        
        # Build the frontend
        print("\n   🔨 Building production frontend...")
        try:
            result = subprocess.run(["npm", "run", "build"], check=True, capture_output=True, text=True)
            print("   ✅ Frontend build completed")
            print(f"   📊 Build output: {result.stdout[:200]}...")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Build error: {e}")
            print(f"   📋 Error output: {e.stderr}")
        
        # Go back to root directory
        os.chdir("..")
        print(f"   📁 Back to: {os.getcwd()}")
        
    else:
        print("   ❌ Frontend directory not found")
    
    print("\n2️⃣ UPSUN DEPLOYMENT:")
    print("   Deploying to production...")
    
    # Deploy to Upsun
    try:
        result = subprocess.run(["upsun", "push"], check=True, capture_output=True, text=True)
        print("   ✅ Deployed to Upsun successfully")
        print(f"   📊 Deploy output: {result.stdout[:300]}...")
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️ Upsun deployment: {e}")
        print("   💡 Manual deployment may be needed")
    except FileNotFoundError:
        print("   ⚠️ Upsun CLI not found - using git push for deployment")
        
        # Alternative: trigger deployment via git push
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "🚀 Deploy Web Unlocker frontend component"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("   ✅ Changes pushed - deployment should trigger automatically")
        except subprocess.CalledProcessError:
            print("   📋 No new changes to deploy")
    
    print("\n3️⃣ VERIFICATION:")
    print("   Web Unlocker component should now be visible at:")
    print("   https://trackfutura.futureobjects.io/organizations/1/projects/2/data-storage")
    
    print("\n🔍 TROUBLESHOOTING:")
    print("=" * 18)
    
    print("\n❓ If component still not visible:")
    print("   1. 🔄 Hard refresh the page (Ctrl+F5)")
    print("   2. 🧹 Clear browser cache")
    print("   3. ⏳ Wait 2-3 minutes for deployment")
    print("   4. 📱 Check browser console for errors")
    
    print("\n✅ COMPONENT FEATURES:")
    print("   🔓 Web Unlocker Scraper title")
    print("   📝 URL input field")
    print("   📝 Scraper name field (optional)")
    print("   🚀 'Start Scraping' button")
    print("   ℹ️ 'How it works' instructions")
    
    print("\n🎯 EXPECTED LOCATION:")
    print("   The component should appear at the top of the Data Storage page,")
    print("   right after the header buttons and before the tabs.")

if __name__ == "__main__":
    deploy_web_unlocker_frontend()