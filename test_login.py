#!/usr/bin/env python3
import requests
import json

# Test login with alice.johnson
url = 'http://localhost:8000/api/users/login/'
data = {
    'username': 'alice.johnson',
    'password': 'demo123!'
}

try:
    # Try JSON format first
    response = requests.post(url, json=data)
    print(f"JSON - Status Code: {response.status_code}")
    print(f"JSON - Response: {response.text}")

    # Try form data format
    response2 = requests.post(url, data=data)
    print(f"Form - Status Code: {response2.status_code}")
    print(f"Form - Response: {response2.text}")

    if response.status_code == 200 or response2.status_code == 200:
        print("Login successful!")
    else:
        print("Login failed!")
except Exception as e:
    print(f"Error: {e}")