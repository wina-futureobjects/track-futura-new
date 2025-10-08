#!/usr/bin/env python3

import requests
import json

def check_production_data():
    """Check what data exists in production system"""
    
    print("🔍 CHECKING PRODUCTION DATA")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Try to get input collections
    try:
        print("\n1. Checking Input Collections...")
        response = requests.get(f"{base_url}/api/input-collections/", timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} input collections:")
            for inp in data:
                print(f"  - ID: {inp.get('id')} | Name: {inp.get('name')} | URLs: {inp.get('input_urls')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error checking input collections: {e}")
    
    # Try to get workflows
    try:
        print("\n2. Checking Workflows...")
        response = requests.get(f"{base_url}/api/workflows/", timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} workflows")
            for workflow in data[:3]:  # Show first 3
                print(f"  - ID: {workflow.get('id')} | Name: {workflow.get('name')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error checking workflows: {e}")

if __name__ == "__main__":
    check_production_data()