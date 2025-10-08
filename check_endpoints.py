#!/usr/bin/env python3
"""
Check all available API endpoints
"""
import requests

BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def check_api_endpoints():
    endpoints = [
        "/api/",
        "/api/brightdata/",
        "/api/brightdata/configs/",
        "/api/brightdata/trigger-scraper/",
        "/api/users/",
        "/api/workflow/",
    ]
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url)
            print(f"{endpoint:35} -> {response.status_code}")
            if response.status_code == 200:
                text = response.text[:200]
                print(f"                                  Content: {text}...")
        except Exception as e:
            print(f"{endpoint:35} -> ERROR: {e}")

if __name__ == "__main__":
    check_api_endpoints()