#!/usr/bin/env python3
"""
Manual database migration to add webhook_delivered field
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

def add_webhook_delivered_field():
    """Manually add webhook_delivered field to production database"""
    
    try:
        with connection.cursor() as cursor:
            # Check if column already exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name='brightdata_integration_brightdatascrapedpost' 
                AND column_name='webhook_delivered'
            """)
            
            exists = cursor.fetchone()[0]
            
            if exists:
                print("✅ webhook_delivered column already exists")
                return True
            
            # Add the column
            cursor.execute("""
                ALTER TABLE brightdata_integration_brightdatascrapedpost 
                ADD COLUMN webhook_delivered boolean DEFAULT false NOT NULL
            """)
            
            print("✅ Successfully added webhook_delivered column to BrightDataScrapedPost table")
            return True
            
    except Exception as e:
        print(f"❌ Error adding webhook_delivered field: {e}")
        return False

if __name__ == "__main__":
    success = add_webhook_delivered_field()
    exit(0 if success else 1)