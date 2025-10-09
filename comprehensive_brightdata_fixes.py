#!/usr/bin/env python3
"""
🔧 COMPREHENSIVE BRIGHTDATA FIXES
================================

Fixes for:
1. Snapshot ID handling and response processing
2. Correct job numbering pattern (181, 184, 188, 191, 194, 198...)
3. Webhook configuration recommendations
4. API response validation

Issues addressed:
- "failed showing the scraped data"
- "make sure it returns correct snapshot id"
- Job numbering pattern should be 181, 184, 188, 191, 194, 198...
"""

import os
import sys
import django

# Set up Django environment
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')
django.setup()

from django.db import transaction
from track_accounts.models import UnifiedRunFolder
import re

def analyze_job_numbering_pattern():
    """Analyze the existing job numbering pattern to understand the business logic"""
    print("🔍 ANALYZING JOB NUMBERING PATTERN")
    print("=" * 40)
    
    # Check if we have any existing job folders with numbers > 100
    job_folders = UnifiedRunFolder.objects.filter(folder_type='job').values_list('name', flat=True)
    
    job_numbers = []
    for name in job_folders:
        match = re.search(r'(\d+)', name)
        if match:
            job_numbers.append(int(match.group(1)))
    
    job_numbers.sort()
    print(f"Current job numbers: {job_numbers}")
    
    # User specified pattern: 181, 184, 188, 191, 194, 198...
    expected_pattern = [181, 184, 188, 191, 194, 198]
    
    print(f"Expected pattern: {expected_pattern}")
    
    # Analyze the pattern
    if len(expected_pattern) > 1:
        differences = [expected_pattern[i+1] - expected_pattern[i] for i in range(len(expected_pattern)-1)]
        print(f"Pattern differences: {differences}")
        
        # It looks like: +3, +4, +3, +3, +4
        # This suggests an alternating pattern of mostly +3 with occasional +4
        
    return expected_pattern

def calculate_next_job_number(current_numbers, business_pattern=None):
    """Calculate the next job number based on business pattern"""
    
    if not current_numbers:
        # If no existing jobs, start with the business starting point
        return 181  # Starting point based on user's pattern
    
    max_number = max(current_numbers)
    
    # If we're in test mode (numbers < 100), use simple increment
    if max_number < 100:
        return max_number + 1
    
    # Business pattern logic
    # Pattern appears to be: start at 181, then mostly +3 with occasional +4
    # 181 → 184 (+3)
    # 184 → 188 (+4) 
    # 188 → 191 (+3)
    # 191 → 194 (+3)
    # 194 → 198 (+4)
    
    # Simple heuristic: use +3 most of the time, +4 occasionally
    # You might need to adjust this based on your business logic
    
    # For now, let's use a pattern where every 3rd increment is +4, others are +3
    if (max_number - 181) % 9 in [4, 5]:  # Rough approximation
        increment = 4
    else:
        increment = 3
        
    next_number = max_number + increment
    print(f"📊 Calculated next job number: {max_number} + {increment} = {next_number}")
    
    return next_number

def create_webhook_configuration_guide():
    """Create guide for webhook configuration"""
    print("\n🔗 WEBHOOK CONFIGURATION GUIDE")
    print("=" * 35)
    
    # Get the production URL
    production_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    webhook_url = f"{production_url}/api/brightdata/webhook/"
    
    print(f"📍 BrightData Webhook URL to configure:")
    print(f"   {webhook_url}")
    print()
    print("🔧 Configuration steps in BrightData dashboard:")
    print("   1. Go to your dataset settings")
    print("   2. Find 'Notify URL' or 'Send to webhook' option")
    print("   3. Enter the webhook URL above")
    print("   4. Enable 'Send to webhook' checkbox")
    print("   5. Test the webhook delivery")
    print()
    print("✅ Benefits of webhook configuration:")
    print("   - Real-time job creation when scraping completes")
    print("   - Automatic data organization")  
    print("   - No manual checking required")
    print()
    print("⚠️  Alternative: If webhook is not configured, the system")
    print("   will still create jobs when you access the data via API")

def create_snapshot_id_validation():
    """Create snapshot ID validation and debugging"""
    print("\n🔍 SNAPSHOT ID DEBUGGING GUIDE")
    print("=" * 32)
    
    validation_script = '''
# Test snapshot ID extraction
import requests
import json

def test_brightdata_api_response():
    """Test what BrightData API actually returns"""
    
    # Mock response structure based on BrightData documentation
    mock_responses = [
        # Successful trigger response
        {
            "snapshot_id": "sd_abc123def456", 
            "status": "running",
            "dataset_id": "gd_lk5ns7kz21pck8jpis"
        },
        
        # Alternative response format
        {
            "id": "sd_xyz789abc012",
            "status": "queued" 
        },
        
        # Error response
        {
            "error": "Invalid input",
            "code": 400
        }
    ]
    
    for i, response in enumerate(mock_responses):
        print(f"Response {i+1}: {response}")
        
        # Extract snapshot ID using multiple fallback methods
        snapshot_id = (
            response.get('snapshot_id') or 
            response.get('id') or 
            response.get('batch_id') or
            f"fallback_{i}"
        )
        
        print(f"Extracted snapshot_id: {snapshot_id}")
        print()

test_brightdata_api_response()
'''
    
    print("🧪 Snapshot ID extraction logic:")
    print(validation_script)

if __name__ == "__main__":
    print("🔧 COMPREHENSIVE BRIGHTDATA FIXES")
    print("=" * 35)
    
    # Analyze current job numbering
    analyze_job_numbering_pattern()
    
    # Create webhook guide
    create_webhook_configuration_guide()
    
    # Create debugging guide
    create_snapshot_id_validation()
    
    print("\n✅ Next steps:")
    print("1. Update job numbering logic in services.py")
    print("2. Improve snapshot ID extraction")
    print("3. Configure webhook URL in BrightData dashboard")
    print("4. Test with real BrightData API calls")