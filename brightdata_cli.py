#!/usr/bin/env python3
"""
BrightData Command Line Trigger Tool
Usage: python brightdata_cli.py [instagram|facebook|both]
"""
import sys
import requests
import json
import argparse
from datetime import datetime

class BrightDataCLI:
    def __init__(self):
        self.api_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/"
        
    def trigger_scraper(self, platform, urls=None):
        """Trigger a scraper for the specified platform"""
        if urls is None:
            urls = self.get_default_urls(platform)
            
        print(f"🚀 Triggering {platform.title()} scraper...")
        print(f"📋 URLs: {', '.join(urls)}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    "platform": platform,
                    "urls": urls
                },
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ SUCCESS! {platform.title()} scraper started!")
                    print(f"📊 Job ID: {data.get('batch_job_id')}")
                    print(f"📊 Dataset: {data.get('dataset_id')}")
                    print(f"🔗 URLs Count: {data.get('urls_count')}")
                    print(f"📝 Message: {data.get('message')}")
                    print("👉 Check your BrightData dashboard for progress!")
                    return True
                else:
                    print(f"❌ ERROR: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ TIMEOUT: Request took too long")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ CONNECTION ERROR: Could not connect to server")
            return False
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {str(e)}")
            return False
    
    def get_default_urls(self, platform):
        """Get default URLs for each platform"""
        defaults = {
            'instagram': [
                'https://www.instagram.com/nike/',
                'https://www.instagram.com/adidas/',
                'https://www.instagram.com/cocacola/'
            ],
            'facebook': [
                'https://www.facebook.com/nike',
                'https://www.facebook.com/adidas',
                'https://www.facebook.com/cocacola'
            ]
        }
        return defaults.get(platform, [])
    
    def trigger_both(self):
        """Trigger both Instagram and Facebook scrapers"""
        print("🎯 TRIGGERING BOTH INSTAGRAM AND FACEBOOK SCRAPERS")
        print("=" * 60)
        
        results = {}
        
        # Trigger Instagram
        print("\n📸 INSTAGRAM SCRAPER:")
        results['instagram'] = self.trigger_scraper('instagram')
        
        # Trigger Facebook  
        print("\n📘 FACEBOOK SCRAPER:")
        results['facebook'] = self.trigger_scraper('facebook')
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY:")
        
        success_count = sum(results.values())
        if success_count == 2:
            print("🎉 Both scrapers started successfully!")
        elif success_count == 1:
            print("⚠️  One scraper started, one failed")
        else:
            print("❌ Both scrapers failed")
            
        print(f"✅ Instagram: {'Success' if results['instagram'] else 'Failed'}")
        print(f"✅ Facebook: {'Success' if results['facebook'] else 'Failed'}")
        
        return success_count > 0

def main():
    parser = argparse.ArgumentParser(
        description="🚀 BrightData Scraper Trigger CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python brightdata_cli.py instagram           # Trigger Instagram scraper
  python brightdata_cli.py facebook            # Trigger Facebook scraper  
  python brightdata_cli.py both                # Trigger both scrapers
  python brightdata_cli.py instagram --urls "https://www.instagram.com/custom/"
        """
    )
    
    parser.add_argument(
        'platform',
        choices=['instagram', 'facebook', 'both'],
        help='Platform to scrape (instagram, facebook, or both)'
    )
    
    parser.add_argument(
        '--urls',
        nargs='+',
        help='Custom URLs to scrape (space-separated)'
    )
    
    args = parser.parse_args()
    
    cli = BrightDataCLI()
    
    print("🚀 BRIGHTDATA SCRAPER TRIGGER CLI")
    print("=" * 40)
    
    if args.platform == 'both':
        success = cli.trigger_both()
    else:
        success = cli.trigger_scraper(args.platform, args.urls)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()