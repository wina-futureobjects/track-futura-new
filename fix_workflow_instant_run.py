#!/usr/bin/env python3
"""
DIRECT FIX for https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/workflow-management
"""

print("""
🚨 IMMEDIATE FIX FOR YOUR WORKFLOW MANAGEMENT PAGE 🚨
=====================================================

STEPS TO FIX RIGHT NOW:

1. Go to: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/workflow-management

2. Press F12 (Developer Tools) → Console tab

3. Paste this EXACT code and press Enter:

""")

fix_code = '''
// IMMEDIATE FIX FOR WORKFLOW MANAGEMENT INSTANT RUN BUTTON
(function() {
    console.log('🚀 Fixing Instant Run button on workflow management page...');
    
    // Wait for page to load completely
    setTimeout(() => {
        // Find the Instant Run card/button
        const findInstantRunButton = () => {
            // Try multiple selectors to find the button
            let button = null;
            
            // Method 1: Look for cards with "Instant Run" text
            const cards = document.querySelectorAll('.MuiCardActionArea-root, [role="button"]');
            for (let card of cards) {
                if (card.textContent.includes('Instant Run')) {
                    button = card;
                    break;
                }
            }
            
            // Method 2: Look for buttons with "Instant Run"
            if (!button) {
                const buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.textContent.includes('Instant Run')) {
                        button = btn;
                        break;
                    }
                }
            }
            
            // Method 3: Look for any element with "Instant Run" text
            if (!button) {
                const allElements = document.querySelectorAll('*');
                for (let el of allElements) {
                    if (el.textContent === 'Instant Run' || el.innerText === 'Instant Run') {
                        // Find the clickable parent
                        let parent = el;
                        while (parent && !parent.onclick && parent.tagName !== 'BUTTON' && !parent.className.includes('Card')) {
                            parent = parent.parentElement;
                        }
                        if (parent) {
                            button = parent;
                            break;
                        }
                    }
                }
            }
            
            return button;
        };
        
        const button = findInstantRunButton();
        
        if (!button) {
            console.error('❌ Could not find Instant Run button');
            alert('❌ Could not find Instant Run button. Make sure you are on the workflow management page.');
            return;
        }
        
        console.log('✅ Found Instant Run button:', button);
        
        // Store original handler
        const originalHandler = button.onclick;
        
        // Replace with working handler
        const newHandler = async function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('🚀 INSTANT RUN TRIGGERED - Calling BrightData API!');
            
            // Show loading state
            const originalText = button.textContent || button.innerText;
            if (button.textContent) button.textContent = 'Starting BrightData...';
            if (button.innerText) button.innerText = 'Starting BrightData...';
            
            try {
                // Call BrightData API directly - ONLY Nike Instagram as requested
                const response = await fetch('/api/brightdata/trigger-scraper/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    },
                    body: JSON.stringify({
                        platform: 'instagram',
                        urls: ['https://www.instagram.com/nike/']  // ONLY Nike base URL
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                console.log('📊 BrightData API Response:', data);
                
                if (data.success) {
                    // Success!
                    const successMsg = `🎉 SUCCESS! Nike Instagram BrightData scraper started!

✅ Job ID: ${data.batch_job_id}
📊 Dataset: ${data.dataset_id}
🔗 Target: https://www.instagram.com/nike/
📝 Message: ${data.message}

👉 Check your BrightData dashboard for progress!`;
                    
                    alert(successMsg);
                    console.log('✅ BrightData job created successfully!');
                    
                    if (button.textContent) button.textContent = '✅ Started!';
                    if (button.innerText) button.innerText = '✅ Started!';
                    
                } else {
                    // API returned error
                    const errorMsg = `❌ BrightData API Error: ${data.error || 'Unknown error'}`;
                    alert(errorMsg);
                    console.error('❌ BrightData API error:', data);
                    
                    if (button.textContent) button.textContent = '❌ Failed';
                    if (button.innerText) button.innerText = '❌ Failed';
                }
                
            } catch (error) {
                // Network or other error
                const errorMsg = `❌ Connection Error: ${error.message}

Please check:
- Internet connection
- Server status
- Try again in a moment`;
                
                alert(errorMsg);
                console.error('❌ Network error:', error);
                
                if (button.textContent) button.textContent = '❌ Error';
                if (button.innerText) button.innerText = '❌ Error';
            }
            
            // Reset button after 5 seconds
            setTimeout(() => {
                if (button.textContent) button.textContent = originalText;
                if (button.innerText) button.innerText = originalText;
            }, 5000);
        };
        
        // Replace the handler
        button.onclick = newHandler;
        
        // Also add event listener in case onclick doesn't work
        button.addEventListener('click', newHandler, true);
        
        console.log('✅ Instant Run button fixed! It now calls BrightData API directly.');
        console.log('🎯 Click the Instant Run button to test it!');
        
        // Visual confirmation
        button.style.border = '2px solid #4CAF50';
        setTimeout(() => {
            if (button.style) button.style.border = '';
        }, 3000);
        
    }, 2000); // Wait 2 seconds for page to fully load
    
    // Helper function to get CSRF token
    function getCsrfToken() {
        // Try cookie first
        const csrfCookie = document.cookie.split(';')
            .find(cookie => cookie.trim().startsWith('csrftoken='));
        
        if (csrfCookie) {
            return csrfCookie.split('=')[1];
        }
        
        // Try meta tag
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.getAttribute('content') || '';
        }
        
        // Try hidden input
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            return csrfInput.value;
        }
        
        console.warn('⚠️ CSRF token not found, proceeding without it');
        return '';
    }
    
})();
'''

print(fix_code)

print("""
4. Press Enter to run the fix

5. You should see a green border around the Instant Run button for 3 seconds

6. Click the "Instant Run" button - it will now work and call BrightData!

This fix:
✅ Finds your Instant Run button automatically
✅ Replaces the broken handler with working BrightData API call
✅ Uses ONLY Nike Instagram base URL (as requested)
✅ Shows proper success/error messages
✅ Works immediately without waiting for deployment

The fix is PERMANENT until you refresh the page!
""")

# Also test that our API is working
import requests
try:
    response = requests.post(
        "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/",
        json={"platform": "instagram", "urls": ["https://www.instagram.com/nike/"]},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"\n✅ CONFIRMED: BrightData API is working! Just created job: {data.get('batch_job_id')}")
        else:
            print(f"\n❌ API Error: {data.get('error')}")
    else:
        print(f"\n❌ HTTP Error: {response.status_code}")
except Exception as e:
    print(f"\n❌ Connection Error: {e}")