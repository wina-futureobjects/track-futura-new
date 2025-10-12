#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import resolve
from django.urls.exceptions import Resolver404

def test_url_resolution():
    test_urls = [
        '/api/brightdata/data-storage/run/18/',
        '/api/brightdata/run-info/18/',
    ]
    
    for url in test_urls:
        print(f"Testing URL: {url}")
        try:
            match = resolve(url)
            print(f"  ✅ Resolves to: {match.func.__name__}")
            print(f"  ✅ Args: {match.args}")
            print(f"  ✅ Kwargs: {match.kwargs}")
        except Resolver404 as e:
            print(f"  ❌ URL NOT FOUND: {e}")
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
        print()

if __name__ == "__main__":
    test_url_resolution()