#!/usr/bin/env python3
"""
FRONTEND DEBUG - Check what your Instant Run button is actually doing
"""

import requests
import json

def debug_frontend_calls():
    """Debug what calls your frontend is making"""
    
    print("🔍 DEBUGGING YOUR FRONTEND INSTANT RUN BUTTON")
    print("=" * 60)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test 1: Check if frontend can reach our BrightData endpoint
    print("1. 🌐 TESTING BRIGHTDATA ENDPOINT FROM FRONTEND PERSPECTIVE...")
    
    try:
        # Test with exact same headers a browser would send
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Origin': base_url,
            'Referer': f'{base_url}/organizations/1/projects/1/workflow-management'
        }
        
        test_payload = {
            "platform": "instagram",
            "urls": ["https://www.instagram.com/nike/"]
        }
        
        print(f"   🔄 Making request to: {base_url}/api/brightdata/trigger-scraper/")
        print(f"   📦 Payload: {json.dumps(test_payload)}")
        print(f"   📋 Headers: {headers}")
        
        response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json=test_payload,
            headers=headers,
            timeout=30
        )
        
        print(f"\n   📊 RESPONSE:")
        print(f"   Status: {response.status_code}")
        print(f"   Response Headers:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower() or 'cors' in key.lower():
                print(f"      {key}: {value}")
        print(f"   Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"\n   ✅ BRIGHTDATA API WORKING!")
                print(f"   📊 Job ID: {data.get('batch_job_id')}")
                print(f"   📊 Dataset: {data.get('dataset_id')}")
            else:
                print(f"\n   ❌ API Error: {data.get('error')}")
        else:
            print(f"\n   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"\n   ❌ Connection Error: {e}")
    
    # Test 2: Check OPTIONS request (CORS preflight)
    print("\n2. 🔧 TESTING CORS PREFLIGHT (OPTIONS REQUEST)...")
    
    try:
        response = requests.options(
            f"{base_url}/api/brightdata/trigger-scraper/",
            headers={
                'Origin': base_url,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=10
        )
        
        print(f"   OPTIONS Status: {response.status_code}")
        print(f"   CORS Headers:")
        cors_headers = {k: v for k, v in response.headers.items() 
                       if 'access-control' in k.lower() or 'cors' in k.lower()}
        
        if cors_headers:
            for key, value in cors_headers.items():
                print(f"      {key}: {value}")
        else:
            print("      ❌ NO CORS HEADERS FOUND!")
            
        if response.status_code == 200:
            print("   ✅ CORS preflight successful!")
        else:
            print(f"   ❌ CORS preflight failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ CORS preflight error: {e}")
    
    # Test 3: Common frontend issues
    print("\n3. 🐛 CHECKING COMMON FRONTEND ISSUES...")
    
    # Check if workflow management page exists
    try:
        print(f"   a) Checking workflow management page...")
        response = requests.get(f"{base_url}/organizations/1/projects/1/workflow-management", timeout=10)
        print(f"      Page Status: {response.status_code}")
        
        if response.status_code == 200:
            print("      ✅ Workflow page accessible")
        else:
            print("      ❌ Workflow page not found")
            
    except Exception as e:
        print(f"      ❌ Page check error: {e}")
    
    # Check if there are other API endpoints interfering
    try:
        print(f"   b) Checking API base...")
        response = requests.get(f"{base_url}/api/", timeout=10)
        print(f"      API Base Status: {response.status_code}")
    except Exception as e:
        print(f"      API Base Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 FRONTEND JAVASCRIPT TO FIX YOUR INSTANT RUN BUTTON:")
    print("=" * 60)
    
    js_code = '''
// PASTE THIS INTO YOUR FRONTEND - INSTANT RUN BUTTON FIX
function setupInstantRunButton() {
    // Find your instant run button (adjust selector as needed)
    const instantRunButton = document.querySelector('#instant-run-btn') || 
                            document.querySelector('.instant-run') ||
                            document.querySelector('[data-action="instant-run"]');
    
    if (instantRunButton) {
        console.log('✅ Found instant run button:', instantRunButton);
        
        // Remove old event listeners
        instantRunButton.replaceWith(instantRunButton.cloneNode(true));
        const newButton = document.querySelector('#instant-run-btn') || 
                         document.querySelector('.instant-run') ||
                         document.querySelector('[data-action="instant-run"]');
        
        // Add new working event listener
        newButton.addEventListener('click', async function(e) {
            e.preventDefault();
            console.log('🚀 Instant Run button clicked!');
            
            // Show loading state
            newButton.disabled = true;
            newButton.textContent = 'Running...';
            
            try {
                // Get selected platform and URLs from your form
                const platform = document.querySelector('#platform-select')?.value || 'instagram';
                const urlInput = document.querySelector('#url-input')?.value || 'https://www.instagram.com/nike/';
                const urls = [urlInput];
                
                console.log('📋 Triggering scraper:', { platform, urls });
                
                // Make the API call
                const response = await fetch('/api/brightdata/trigger-scraper/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken() // Your CSRF token function
                    },
                    body: JSON.stringify({
                        platform: platform,
                        urls: urls
                    })
                });
                
                const data = await response.json();
                console.log('📊 API Response:', data);
                
                if (data.success) {
                    // Success!
                    alert(`✅ Success! BrightData ${platform} scraper started!\\n\\nJob ID: ${data.batch_job_id}\\nDataset: ${data.dataset_id}\\n\\nCheck BrightData dashboard for progress.`);
                    
                    // Update UI
                    newButton.textContent = '✅ Started!';
                    setTimeout(() => {
                        newButton.textContent = 'Instant Run';
                        newButton.disabled = false;
                    }, 3000);
                    
                } else {
                    // Error
                    console.error('❌ API Error:', data.error);
                    alert(`❌ Error: ${data.error}`);
                    
                    newButton.textContent = '❌ Failed';
                    setTimeout(() => {
                        newButton.textContent = 'Instant Run';
                        newButton.disabled = false;
                    }, 3000);
                }
                
            } catch (error) {
                console.error('❌ Network Error:', error);
                alert(`❌ Connection Error: ${error.message}`);
                
                newButton.textContent = '❌ Error';
                setTimeout(() => {
                    newButton.textContent = 'Instant Run';
                    newButton.disabled = false;
                }, 3000);
            }
        });
        
        console.log('✅ Instant Run button setup complete!');
    } else {
        console.error('❌ Instant Run button not found! Check your button selector.');
    }
}

// Helper function to get CSRF token
function getCsrfToken() {
    const csrfCookie = document.cookie.split(';')
        .find(cookie => cookie.trim().startsWith('csrftoken='));
    
    if (csrfCookie) {
        return csrfCookie.split('=')[1];
    }
    
    // Fallback: try to get from meta tag or hidden input
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) return csrfMeta.content;
    
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput) return csrfInput.value;
    
    return '';
}

// Run when page loads
document.addEventListener('DOMContentLoaded', setupInstantRunButton);

// Also run if button is added dynamically
setTimeout(setupInstantRunButton, 1000);
'''
    
    print(js_code)
    
    print("\n" + "=" * 60)
    print("🔧 HOW TO FIX YOUR INSTANT RUN BUTTON:")
    print("=" * 60)
    print("1. Go to your workflow management page")
    print("2. Open browser Developer Tools (F12)")
    print("3. Go to Console tab")
    print("4. Paste the JavaScript code above")
    print("5. Press Enter to run it")
    print("6. Try clicking your Instant Run button")
    print("7. Check console for any error messages")
    
    print("\n📋 WHAT THE CODE DOES:")
    print("• Finds your Instant Run button automatically")
    print("• Removes old broken event listeners") 
    print("• Adds new working BrightData API call")
    print("• Shows loading states and success/error messages")
    print("• Handles CSRF tokens properly")
    print("• Works with your existing frontend structure")

if __name__ == "__main__":
    debug_frontend_calls()