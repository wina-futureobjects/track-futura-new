#!/usr/bin/env python3
"""
FRONTEND INTERFACE TEST - Test your exact interface code
This will help you test your frontend interface connection
"""

import requests
import json

def test_frontend_interface():
    """Test exactly what your frontend interface should do"""
    
    print("🌐 FRONTEND INTERFACE CONNECTION TEST")
    print("=" * 60)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("1. 📱 TESTING YOUR INTERFACE CONNECTION...")
    
    # Test what your frontend interface is doing
    try:
        # This simulates exactly what your frontend JavaScript should do
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        test_data = {
            "platform": "instagram",
            "urls": ["https://www.instagram.com/nike/"]
        }
        
        print(f"   🔄 Sending request to: {base_url}/api/brightdata/trigger-scraper/")
        print(f"   📦 Payload: {json.dumps(test_data, indent=2)}")
        print(f"   📋 Headers: {headers}")
        
        response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json=test_data,
            headers=headers,
            timeout=30
        )
        
        print(f"\n   📊 RESPONSE:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"\n   ✅ INTERFACE TEST SUCCESS!")
                print(f"   🎯 Your interface SHOULD work with this exact code!")
                print(f"   📊 Batch Job: {data.get('batch_job_id')}")
                print(f"   📊 Dataset: {data.get('dataset_id')}")
            else:
                print(f"\n   ❌ API Error: {data.get('error')}")
        else:
            print(f"\n   ❌ HTTP Error: {response.status_code}")
        
    except Exception as e:
        print(f"\n   ❌ Connection Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 YOUR INTERFACE CODE (JavaScript):")
    print("=" * 60)
    
    interface_code = '''
// EXACT CODE FOR YOUR FRONTEND INTERFACE
async function triggerBrightDataScraper(platform, urls) {
    try {
        console.log('🚀 Triggering BrightData scraper...', { platform, urls });
        
        const response = await fetch('https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                platform: platform,
                urls: urls
            })
        });
        
        console.log('📊 Response status:', response.status);
        
        const data = await response.json();
        console.log('📦 Response data:', data);
        
        if (data.success) {
            console.log('✅ SUCCESS! BrightData job created:', data.batch_job_id);
            
            // Show success message to user
            alert(`✅ Success! BrightData ${platform} scraper started!\\nJob ID: ${data.batch_job_id}\\nDataset: ${data.dataset_id}`);
            
            return data;
        } else {
            console.error('❌ API Error:', data.error);
            alert(`❌ Error: ${data.error}`);
            return null;
        }
        
    } catch (error) {
        console.error('❌ Network Error:', error);
        alert(`❌ Connection Error: ${error.message}`);
        return null;
    }
}

// USAGE EXAMPLES:
// Instagram scraping
triggerBrightDataScraper('instagram', ['https://www.instagram.com/nike/']);

// Facebook scraping  
triggerBrightDataScraper('facebook', ['https://www.facebook.com/nike']);

// Multiple URLs
triggerBrightDataScraper('instagram', [
    'https://www.instagram.com/nike/',
    'https://www.instagram.com/adidas/'
]);
'''
    
    print(interface_code)
    
    print("\n" + "=" * 60)
    print("🔧 HOW TO DEBUG YOUR INTERFACE:")
    print("=" * 60)
    print("1. Open your browser's Developer Tools (F12)")
    print("2. Go to the Console tab")
    print("3. Paste the JavaScript code above")
    print("4. Call the function: triggerBrightDataScraper('instagram', ['https://www.instagram.com/nike/'])")
    print("5. Check the console for any errors or success messages")
    print("6. If you see '✅ SUCCESS!', your interface is working!")
    print("7. If you see errors, copy the exact error message")
    
    print("\n📋 IF YOUR INTERFACE STILL DOESN'T WORK:")
    print("• Check browser console for CORS errors")
    print("• Make sure you're using the exact URL above")
    print("• Verify the payload format matches exactly")
    print("• Try the browser test code above first")
    print("• Check if your interface is running on HTTPS (required for CORS)")

if __name__ == "__main__":
    test_frontend_interface()