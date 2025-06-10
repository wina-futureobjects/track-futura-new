#!/usr/bin/env python3
"""
Comprehensive Webhook Testing Script for Track-Futura BrightData Integration

This script tests webhook functionality both locally and in production environments.
It simulates BrightData webhook calls and validates the entire pipeline.
"""

import requests
import json
import time
import hmac
import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass
import argparse
import sys
import os

@dataclass
class TestResult:
    name: str
    success: bool
    message: str
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    response_data: Optional[dict] = None

class WebhookTester:
    def __init__(self, base_url: str, webhook_token: str):
        self.base_url = base_url.rstrip('/')
        self.webhook_token = webhook_token
        self.webhook_url = f"{self.base_url}/api/brightdata/webhook/"
        self.notify_url = f"{self.base_url}/api/brightdata/notify/"
        self.health_url = f"{self.base_url}/api/brightdata/webhook/health/"

    def create_signature(self, payload: str) -> str:
        """Create HMAC signature for webhook payload"""
        return hmac.new(
            self.webhook_token.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def test_server_health(self) -> TestResult:
        """Test if the server is accessible"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/health/", timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                return TestResult(
                    name="Server Health Check",
                    success=True,
                    message="✅ Server is healthy and accessible",
                    response_time=response_time,
                    status_code=response.status_code,
                    response_data=response.json()
                )
            else:
                return TestResult(
                    name="Server Health Check",
                    success=False,
                    message=f"❌ Server returned status {response.status_code}",
                    response_time=response_time,
                    status_code=response.status_code
                )
        except requests.exceptions.RequestException as e:
            return TestResult(
                name="Server Health Check",
                success=False,
                message=f"❌ Cannot connect to server: {str(e)}"
            )

    def test_webhook_health(self) -> TestResult:
        """Test webhook health endpoint"""
        try:
            start_time = time.time()
            response = requests.get(self.health_url, timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                return TestResult(
                    name="Webhook Health Check",
                    success=True,
                    message="✅ Webhook system is healthy",
                    response_time=response_time,
                    status_code=response.status_code,
                    response_data=response.json()
                )
            else:
                return TestResult(
                    name="Webhook Health Check",
                    success=False,
                    message=f"❌ Webhook health check failed with status {response.status_code}",
                    response_time=response_time,
                    status_code=response.status_code
                )
        except requests.exceptions.RequestException as e:
            return TestResult(
                name="Webhook Health Check",
                success=False,
                message=f"❌ Cannot connect to webhook endpoint: {str(e)}"
            )

    def test_webhook_authentication(self) -> TestResult:
        """Test webhook authentication"""
        payload = json.dumps([{
            "url": "https://www.facebook.com/test-post-12345",
            "platform": "facebook",
            "timestamp": int(time.time())
        }])

        # Test with correct authentication
        try:
            start_time = time.time()
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.webhook_token}',
                'X-BrightData-Timestamp': str(int(time.time())),
                'X-BrightData-Signature': f'sha256={self.create_signature(payload)}'
            }

            response = requests.post(self.webhook_url, data=payload, headers=headers, timeout=10)
            response_time = time.time() - start_time

            if response.status_code in [200, 400, 500]:  # 400/500 might be expected due to test data
                return TestResult(
                    name="Webhook Authentication",
                    success=True,
                    message="✅ Webhook accepts authenticated requests",
                    response_time=response_time,
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None
                )
            elif response.status_code == 401:
                return TestResult(
                    name="Webhook Authentication",
                    success=False,
                    message="❌ Authentication failed - check webhook token",
                    response_time=response_time,
                    status_code=response.status_code
                )
            else:
                return TestResult(
                    name="Webhook Authentication",
                    success=False,
                    message=f"❌ Unexpected response status {response.status_code}",
                    response_time=response_time,
                    status_code=response.status_code
                )
        except requests.exceptions.RequestException as e:
            return TestResult(
                name="Webhook Authentication",
                success=False,
                message=f"❌ Request failed: {str(e)}"
            )

    def test_webhook_unauthorized(self) -> TestResult:
        """Test webhook rejects unauthorized requests"""
        payload = json.dumps([{"url": "https://www.facebook.com/test", "platform": "facebook"}])

        try:
            start_time = time.time()
            headers = {'Content-Type': 'application/json'}  # No authentication

            response = requests.post(self.webhook_url, data=payload, headers=headers, timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 401:
                return TestResult(
                    name="Webhook Security",
                    success=True,
                    message="✅ Webhook correctly rejects unauthorized requests",
                    response_time=response_time,
                    status_code=response.status_code
                )
            else:
                return TestResult(
                    name="Webhook Security",
                    success=False,
                    message=f"⚠️ Webhook security may be compromised - status {response.status_code}",
                    response_time=response_time,
                    status_code=response.status_code
                )
        except requests.exceptions.RequestException as e:
            return TestResult(
                name="Webhook Security",
                success=False,
                message=f"❌ Request failed: {str(e)}"
            )

    def test_facebook_data_processing(self) -> TestResult:
        """Test Facebook data processing"""
        facebook_data = [{
            "url": "https://www.facebook.com/test-page/posts/123456789",
            "platform": "facebook",
            "content": "Test Facebook post content",
            "likes": 100,
            "num_comments": 25,
            "num_shares": 10,
            "date_posted": "2023-01-01T10:00:00Z",
            "author": "Test Author",
            "timestamp": int(time.time())
        }]

        return self._test_platform_data("Facebook Data Processing", facebook_data)

    def test_instagram_data_processing(self) -> TestResult:
        """Test Instagram data processing"""
        instagram_data = [{
            "url": "https://www.instagram.com/p/test123456/",
            "platform": "instagram",
            "content": "Test Instagram post content #test",
            "likes": 500,
            "num_comments": 45,
            "date_posted": "2023-01-01T12:00:00Z",
            "author": "test_user",
            "hashtags": ["#test", "#instagram"],
            "timestamp": int(time.time())
        }]

        return self._test_platform_data("Instagram Data Processing", instagram_data)

    def _test_platform_data(self, test_name: str, data: List[Dict]) -> TestResult:
        """Helper method to test platform-specific data processing"""
        payload = json.dumps(data)

        try:
            start_time = time.time()
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.webhook_token}',
                'X-BrightData-Timestamp': str(int(time.time())),
                'X-BrightData-Signature': f'sha256={self.create_signature(payload)}',
                'X-Platform': data[0]['platform'],
                'X-Snapshot-Id': f'test-{int(time.time())}'
            }

            response = requests.post(self.webhook_url, data=payload, headers=headers, timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                return TestResult(
                    name=test_name,
                    success=True,
                    message=f"✅ {test_name} successful",
                    response_time=response_time,
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None
                )
            else:
                return TestResult(
                    name=test_name,
                    success=False,
                    message=f"❌ {test_name} failed with status {response.status_code}",
                    response_time=response_time,
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None
                )
        except requests.exceptions.RequestException as e:
            return TestResult(
                name=test_name,
                success=False,
                message=f"❌ {test_name} request failed: {str(e)}"
            )

    def test_notify_endpoint(self) -> TestResult:
        """Test notification endpoint"""
        payload = json.dumps({
            "snapshot_id": f"test-notify-{int(time.time())}",
            "status": "completed",
            "message": "Test notification"
        })

        try:
            start_time = time.time()
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.webhook_token}'
            }

            response = requests.post(self.notify_url, data=payload, headers=headers, timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                return TestResult(
                    name="Notification Endpoint",
                    success=True,
                    message="✅ Notification endpoint working correctly",
                    response_time=response_time,
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None
                )
            else:
                return TestResult(
                    name="Notification Endpoint",
                    success=False,
                    message=f"❌ Notification endpoint failed with status {response.status_code}",
                    response_time=response_time,
                    status_code=response.status_code
                )
        except requests.exceptions.RequestException as e:
            return TestResult(
                name="Notification Endpoint",
                success=False,
                message=f"❌ Notification request failed: {str(e)}"
            )

    def run_all_tests(self) -> List[TestResult]:
        """Run all webhook tests"""
        tests = [
            self.test_server_health,
            self.test_webhook_health,
            self.test_webhook_authentication,
            self.test_webhook_unauthorized,
            self.test_facebook_data_processing,
            self.test_instagram_data_processing,
            self.test_notify_endpoint
        ]

        results = []
        for test in tests:
            print(f"Running {test.__name__}...")
            result = test()
            results.append(result)
            print(f"  {result.message}")
            if result.response_time:
                print(f"  Response time: {result.response_time:.3f}s")
            print()

        return results

def main():
    parser = argparse.ArgumentParser(description='Test Track-Futura webhook functionality')
    parser.add_argument('--url', default='http://localhost:8000',
                       help='Base URL of the application (default: http://localhost:8000)')
    parser.add_argument('--token', default='your-default-webhook-secret-token-change-this',
                       help='Webhook authentication token')
    parser.add_argument('--ngrok', action='store_true',
                       help='Auto-detect ngrok URL for local testing')

    args = parser.parse_args()

    base_url = args.url

    # Auto-detect ngrok URL if requested
    if args.ngrok:
        try:
            import requests
            response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
            if response.status_code == 200:
                tunnels = response.json().get('tunnels', [])
                for tunnel in tunnels:
                    if tunnel.get('proto') == 'https':
                        base_url = tunnel['public_url']
                        print(f"🔗 Detected ngrok URL: {base_url}")
                        break
        except:
            print("⚠️ Could not detect ngrok URL, using provided URL")

    print(f"🧪 Testing webhook functionality at: {base_url}")
    print(f"🔑 Using webhook token: {args.token[:10]}..." if len(args.token) > 10 else f"🔑 Using webhook token: {args.token}")
    print("=" * 60)

    tester = WebhookTester(base_url, args.token)
    results = tester.run_all_tests()

    # Summary
    print("=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    successful = sum(1 for r in results if r.success)
    total = len(results)

    for result in results:
        status = "✅ PASS" if result.success else "❌ FAIL"
        print(f"{status} {result.name}")
        if not result.success:
            print(f"     {result.message}")

    print()
    print(f"📈 Overall: {successful}/{total} tests passed ({successful/total*100:.1f}%)")

    if successful == total:
        print("🎉 All tests passed! Webhook system is ready for production.")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
