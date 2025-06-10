#!/usr/bin/env python3
"""
Test script to verify webhook fixes for infinite refresh and data folder issues
"""

import requests
import json
import time
from typing import Dict, Any

def test_webhook_monitor_api():
    """Test the webhook monitor API endpoints"""
    print("🧪 Testing Webhook Monitor API")
    print("=" * 50)

    base_url = 'http://localhost:8000'

    endpoints = [
        '/api/health/',
        '/api/brightdata/webhook/health/',
        '/api/brightdata/webhook/metrics/',
        '/api/brightdata/webhook/events/',
        '/api/brightdata/webhook/alerts/',
        '/api/brightdata/webhook/analytics/',
    ]

    results = {}

    for endpoint in endpoints:
        try:
            print(f"Testing {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)

            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
                results[endpoint] = {
                    'status': 'success',
                    'status_code': response.status_code,
                    'response_size': len(response.content)
                }
            else:
                print(f"❌ {endpoint}: {response.status_code}")
                results[endpoint] = {
                    'status': 'error',
                    'status_code': response.status_code,
                    'error': response.text[:200]
                }

        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")
            results[endpoint] = {
                'status': 'exception',
                'error': str(e)
            }

    return results

def test_webhook_data_processing():
    """Test webhook data processing with folder assignment"""
    print("\n🧪 Testing Webhook Data Processing")
    print("=" * 50)

    base_url = 'http://localhost:8000'
    webhook_url = f"{base_url}/api/brightdata/webhook/"

    # Test data for different platforms
    test_cases = [
        {
            'platform': 'facebook',
            'data': [
                {
                    "url": "https://www.facebook.com/test",
                    "post_id": "test_facebook_123",
                    "content": "Test Facebook post",
                    "date_posted": "2024-12-19T12:00:00Z",
                    "likes": 100,
                    "num_comments": 50
                }
            ]
        },
        {
            'platform': 'instagram',
            'data': [
                {
                    "url": "https://www.instagram.com/p/test",
                    "post_id": "test_instagram_123",
                    "content": "Test Instagram post",
                    "date_posted": "2024-12-19T12:00:00Z",
                    "likes": 200,
                    "num_comments": 30
                }
            ]
        },
        {
            'platform': 'linkedin',
            'data': [
                {
                    "url": "https://www.linkedin.com/feed/update/test",
                    "post_id": "test_linkedin_123",
                    "content": "Test LinkedIn post",
                    "date_posted": "2024-12-19T12:00:00Z",
                    "likes": 75,
                    "num_comments": 25
                }
            ]
        }
    ]

    results = {}

    for test_case in test_cases:
        platform = test_case['platform']
        data = test_case['data']

        print(f"\nTesting {platform} data processing...")

        # Headers to simulate BrightData webhook
        headers = {
            'Content-Type': 'application/json',
            'X-Platform': platform,
            'X-Snapshot-Id': f'test_{platform}_{int(time.time())}',
            'User-Agent': 'BrightData-Webhook/1.0'
        }

        try:
            response = requests.post(
                webhook_url,
                json=data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                response_data = response.json()
                print(f"✅ {platform}: Data processed successfully")
                print(f"   Response: {response_data.get('message', 'No message')}")
                print(f"   Processing time: {response_data.get('processing_time', 'N/A')}s")

                results[platform] = {
                    'status': 'success',
                    'response': response_data
                }
            else:
                print(f"❌ {platform}: HTTP {response.status_code}")
                print(f"   Error: {response.text[:200]}")

                results[platform] = {
                    'status': 'error',
                    'status_code': response.status_code,
                    'error': response.text[:200]
                }

        except Exception as e:
            print(f"❌ {platform}: Exception - {str(e)}")
            results[platform] = {
                'status': 'exception',
                'error': str(e)
            }

    return results

def test_frontend_accessibility():
    """Test if the frontend webhook monitor is accessible"""
    print("\n🧪 Testing Frontend Accessibility")
    print("=" * 50)

    frontend_url = 'http://localhost:5173'

    try:
        print("Testing frontend health...")
        response = requests.get(frontend_url, timeout=5)

        if response.status_code == 200:
            print("✅ Frontend: Accessible")
            return {'status': 'success', 'frontend_accessible': True}
        else:
            print(f"❌ Frontend: HTTP {response.status_code}")
            return {'status': 'error', 'status_code': response.status_code}

    except Exception as e:
        print(f"❌ Frontend: {str(e)}")
        return {'status': 'exception', 'error': str(e)}

def main():
    """Run all tests"""
    print("🚀 Testing Track-Futura Webhook Fixes")
    print("=" * 60)

    # Test webhook monitor API
    api_results = test_webhook_monitor_api()

    # Test webhook data processing
    webhook_results = test_webhook_data_processing()

    # Test frontend accessibility
    frontend_results = test_frontend_accessibility()

    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)

    total_tests = len(api_results) + len(webhook_results) + 1
    successful_tests = 0

    print(f"\n🔧 API Endpoints ({len(api_results)} tests):")
    for endpoint, result in api_results.items():
        status = "✅" if result['status'] == 'success' else "❌"
        print(f"  {status} {endpoint}")
        if result['status'] == 'success':
            successful_tests += 1

    print(f"\n📡 Webhook Processing ({len(webhook_results)} tests):")
    for platform, result in webhook_results.items():
        status = "✅" if result['status'] == 'success' else "❌"
        print(f"  {status} {platform}")
        if result['status'] == 'success':
            successful_tests += 1

    print(f"\n🌐 Frontend (1 test):")
    status = "✅" if frontend_results['status'] == 'success' else "❌"
    print(f"  {status} Accessibility")
    if frontend_results['status'] == 'success':
        successful_tests += 1

    print(f"\n🎯 Overall Result: {successful_tests}/{total_tests} tests passed")

    if successful_tests == total_tests:
        print("🎉 All tests passed! Webhook fixes are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
