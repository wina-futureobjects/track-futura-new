# 🚨 EMERGENCY UPSUN DEPLOYMENT FIX

## **PROBLEM IDENTIFIED:**
- Webhook returns 500 errors (ModuleNotFoundError)
- API endpoints return 404 errors
- Django backend partially broken on Upsun

## **IMMEDIATE FIX STEPS:**

### **1. SSH INTO UPSUN**
```bash
upsun ssh
```

### **2. CHECK DJANGO STATUS**
```bash
cd /app
python manage.py check
python manage.py migrate --plan
```

### **3. FIX MISSING DEPENDENCIES**
```bash
# Check what's missing
python -c "import brightdata_integration; print('OK')"
python -c "import instagram_data; print('OK')"

# If errors, run:
pip install -r requirements.txt --force-reinstall
```

### **4. RUN DATABASE MIGRATIONS**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### **5. TEST DJANGO FUNCTIONALITY**
```bash
# Test basic Django
python manage.py shell -c "
from django.conf import settings
print('Django settings loaded')
from instagram_data.models import Folder
print('Instagram models imported')
from brightdata_integration.models import ScraperRequest
print('BrightData models imported')
"
```

### **6. CREATE MISSING SCRAPER REQUEST**
```bash
python manage.py shell
```

**In Django shell:**
```python
from brightdata_integration.models import ScraperRequest, BrightdataConfig
from instagram_data.models import Folder

# Check if models work
print("Testing models...")

# Get latest folder
latest_folder = Folder.objects.order_by('-id').first()
if latest_folder:
    print(f"Latest folder: {latest_folder.name} (ID: {latest_folder.id})")

    # Get or create config
    config, created = BrightdataConfig.objects.get_or_create(
        name='Emergency Config',
        defaults={'config_id': 'emergency_config'}
    )
    print(f"Config: {config.name} (Created: {created})")

    # Create ScraperRequest
    import time
    request_id = f"emergency_fix_{int(time.time())}"

    scraper_request = ScraperRequest.objects.create(
        config=config,
        folder=latest_folder,
        request_id=request_id,
        platform='instagram',
        status='pending'
    )

    print(f"✅ Created ScraperRequest:")
    print(f"   ID: {scraper_request.id}")
    print(f"   Request ID: {scraper_request.request_id}")
    print(f"   Folder: {scraper_request.folder.name}")

    print(f"\n🎯 USE THIS IN BRIGHTDATA:")
    print(f"   X-Snapshot-Id: {scraper_request.request_id}")
else:
    print("❌ No folders found!")
```

### **7. TEST WEBHOOK ENDPOINT**
```bash
# Test from inside Upsun
curl -X POST http://localhost:8000/api/brightdata/webhook/ \
  -H "Content-Type: application/json" \
  -H "X-Platform: instagram" \
  -H "X-Snapshot-Id: test_internal" \
  -d '[{"test": true}]'
```

### **8. RESTART SERVICES**
```bash
# Force restart the application
exit  # Exit SSH
```

```bash
# From local machine
upsun app:restart backend
```

## **AFTER FIXING BACKEND:**

### **UPDATE BRIGHTDATA CONFIGURATION:**

1. **Webhook URL:**
   ```
   https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/
   ```

2. **Headers:**
   - `Content-Type: application/json`
   - `X-Platform: instagram`
   - `X-Snapshot-Id: emergency_fix_[timestamp]` (use the one created above)

3. **Test Webhook:**
   - Run new scraping job
   - Check if data appears in folder
   - Monitor with: `python webhook_monitor_upsun.py`

## **VERIFICATION STEPS:**

### **Test API Endpoints:**
```bash
# Test these URLs should return JSON, not 404:
curl https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/instagram_data/folders/
curl https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/health/
```

### **Test Complete Workflow:**
1. Create folder in app
2. Create ScraperRequest (manually until app interface fixed)
3. Update BrightData with correct webhook URL and X-Snapshot-Id
4. Run scraping job
5. Check folder for data

## **🎯 SUCCESS CRITERIA:**
- ✅ Webhook returns 200 OK (not 500 errors)
- ✅ API endpoints return JSON (not 404 errors)
- ✅ ScraperRequest created and linked to folder
- ✅ BrightData webhook URL updated
- ✅ Data appears in folder after scraping

**This should fix your entire scraping workflow!**
