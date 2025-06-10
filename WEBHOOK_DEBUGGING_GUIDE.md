# Webhook Debugging Guide - Complete Solution

## 🔍 Problem Analysis

Your Instagram folder is being created but remains empty even after scraping finishes. The issue is **NOT** with the webhook system - it's with the connection between your scraper and the webhook.

## ✅ Current Status (What's Working)

- ✅ Webhook endpoints are working (`/api/brightdata/webhook/`)
- ✅ Folder creation is working (folder ID 46 exists)
- ✅ Data processing is working (1,143 posts saved in other folders)
- ✅ Instagram data parsing is working

## ❌ The Actual Problem

**NO scraper requests are being created for your newest folder.** This means:
- You're running scraping directly in BrightData dashboard
- Your app doesn't know about the scraping job
- When BrightData sends webhook data, there's no folder association

## 🚀 Complete Solution

### Step 1: Check Your Workflow

**WRONG WAY (What you're doing now):**
```
1. Create folder in your app
2. Go to BrightData dashboard
3. Run scraper manually
4. Webhook has no way to know which folder to use
```

**RIGHT WAY (What you should do):**
```
1. Create folder in your app
2. Use your app's scraper interface to trigger the scrape
3. App creates ScraperRequest with folder_id
4. BrightData sends webhook with request_id
5. Webhook matches request_id to folder_id
```

### Step 2: Debug Your Current Setup

Run this to see what's happening:

```bash
# Check your Django server is running
python backend/manage.py runserver

# In another terminal, check folder status
python check_instagram_debug.py

# Check recent scraper requests
python detailed_folder_debug.py
```

### Step 3: Fix the Workflow

**Option A: Use Your App's Scraper Interface**
1. Go to your app's Instagram scraper page
2. Select folder "sadfewfwfwe2f2f" (ID: 46)
3. Enter the Instagram URL you want to scrape
4. Click "Start Scraping"
5. This will create a proper ScraperRequest with folder_id

**Option B: Create Manual Test**
```bash
# Test with a specific folder
python test_folder_46_webhook.py
```

### Step 4: Verify BrightData Webhook Configuration

1. **Check your BrightData webhook URL:**
   - Should be: `https://your-ngrok-url.ngrok.io/api/brightdata/webhook/`
   - NOT: `https://your-ngrok-url.ngrok.io/api/brightdata/webhook/instagram/`

2. **Check webhook authentication:**
   - Your webhook token should match `BRIGHTDATA_WEBHOOK_TOKEN` in your .env

3. **Check webhook headers:**
   ```
   X-Platform: instagram
   X-Snapshot-Id: your_request_id
   Content-Type: application/json
   ```

### Step 5: Test the Complete Flow

1. **Start your servers:**
   ```bash
   # Terminal 1: Django
   cd backend
   python manage.py runserver

   # Terminal 2: React (if needed)
   cd frontend
   npm run dev
   ```

2. **Create a test scraper request:**
   ```python
   # In Django shell
   python manage.py shell

   from brightdata_integration.models import ScraperRequest
   from instagram_data.models import Folder

   # Get your folder
   folder = Folder.objects.get(id=46)

   # Create scraper request
   request = ScraperRequest.objects.create(
       platform='instagram',
       target_url='https://www.instagram.com/your_target_account',
       request_id='test_folder_46_' + str(int(time.time())),
       folder_id=folder.id,
       status='processing'
   )
   ```

3. **Configure BrightData to use the request_id:**
   - In BrightData, set the webhook URL to include the request_id
   - Or configure the scraper to use the request_id as snapshot_id

### Step 6: Test Direct Webhook (For Immediate Debugging)

```bash
# This will test if webhook processing works
python test_webhook_simulation.py
```

## 🎯 Quick Fix for Immediate Testing

If you want to test with your current setup:

1. **Find your actual BrightData request/snapshot ID**
2. **Create a matching ScraperRequest:**

```python
# In Django shell
from brightdata_integration.models import ScraperRequest
from instagram_data.models import Folder

ScraperRequest.objects.create(
    platform='instagram',
    target_url='https://www.instagram.com/your_target',
    request_id='YOUR_ACTUAL_BRIGHTDATA_REQUEST_ID',  # Use real ID
    folder_id=46,  # Your folder ID
    status='processing'
)
```

3. **Re-run your BrightData scraper** - it should now assign data to folder 46

## 🔧 Debug Commands

```bash
# Check current state
python check_instagram_debug.py

# Check specific folder
python detailed_folder_debug.py

# Test webhook processing
python simple_webhook_test_folder_46.py

# Test complete flow
python test_folder_46_webhook.py
```

## 📋 Checklist for Success

- [ ] Django server running on port 8000
- [ ] Ngrok or webhook URL accessible to BrightData
- [ ] ScraperRequest created with correct folder_id
- [ ] BrightData webhook configured with correct URL
- [ ] BrightData sending correct X-Snapshot-Id header
- [ ] Webhook authentication token matches
- [ ] Instagram target URL is valid

## 🆘 If Still Not Working

**Check these common issues:**

1. **Webhook URL not accessible:**
   ```bash
   curl -X POST http://localhost:8000/api/brightdata/webhook/health/
   ```

2. **Authentication failing:**
   - Check `BRIGHTDATA_WEBHOOK_TOKEN` in your .env
   - Verify BrightData is sending Authorization header

3. **Request ID mismatch:**
   - BrightData `X-Snapshot-Id` must match ScraperRequest `request_id`

4. **Platform mismatch:**
   - BrightData `X-Platform` must be `instagram`

5. **Data format issues:**
   - Check if BrightData is sending expected JSON structure

## 💡 Prevention

To avoid this issue in the future:
1. Always use your app's scraper interface
2. Never run scraping directly in BrightData dashboard
3. Always verify ScraperRequest is created before scraping
4. Monitor webhook logs for processing errors

The key insight is that **your webhook system works perfectly** - you just need to create the proper ScraperRequest to link the folder with the scraping job.
