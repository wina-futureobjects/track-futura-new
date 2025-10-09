#!/usr/bin/env python
"""
Test authentication with the new tokens
"""
import requests
import json

# Test different endpoints with the new token
BASE_URL = "http://localhost:8080/api"
TOKEN = "e242daf2ea05576f08fb8d808aba529b0c7ffbab"
TEMP_TOKEN = "temp-token-for-testing"

headers = {
    'Authorization': f'Token {TOKEN}',
    'Content-Type': 'application/json'
}

temp_headers = {
    'Authorization': f'Token {TEMP_TOKEN}',
    'Content-Type': 'application/json'
}

def test_endpoints():
    print("🧪 TESTING AUTHENTICATION")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        '/reports/templates/',
        '/reports/generated/',
        '/users/profile/',
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing: {BASE_URL}{endpoint}")
        
        # Test with real token
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            print(f"   Real Token: {response.status_code} - {response.reason}")
            if response.status_code != 200 and response.status_code != 404:
                print(f"   Error: {response.text[:100]}...")
        except Exception as e:
            print(f"   Real Token Error: {str(e)}")
        
        # Test with temp token
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=temp_headers, timeout=5)
            print(f"   Temp Token: {response.status_code} - {response.reason}")
            if response.status_code != 200 and response.status_code != 404:
                print(f"   Error: {response.text[:100]}...")
        except Exception as e:
            print(f"   Temp Token Error: {str(e)}")

    # Test sentiment analysis endpoint specifically
    print(f"\n🎯 TESTING SENTIMENT ANALYSIS (Report ID: 1)")
    endpoint = '/reports/sentiment-analysis/1/'
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
        print(f"   Real Token: {response.status_code} - {response.reason}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Real Token Error: {str(e)}")
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=temp_headers, timeout=5)
        print(f"   Temp Token: {response.status_code} - {response.reason}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Temp Token Error: {str(e)}")

if __name__ == '__main__':
    test_endpoints()