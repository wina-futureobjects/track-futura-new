# Apify Polling Service Guide

## Problem
Apify webhooks require a public URL to send status updates. When running locally or without a public webhook URL, scraper requests get stuck in "processing" status even after Apify completes the scraping.

## Solution
We've implemented a **polling service** that periodically checks Apify for run status updates and automatically downloads results when jobs complete.

## How It Works

1. When you start a scraping job, it creates an `ApifyScraperRequest` with status "processing"
2. The polling service checks Apify API every 30 seconds for updates
3. When Apify completes a run, the service:
   - Updates the request status to "completed"
   - Downloads the scraped data
   - Saves posts to the database
   - Creates folders with the format: `"Source Folder Name - DD/MM/YYYY HH:MM:SS"`
   - Updates the batch job status

## Usage

### Option 1: Run Once (Manual Check)
```bash
cd backend
./venv/Scripts/python manage.py poll_apify_runs
```

This checks all active runs once and exits.

### Option 2: Continuous Polling (Recommended)
```bash
cd backend
./venv/Scripts/python manage.py poll_apify_runs --continuous
```

This runs continuously, checking every 30 seconds. Press Ctrl+C to stop.

### Option 3: Use the Batch File (Windows)
```bash
cd backend
start_polling.bat
```

This is a convenient wrapper that starts continuous polling.

### Option 4: Custom Interval
```bash
./venv/Scripts/python manage.py poll_apify_runs --continuous --interval 60
```

This polls every 60 seconds instead of the default 30.

## Recommended Setup

### For Development (Local)
1. Start your Django server in one terminal:
   ```bash
   cd backend
   ./venv/Scripts/python manage.py runserver
   ```

2. Start the polling service in another terminal:
   ```bash
   cd backend
   start_polling.bat
   ```

### For Production
Set up a systemd service (Linux) or Windows Service to run the polling continuously in the background.

**Linux systemd example:**
```ini
[Unit]
Description=TrackFutura Apify Polling Service
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/TrackFutura/backend
ExecStart=/path/to/TrackFutura/backend/venv/bin/python manage.py poll_apify_runs --continuous --interval 30
Restart=always

[Install]
WantedBy=multi-user.target
```

## What Gets Updated

When the polling service detects a completed run:

✅ **Scraper Request Status**: `processing` → `completed`
✅ **Downloads Data**: Fetches all scraped posts from Apify
✅ **Creates Folders**: Named as "Source Folder Name - DD/MM/YYYY HH:MM:SS"
✅ **Saves Posts**: Stores all posts in the database
✅ **Batch Job Status**: Updates overall job status when all requests complete

## Folder Naming

The new folder naming format includes your source folder name and the exact date/time:

- **With source folder**: `"Brand Sources - 06/10/2025 14:30:00"`
- **Multiple folders**: `"Nike, Adidas - 06/10/2025 14:30:00"`
- **No folder**: `"Facebook Scrape - 06/10/2025 14:30:00"`

## Troubleshooting

### Runs stuck in "processing"?
1. Check if polling service is running
2. Manually run: `./venv/Scripts/python manage.py poll_apify_runs`
3. Check the console output for errors

### No data appearing?
1. Verify the run completed successfully in Apify dashboard
2. Check the batch job status in Django admin
3. Look for error messages in the polling output

### Polling service crashes?
1. Check your Apify API token is valid
2. Ensure network connectivity to Apify API
3. Review error logs for specific issues

## Future Enhancement: Webhooks

Once you have a public URL (e.g., deployed to production), you can switch to webhooks for instant updates instead of polling. The webhook endpoint is already implemented at:

```
POST /api/apify/webhook/
```

To enable webhooks, update the `webhook_base` in `apify_integration/services.py` line 356 to your public URL.
