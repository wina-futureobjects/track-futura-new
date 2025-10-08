#!/usr/bin/env python3
"""
EMERGENCY DEBUG: Test if the frontend fix is actually deployed
"""
import requests
import json

def emergency_frontend_debug():
    print("🚨 EMERGENCY FRONTEND DEBUG")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test 1: Check if BrightData API still works
    print("1. 🔧 Testing BrightData API directly...")
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json={"platform": "instagram", "urls": ["https://www.instagram.com/nike/"]},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Works! Job ID: {data.get('batch_job_id', 'N/A')}")
        else:
            print(f"   ❌ API failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ API error: {e}")
    
    # Test 2: Check if frontend has our fix by looking for our specific code
    print("\n2. 🔍 Checking if frontend deployment includes our fix...")
    try:
        # Try to get the JavaScript bundle to see if our fix is there
        workflow_response = requests.get(f"{base_url}/organizations/1/projects/1/workflow-management", timeout=10)
        if workflow_response.status_code == 200:
            html_content = workflow_response.text
            
            # Look for signs that our fix is deployed
            has_brightdata_call = '/api/brightdata/trigger-scraper/' in html_content
            has_csrf_token = 'getCsrfToken' in html_content
            
            print(f"   Workflow page loaded: ✅")
            print(f"   Contains BrightData API call: {'✅' if has_brightdata_call else '❌'}")
            print(f"   Contains CSRF token function: {'✅' if has_csrf_token else '❌'}")
            
            if not (has_brightdata_call and has_csrf_token):
                print("   ⚠️  Frontend fix might not be deployed yet!")
        else:
            print(f"   ❌ Workflow page failed: {workflow_response.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend check error: {e}")
        
    print("\n" + "=" * 50)
    print("🎯 INSTANT JAVASCRIPT FIX FOR CONSOLE:")
    print("=" * 50)
    print("""
PASTE THIS INTO YOUR BROWSER CONSOLE RIGHT NOW:

// EMERGENCY INSTANT RUN FIX - PASTE IN CONSOLE
(function() {
    console.log('🚀 Emergency Instant Run Fix Loading...');
    
    // Find the instant run button
    const findButton = () => {
        return document.querySelector('[data-testid="instant-run"]') ||
               document.querySelector('.instant-run') ||
               document.querySelector('#instant-run-btn') ||
               document.querySelector('button:contains("Instant Run")') ||
               Array.from(document.querySelectorAll('button')).find(btn => 
                   btn.textContent.includes('Instant Run')
               ) ||
               // Look for the card with "Instant Run" text
               Array.from(document.querySelectorAll('[role="button"], .MuiCardActionArea-root')).find(el => 
                   el.textContent.includes('Instant Run')
               );
    };
    
    const button = findButton();
    if (!button) {
        console.error('❌ Instant Run button not found!');
        console.log('Available buttons:', Array.from(document.querySelectorAll('button')).map(b => b.textContent));
        return;
    }
    
    console.log('✅ Found button:', button);
    
    // Replace with working version
    button.onclick = async function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('🚀 EMERGENCY INSTANT RUN TRIGGERED!');
        
        // Show loading
        const originalText = button.textContent;
        button.textContent = 'Running...';
        button.disabled = true;
        
        try {
            // Call BrightData API directly
            const response = await fetch('/api/brightdata/trigger-scraper/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    platform: 'instagram',
                    urls: ['https://www.instagram.com/nike/', 'https://www.instagram.com/adidas/']
                })
            });
            
            const data = await response.json();
            console.log('📊 Response:', data);
            
            if (data.success) {
                alert(`✅ SUCCESS! Instagram scraper started!\\n\\nJob ID: ${data.batch_job_id}\\nDataset: ${data.dataset_id}\\n\\nCheck BrightData dashboard!`);
                button.textContent = '✅ Started!';
            } else {
                alert(`❌ Error: ${data.error || 'Unknown error'}`);
                button.textContent = '❌ Failed';
            }
            
        } catch (error) {
            console.error('Error:', error);
            alert(`❌ Connection Error: ${error.message}`);
            button.textContent = '❌ Error';
        }
        
        // Reset button after 3 seconds
        setTimeout(() => {
            button.textContent = originalText;
            button.disabled = false;
        }, 3000);
    };
    
    // CSRF token function
    function getCsrfToken() {
        const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }
    
    console.log('✅ Emergency fix applied! Try clicking Instant Run now!');
})();
""")
    
    print("\n📋 STEPS TO FIX RIGHT NOW:")
    print("1. Go to your workflow page")
    print("2. Press F12 → Console tab")
    print("3. Paste the JavaScript code above")
    print("4. Press Enter")
    print("5. Click 'Instant Run' - it should work!")

if __name__ == "__main__":
    emergency_frontend_debug()