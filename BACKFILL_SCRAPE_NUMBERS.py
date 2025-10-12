#!/usr/bin/env python3
"""
Backfill scrape_number for existing BrightDataScraperRequest records
"""

import os
import sys
import django

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(backend_dir, 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScraperRequest
from collections import defaultdict

def backfill_scrape_numbers():
    """Backfill scrape_number for existing requests"""
    print("🔄 BACKFILLING SCRAPE NUMBERS")
    print("=" * 40)
    
    # Group existing requests by folder_id
    folder_requests = defaultdict(list)
    
    requests = BrightDataScraperRequest.objects.filter(
        scrape_number__isnull=True
    ).order_by('folder_id', 'created_at')
    
    for request in requests:
        if request.folder_id:
            folder_requests[request.folder_id].append(request)
    
    total_updated = 0
    
    for folder_id, requests_list in folder_requests.items():
        print(f"\n📁 Processing folder {folder_id}: {len(requests_list)} requests")
        
        for i, request in enumerate(requests_list, 1):
            request.scrape_number = i
            request.save()
            print(f"   Request {request.id}: set scrape_number = {i}")
            total_updated += 1
    
    print(f"\n✅ Updated {total_updated} scraper requests with scrape numbers")
    
    # Show summary
    print(f"\n📊 SUMMARY BY FOLDER:")
    folders_with_requests = BrightDataScraperRequest.objects.values('folder_id').distinct()
    
    for folder_data in folders_with_requests:
        folder_id = folder_data['folder_id']
        if folder_id:
            max_scrape = BrightDataScraperRequest.objects.filter(
                folder_id=folder_id
            ).aggregate(max_scrape=django.db.models.Max('scrape_number'))['max_scrape']
            
            print(f"   Folder {folder_id}: {max_scrape} scrapes")

if __name__ == "__main__":
    backfill_scrape_numbers()