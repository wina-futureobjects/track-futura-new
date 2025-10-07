#!/usr/bin/env python
"""
Apify Polling Service - Background Process
Starts the continuous polling service for Apify runs
"""
import os
import django
import subprocess
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def start_polling_service():
    """Start the continuous Apify polling service"""
    try:
        print("🚀 Starting Apify Polling Service...")
        print("📊 Refreshes every 30 seconds")
        print("⏹️  Press Ctrl+C to stop")
        
        # Start the polling command
        result = subprocess.run([
            sys.executable, 'manage.py', 'poll_apify_runs', 
            '--continuous', '--interval', '30'
        ], cwd=os.path.dirname(__file__))
        
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print("\n🛑 Polling service stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting polling service: {e}")
        return False

if __name__ == "__main__":
    start_polling_service()