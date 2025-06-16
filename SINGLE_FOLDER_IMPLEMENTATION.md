# 🔧 SINGLE SHARED FOLDER IMPLEMENTATION

## 🎯 **WHAT CHANGED**

I've updated the automated batch scraper to create **ONE SINGLE FOLDER per scraping job** that contains data from ALL accounts, instead of separate folders for each account.

## ✅ **NEW BEHAVIOR**

### **Before (Smart Folder Matching)**:
- ❌ Posts from `@account_a` → `Instagram_POSTS_2024-12-16_JobName_AccountA`
- ❌ Posts from `@account_b` → `Instagram_POSTS_2024-12-16_JobName_AccountB`
- ❌ Posts from `@account_c` → `Instagram_POSTS_2024-12-16_JobName_AccountC`

### **After (Single Shared Folder)**:
- ✅ **ALL posts** → `Instagram_POSTS_2024-12-16_JobName`
- ✅ Data from all 5 accounts stored in ONE folder
- ✅ Folder named with scraping date

## 🔧 **TECHNICAL CHANGES**

### **1. Folder Creation Logic** (`services.py`)
**Changed**: `_get_or_create_output_folder()` method

```python
# OLD: Used account_name in folder pattern
folder_name = job.output_folder_pattern.format(
    platform=platform.title(),
    content_type=content_type_for_name.upper(),
    date=timezone.now().strftime('%Y-%m-%d'),
    job_name=job.name,
    account_name=source.name,  # ❌ This created separate folders
)

# NEW: Single folder per job (no account_name)
folder_name = f"{platform.title()}_{content_type_for_name.upper()}_{timezone.now().strftime('%Y-%m-%d')}_{job.name}"
```

### **2. Webhook Processing** (`views.py`)
**Simplified**: `_process_webhook_data_with_batch_support()` method

```python
# OLD: Smart folder matching based on username
user_posted = post_data.get('user_posted', '')
for mapped_url, mapped_folder_id in url_to_folder_map.items():
    if user_posted.lower() in mapped_url.lower():
        folder_id = mapped_folder_id
        break

# NEW: All posts use the same shared folder
shared_folder_id = scraper_requests[0].folder_id
folder_id = shared_folder_id  # Same for ALL posts
```

## 🚀 **HOW IT WORKS NOW**

### **Scraping Flow**:
1. **Create Job**: User creates batch job for 5 Instagram accounts
2. **Single Folder**: System creates ONE folder: `Instagram_POSTS_2024-12-16_MyJob`
3. **All Requests Share Folder**: All 5 `ScraperRequest` objects get the same `folder_id`
4. **Batch API Call**: ONE API call to BrightData with all 5 URLs
5. **Same snapshot_id**: ALL requests get the same `snapshot_id`
6. **Webhook Processing**: When data arrives:
   - Finds ALL requests with matching `snapshot_id`
   - Uses the shared `folder_id` for ALL posts
   - Stores ALL posts in the SAME folder

### **Result**:
✅ **Single folder**: `Instagram_POSTS_2024-12-16_MyJob`
✅ **Contains posts from**: @account_a, @account_b, @account_c, @account_d, @account_e
✅ **Easy organization**: All data from one scraping session in one place
✅ **Date-based naming**: Clear when the scraping was performed

## 📊 **FOLDER NAMING PATTERN**

```
{Platform}_{ContentType}_{Date}_{JobName}
```

**Examples**:
- `Instagram_POSTS_2024-12-16_DailyScrap`
- `Instagram_REELS_2024-12-16_WeeklyCheck`
- `Facebook_POSTS_2024-12-16_CompetitorAnalysis`

## 🧪 **TESTING**

### **Expected Behavior**:
1. Run automated batch scraper with 5 accounts
2. System creates ONE folder with today's date
3. ALL posts from ALL accounts appear in that single folder
4. No more separate folders per account

### **Verification**:
- Check Instagram data section
- Look for folder named: `Instagram_POSTS_YYYY-MM-DD_JobName`
- Verify it contains posts from multiple accounts
- Check that Folder field is no longer "null"

## 🔄 **DEPLOYMENT STATUS**

- ✅ **Code Updated**: Both `services.py` and `views.py` modified
- ✅ **Committed**: Changes committed to git
- ✅ **Pushed**: Deployed to `upsun-deployment` branch
- 🚀 **Ready for Testing**: System now uses single shared folders

---

**🎉 IMPLEMENTATION COMPLETE!**

Your automated batch scraper now creates **one single folder per scraping job** that contains data from all accounts, named with the scraping date as requested!
