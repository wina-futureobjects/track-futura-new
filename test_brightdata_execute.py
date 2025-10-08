#!/usr/bin/env python3
"""
Test BrightData directly by triggering from production workflow
"""
import requests
import json
import time

# Test the production workflow that should trigger BrightData
BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def test_brightdata_execution():
    try:
        print("🚀 TESTING BRIGHTDATA EXECUTION IN PRODUCTION")
        print("=" * 50)
        
        # Create a workflow directly (this should trigger BrightData)
        workflow_url = f"{BASE_URL}/api/workflow/input-collections/"
        workflow_data = {
            "name": f"Test BrightData Execution {int(time.time())}",
            "project": 1,
            "platform_service": 1,  # Instagram posts
            "urls": ["https://instagram.com/nike"],
            "description": "Test to trigger BrightData scraper"
        }
        
        print(f"Creating workflow at: {workflow_url}")
        print(f"Payload: {json.dumps(workflow_data, indent=2)}")
        
        response = requests.post(workflow_url, json=workflow_data)
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            workflow_data = response.json()
            input_collection_id = workflow_data.get('id') or workflow_data.get('project')
            print(f"✅ Workflow created! ID: {input_collection_id}")
            
            # Now trigger the scraper manually
            scraper_url = f"{BASE_URL}/api/brightdata/trigger-scraper/"
            scraper_payload = {
                "platform": "instagram",
                "urls": ["https://instagram.com/nike"],
                "input_collection_id": input_collection_id
            }
            
            print(f"\n🎯 Triggering scraper at: {scraper_url}")
            scraper_response = requests.post(scraper_url, json=scraper_payload)
            print(f"Scraper response status: {scraper_response.status_code}")
            print(f"Scraper response: {scraper_response.text}")
            
            if scraper_response.status_code == 200:
                print("✅ SCRAPER TRIGGERED SUCCESSFULLY!")
                print("✅ Check your BrightData dashboard for incoming requests")
            else:
                print(f"❌ Scraper trigger failed: {scraper_response.text}")
        else:
            print(f"❌ Workflow creation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_brightdata_execution()