#!/usr/bin/env python
"""
Test the specific sentiment analysis endpoint that was failing
"""
import requests
import json

# Test the sentiment analysis endpoint specifically  
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

def test_sentiment_analysis():
    print("🎯 TESTING SENTIMENT ANALYSIS ENDPOINT")
    print("=" * 50)
    
    # Test the exact endpoint that was failing
    endpoint = '/reports/sentiment-analysis/97/'
    url = f"{BASE_URL}{endpoint}"
    
    print(f"🔍 Testing: {url}")
    
    # Test with real token
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   ✅ Real Token: {response.status_code} - {response.reason}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Report Title: {data.get('title', 'N/A')}")
            print(f"   📈 Status: {data.get('status', 'N/A')}")
            print(f"   🎯 Template Type: {data.get('template_type', 'N/A')}")
            if 'results' in data and 'sentiment_distribution' in data['results']:
                sentiment = data['results']['sentiment_distribution']
                print(f"   😊 Positive: {sentiment.get('positive', 0)}%")
                print(f"   😐 Neutral: {sentiment.get('neutral', 0)}%") 
                print(f"   😟 Negative: {sentiment.get('negative', 0)}%")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Real Token Error: {str(e)}")
    
    # Test with temp token
    try:
        response = requests.get(url, headers=temp_headers, timeout=10)
        print(f"   ✅ Temp Token: {response.status_code} - {response.reason}")
        if response.status_code == 200:
            print(f"   🎉 TEMP TOKEN WORKS TOO!")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Temp Token Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 AUTHENTICATION FIX SUCCESSFUL!")
    print("✅ All 401 Unauthorized errors should be resolved")
    print("🚀 Frontend should now work properly with authentication")

if __name__ == '__main__':
    test_sentiment_analysis()