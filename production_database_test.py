#!/usr/bin/env python3
"""
🚨 PRODUCTION DATABASE TEST
===========================
Test database writes directly in production
"""

def create_production_database_test():
    print("🚨 PRODUCTION DATABASE TEST")
    print("=" * 50)
    
    # Commands to run in production
    commands = [
        {
            "name": "Check BrightData tables exist",
            "command": "psql -c \"\\dt brightdata_integration_*\""
        },
        {
            "name": "Check webhook events table structure",
            "command": "psql -c \"\\d brightdata_integration_brightdatawebhookevent\""
        },
        {
            "name": "Check scraped posts table structure", 
            "command": "psql -c \"\\d brightdata_integration_brightdatascrapedpost\""
        },
        {
            "name": "Test manual webhook event insert",
            "command": """psql -c "INSERT INTO brightdata_integration_brightdatawebhookevent (platform, event_type, status, raw_data, created_at) VALUES ('test', 'webhook', 'received', '{}', NOW()) RETURNING id;\""""
        },
        {
            "name": "Test manual scraped post insert",
            "command": """psql -c "INSERT INTO brightdata_integration_brightdatascrapedpost (post_id, url, content, platform, folder_id, created_at) VALUES ('TEST_001', 'https://test.com', 'Test content', 'instagram', 216, NOW()) RETURNING id;\""""
        },
        {
            "name": "Check Django migrations status",
            "command": "python manage.py showmigrations brightdata_integration"
        },
        {
            "name": "Check recent webhook events",
            "command": "psql -c \"SELECT id, platform, event_type, status, created_at FROM brightdata_integration_brightdatawebhookevent ORDER BY created_at DESC LIMIT 5;\""
        },
        {
            "name": "Check recent scraped posts",
            "command": "psql -c \"SELECT id, post_id, platform, folder_id, created_at FROM brightdata_integration_brightdatascrapedpost ORDER BY created_at DESC LIMIT 5;\""
        }
    ]
    
    print("🛠️ RUN THESE COMMANDS IN PRODUCTION:")
    print("=" * 50)
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n{i}. {cmd['name']}:")
        print(f"   upsun ssh -p inhoolfrqniuu -e main --app trackfutura '{cmd['command']}'")
    
    print(f"\n📋 WHAT TO LOOK FOR:")
    print("=" * 50)
    
    print("✅ SUCCESS INDICATORS:")
    print("   • Tables exist and have correct structure")
    print("   • Manual INSERTs succeed and return IDs")
    print("   • All migrations are applied")
    
    print("\n❌ FAILURE INDICATORS:")
    print("   • Tables missing or wrong structure")
    print("   • Permission denied on INSERT")
    print("   • Unapplied migrations")
    print("   • Constraint violations")
    
    print(f"\n🎯 EXPECTED ISSUES:")
    print("   1. Missing migrations - tables don't exist")
    print("   2. Permission issues - can't INSERT")
    print("   3. Schema mismatch - wrong column types")
    print("   4. Foreign key constraints - invalid folder_id")

def main():
    create_production_database_test()
    
    print(f"\n🚨 CRITICAL DIAGNOSIS:")
    print("=" * 60)
    print("The webhook processes successfully but NO data gets saved.")
    print("This is definitely a database write failure in production.")
    print("\nRun the commands above to identify the exact database issue.")

if __name__ == "__main__":
    main()