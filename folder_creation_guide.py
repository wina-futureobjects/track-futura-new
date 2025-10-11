#!/usr/bin/env python3
"""
🎯 FOLDER CREATION GUIDE
========================
How to fill out the UnifiedRunFolder form
"""

def folder_creation_guide():
    print("🎯 FOLDER CREATION GUIDE")
    print("=" * 50)
    
    print("📋 HOW TO FILL OUT THE FORM:")
    print()
    
    print("✅ BASIC INFORMATION:")
    print("   Name: Job Folder 216")
    print("   Description: (leave empty or add: 'BrightData scraping job folder')")
    print()
    
    print("✅ FOLDER TYPE & CATEGORY:")
    print("   Folder type: Content")
    print("   Category: Posts")
    print()
    
    print("✅ PLATFORM & SERVICE:")
    print("   Platform code: Instagram")
    print("   Service code: Posts")
    print()
    
    print("🚨 RELATIONSHIPS (CRITICAL):")
    print("   Project: LEAVE EMPTY (remove '216')")
    print("   Scraping run: LEAVE EMPTY")
    print("   Parent folder: LEAVE EMPTY")
    print()
    
    print("🎯 THE ISSUE:")
    print("The 'Project: 216' field is causing the error!")
    print("This should be EMPTY, not '216'")
    print()
    
    print("📝 CORRECT FORM VALUES:")
    print("=" * 30)
    print("Name: Job Folder 216")
    print("Description: (empty)")
    print("Folder type: Content")
    print("Category: Posts")
    print("Platform code: Instagram")
    print("Service code: Posts")
    print("Project: (EMPTY - clear this field!)")
    print("Scraping run: (empty)")
    print("Parent folder: (empty)")

def after_folder_creation():
    print("\n🎉 AFTER CREATING FOLDER 216:")
    print("=" * 50)
    
    print("1. Create folder 219 with same settings:")
    print("   Name: Job Folder 219")
    print("   Everything else same as folder 216")
    print("   Project: (EMPTY)")
    
    print("\n2. Test the webhook:")
    print("   Run our test script to verify data appears")

def main():
    folder_creation_guide()
    after_folder_creation()
    
    print("\n🚨 KEY POINT:")
    print("=" * 50)
    print("CLEAR the 'Project: 216' field - it should be EMPTY!")
    print("That's what's causing the 'This field is required' error.")

if __name__ == "__main__":
    main()