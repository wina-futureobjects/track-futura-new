#!/usr/bin/env python
"""
Test script to verify the scraping-runs API endpoint
"""
import os
import sys
import django
import json
import requests

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from workflow.models import ScrapingRun

def test_api_endpoint():
    """Test the scraping-runs API endpoint"""
    print("🔍 Testing scraping-runs API endpoint...")
    
    # Test 1: Check if ScrapingRun ID 74 exists in database
    try:
        run = ScrapingRun.objects.get(id=74)
        print(f"✅ ScrapingRun ID 74 found in database:")
        print(f"   - Project ID: {run.project_id}")
        print(f"   - Name: {run.name}")
        print(f"   - Status: {run.status}")
        print(f"   - Configuration: {json.dumps(run.configuration, indent=2)}")
    except ScrapingRun.DoesNotExist:
        print("❌ ScrapingRun ID 74 not found in database")
        return
    
    # Test 2: Check all ScrapingRun records for project 14
    project_14_runs = ScrapingRun.objects.filter(project_id=14)
    print(f"\n📊 Total ScrapingRun records for project 14: {project_14_runs.count()}")
    
    for run in project_14_runs:
        print(f"   - ID: {run.id}, Name: {run.name}, Status: {run.status}")
        if 'period' in run.configuration:
            print(f"     ⚠️  Has period: {run.configuration['period']}")
        else:
            print(f"     ✅ No period (should appear in Instant Runs)")
    
    # Test 3: Test the API endpoint directly
    print(f"\n🌐 Testing API endpoint: http://localhost:8000/api/workflow/scraping-runs/?project=14")
    
    try:
        response = requests.get(
            "http://localhost:8000/api/workflow/scraping-runs/?project=14",
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📡 API Response Status: {response.status_code}")
        print(f"📡 API Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response Data:")
            print(f"   - Type: {type(data)}")
            
            if isinstance(data, dict) and 'results' in data:
                runs = data['results']
                print(f"   - Results count: {len(runs)}")
                
                for run_data in runs:
                    print(f"     - ID: {run_data.get('id')}, Name: {run_data.get('name')}, Status: {run_data.get('status')}")
                    config = run_data.get('configuration', {})
                    if 'period' in config:
                        print(f"       ⚠️  Has period: {config['period']}")
                    else:
                        print(f"       ✅ No period (should appear in Instant Runs)")
            else:
                print(f"   - Direct data: {data}")
        else:
            print(f"❌ API Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Django server might not be running")
    except Exception as e:
        print(f"❌ API Test Error: {str(e)}")

if __name__ == "__main__":
    test_api_endpoint()

