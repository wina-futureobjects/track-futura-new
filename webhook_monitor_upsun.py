#!/usr/bin/env python3
"""
Real-time Webhook Monitor for Upsun
Monitor webhook calls in real-time
"""

import requests
import time
import json
from datetime import datetime

def monitor_webhook():
    webhook_url = "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/"
    health_url = "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/health/"

    print("WEBHOOK MONITOR STARTED")
    print(f"Monitoring: {webhook_url}")
    print("Press Ctrl+C to stop")
    print("-" * 50)

    while True:
        try:
            # Check webhook health every 30 seconds
            response = requests.get(health_url, timeout=5)
            status = "Online" if response.status_code == 200 else f"Error {response.status_code}"
            print(f"{datetime.now().strftime('%H:%M:%S')} - Webhook Status: {status}")

            time.sleep(30)

        except KeyboardInterrupt:
            print("\nMonitor stopped")
            break
        except Exception as e:
            print(f"{datetime.now().strftime('%H:%M:%S')} - Monitor Error: {str(e)}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_webhook()
