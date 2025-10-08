"""
Force deployment trigger - production sync check
This file forces a new deployment to ensure all BrightData fixes are live.
Created: 2025-10-08 04:46 UTC
"""

# All critical fixes should be deployed:
# 1. BrightDataAutomatedBatchScraper with Web Unlocker API
# 2. _get_target_url_for_platform method
# 3. _get_or_create_config method  
# 4. Web Unlocker API endpoint /request
# 5. Correct zone parameter format
# 6. JSON error handling
# 7. response_data field in model

DEPLOYMENT_VERSION = "v2.1.3"
BRIGHTDATA_FIXES_COMPLETE = True