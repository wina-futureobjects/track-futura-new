#!/usr/bin/env python3
"""
BrightData Dashboard API Testing - REAL ENDPOINTS
Testing the actual API endpoints from the dashboard page
"""

import requests
import json
from datetime import datetime

class BrightDataRealAPITester:
    def __init__(self):
        self.api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
        self.facebook_dataset_id = "gd_lkaxegm826bjpoo9m5"
        self.instagram_dataset_id = "gd_lk5ns7kz21pck8jpis"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Real endpoints from dashboard
        self.endpoints = {
            "progress": "https://api.brightdata.com/datasets/v3/progress/",
            "deliver": "https://api.brightdata.com/datasets/v3/deliver/",
            "snapshots": "https://api.brightdata.com/datasets/v3/snapshots"
        }
    
    def test_progress_monitoring(self):
        """Test progress monitoring endpoint"""
        print("🔍 TESTING PROGRESS MONITORING")
        print("=" * 35)
        
        try:
            response = requests.get(self.endpoints["progress"], headers=self.headers, timeout=15)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS - Progress endpoint working!")
                data = response.json()
                print(f"📄 Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_snapshots_list(self, dataset_id, platform_name):
        """Test getting snapshots list"""
        print(f"\n🔍 TESTING SNAPSHOTS LIST - {platform_name.upper()}")
        print("=" * 45)
        
        try:
            params = {
                "dataset_id": dataset_id,
                "status": "ready"
            }
            
            response = requests.get(self.endpoints["snapshots"], 
                                  headers=self.headers, 
                                  params=params, 
                                  timeout=15)
            
            print(f"📊 Status: {response.status_code}")
            print(f"🔗 URL: {response.url}")
            
            if response.status_code == 200:
                print(f"✅ SUCCESS - {platform_name} snapshots endpoint working!")
                data = response.json()
                print(f"📄 Response: {json.dumps(data, indent=2)}")
                
                # Check if we have snapshots
                if isinstance(data, list):
                    print(f"📸 Found {len(data)} snapshots")
                    for i, snapshot in enumerate(data[:3]):  # Show first 3
                        snapshot_id = snapshot.get('snapshot_id', 'Unknown')
                        status = snapshot.get('status', 'Unknown')
                        print(f"   {i+1}. {snapshot_id} - {status}")
                elif isinstance(data, dict) and 'snapshots' in data:
                    snapshots = data['snapshots']
                    print(f"📸 Found {len(snapshots)} snapshots")
                    for i, snapshot in enumerate(snapshots[:3]):
                        snapshot_id = snapshot.get('snapshot_id', 'Unknown')
                        status = snapshot.get('status', 'Unknown')
                        print(f"   {i+1}. {snapshot_id} - {status}")
                
                return True, data
            else:
                print(f"❌ Failed: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False, None
    
    def test_delivery_setup(self):
        """Test delivery to storage endpoint"""
        print(f"\n🔍 TESTING DELIVERY SETUP")
        print("=" * 30)
        
        try:
            data = {
                "deliver": {
                    "type": "s3",
                    "filename": {
                        "template": "{[snapshot_id]}",
                        "extension": "json"
                    },
                    "bucket": "",
                    "directory": ""
                },
                "compress": "false"
            }
            
            response = requests.post(self.endpoints["deliver"], 
                                   headers=self.headers, 
                                   json=data, 
                                   timeout=15)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS - Delivery endpoint working!")
                result = response.json()
                print(f"📄 Response: {json.dumps(result, indent=2)}")
                return True
            else:
                print(f"❌ Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_specific_snapshot_access(self, snapshot_id):
        """Test accessing a specific snapshot"""
        print(f"\n🔍 TESTING SNAPSHOT ACCESS: {snapshot_id}")
        print("=" * 50)
        
        # Try different patterns for accessing snapshot data
        patterns = [
            f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}",
            f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}/data",
            f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}/download",
            f"https://api.brightdata.com/datasets/v3/snapshots/{snapshot_id}",
            f"https://api.brightdata.com/datasets/v3/snapshots/{snapshot_id}/data"
        ]
        
        for pattern in patterns:
            try:
                print(f"\n   Testing: {pattern}")
                response = requests.get(pattern, headers=self.headers, timeout=15)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ SUCCESS!")
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"   📦 Data: {len(data)} items")
                        else:
                            print(f"   📄 Response: {str(data)[:200]}...")
                    except:
                        print(f"   📄 Response: {response.text[:200]}...")
                elif response.status_code != 404:
                    print(f"   ⚠️ Interesting: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def comprehensive_test(self):
        """Run all tests"""
        print("🚀 COMPREHENSIVE BRIGHTDATA REAL API TEST")
        print("=" * 50)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔑 Token: {self.api_token[:20]}...")
        print()
        
        results = {}
        
        # Test 1: Progress monitoring
        results['progress'] = self.test_progress_monitoring()
        
        # Test 2: Facebook snapshots
        success, fb_data = self.test_snapshots_list(self.facebook_dataset_id, "Facebook")
        results['facebook_snapshots'] = success
        
        # Test 3: Instagram snapshots  
        success, ig_data = self.test_snapshots_list(self.instagram_dataset_id, "Instagram")
        results['instagram_snapshots'] = success
        
        # Test 4: Delivery setup
        results['delivery'] = self.test_delivery_setup()
        
        # Test 5: Try to access known snapshot IDs
        known_snapshots = ["s_mggq02qnd20yqnt78", "s_mggpf9c8d4954otj6"]
        for snapshot_id in known_snapshots:
            self.test_specific_snapshot_access(snapshot_id)
        
        print("\n" + "=" * 50)
        print("🎯 TEST SUMMARY")
        print("=" * 50)
        
        for test_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        total_passed = sum(results.values())
        total_tests = len(results)
        
        print(f"\nOverall: {total_passed}/{total_tests} tests passed")
        
        if total_passed >= 2:  # At least progress and one snapshots endpoint
            print("\n🎉 GREAT! We have working endpoints!")
            print("✅ Ready to update services.py with real endpoints")
        else:
            print("\n⚠️ Need to investigate further")
        
        return results

def main():
    tester = BrightDataRealAPITester()
    results = tester.comprehensive_test()
    
    print("\n🔧 NEXT STEPS:")
    if results.get('progress') or results.get('facebook_snapshots') or results.get('instagram_snapshots'):
        print("1. ✅ Update services.py with working endpoints")
        print("2. ✅ Implement real data fetching")
        print("3. ✅ Test complete integration")
    else:
        print("1. Debug authentication or endpoint URLs")
        print("2. Check API token permissions")
        print("3. Verify dataset IDs")

if __name__ == "__main__":
    main()