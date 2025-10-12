#!/usr/bin/env python3
"""
Analyze scraping continuity and database relationships
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from brightdata_integration.models import *
from django.db import connection

def analyze_database_schema():
    print('📊 DATABASE SCHEMA ANALYSIS')
    print('=' * 50)
    
    # Check current tables and relationships
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name LIKE '%brightdata%' OR table_name LIKE '%unified%'
            ORDER BY table_name, ordinal_position
        """)
        
        current_table = None
        for row in cursor.fetchall():
            table, column, dtype, nullable = row
            if table != current_table:
                print(f'\n🗃️ Table: {table}')
                current_table = table
            print(f'   {column}: {dtype} ({"NULL" if nullable == "YES" else "NOT NULL"})')

def check_relationships():
    print('\n📈 RELATIONSHIP CHECK')
    print('=' * 30)
    
    # Check foreign key relationships
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND (tc.table_name LIKE '%brightdata%' OR tc.table_name LIKE '%unified%')
        """)
        
        relationships = cursor.fetchall()
        for rel in relationships:
            table, column, foreign_table, foreign_column = rel
            print(f'🔗 {table}.{column} → {foreign_table}.{foreign_column}')

def analyze_scrape_continuity():
    print('\n📋 CURRENT SCRAPING WORKFLOW')
    print('=' * 35)
    
    # Get all folders and their scrape counts
    folders = UnifiedRunFolder.objects.all().order_by('-created_at')
    
    for folder in folders[:10]:  # Show top 10
        scrape_requests = BrightDataScraperRequest.objects.filter(folder=folder).order_by('scrape_number')
        total_posts = BrightDataScrapedPost.objects.filter(scraper_request__folder=folder).count()
        
        print(f'\n📁 Folder: {folder.id} - "{folder.name}"')
        print(f'   Created: {folder.created_at}')
        print(f'   Total scrapes: {scrape_requests.count()}')
        print(f'   Total posts: {total_posts}')
        
        for req in scrape_requests:
            posts_count = BrightDataScrapedPost.objects.filter(scraper_request=req).count()
            print(f'   🔄 Scrape #{req.scrape_number}: {posts_count} posts (Status: {req.status})')

def predict_next_scrape():
    print('\n🎯 NEXT SCRAPE PREDICTION')
    print('=' * 27)
    
    # Find latest folder
    latest_folder = UnifiedRunFolder.objects.order_by('-created_at').first()
    if latest_folder:
        next_scrape_num = BrightDataScraperRequest.objects.filter(folder=latest_folder).count() + 1
        print(f'📁 Latest folder: {latest_folder.id} ({latest_folder.name})')
        print(f'🔄 Next scrape number for this folder: {next_scrape_num}')
        print(f'🌐 Next URL would be: /data-storage/{latest_folder.name.lower()}/{next_scrape_num}/')
        
        # Check if there are any incomplete requests
        incomplete_requests = BrightDataScraperRequest.objects.filter(
            folder=latest_folder,
            status__in=['pending', 'processing']
        )
        
        if incomplete_requests.exists():
            print('⚠️ WARNING: There are incomplete scrape requests!')
            for req in incomplete_requests:
                print(f'   🔄 Request {req.id}: Scrape #{req.scrape_number} - Status: {req.status}')

def check_snapshot_system():
    print('\n📸 SNAPSHOT ID SYSTEM')
    print('=' * 25)
    
    # Check if there's a snapshot tracking system
    try:
        from brightdata_integration.models import BrightDataSnapshot
        snapshots = BrightDataSnapshot.objects.all().order_by('-created_at')[:5]
        print(f'✅ Found {snapshots.count()} snapshots')
        for snapshot in snapshots:
            print(f'📸 Snapshot {snapshot.id}: {snapshot.created_at}')
    except:
        print('❌ No snapshot tracking system found')
        
    # Check if scraper requests have snapshot references
    sample_request = BrightDataScraperRequest.objects.first()
    if sample_request:
        print(f'🔍 Sample request fields: {[field.name for field in sample_request._meta.fields]}')

if __name__ == '__main__':
    analyze_database_schema()
    check_relationships()
    analyze_scrape_continuity() 
    predict_next_scrape()
    check_snapshot_system()