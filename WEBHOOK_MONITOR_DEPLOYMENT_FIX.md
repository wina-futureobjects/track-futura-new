# Webhook Monitor Deployment Fix for Upsun

## Issue Summary

The webhook monitor dashboard at `https://upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/organizations/4/projects/10/webhook-monitor` was showing "Failed to fetch webhook data" due to incorrect API base URL configuration in the frontend.

## Root Cause Analysis

1. **Missing Environment Variable**: The frontend was looking for `VITE_API_BASE_URL` but it wasn't set in the Upsun deployment configuration.

2. **Incorrect API URL Construction**: The frontend was defaulting to `http://localhost:8000` when the environment variable wasn't found, which doesn't work in the Upsun deployment.

3. **No Fallback Logic**: There was no automatic detection of the deployment environment to construct the correct API URL.

## Fixes Applied

### 1. Updated Upsun Configuration (`.upsun/config.yaml`)

Added dynamic API base URL configuration to the frontend build process:

```yaml
frontend:
  # ... existing config ...
  hooks:
    build: |
      # Extract the domain from PLATFORM_ROUTES and set API base URL
      if [ -n "$PLATFORM_ROUTES" ]; then
        DOMAIN=$(echo $PLATFORM_ROUTES | base64 --decode | jq -r 'to_entries[] | select(.value.primary == true) | .key' | sed 's:/*$::' | sed 's|https\?://||')
        export VITE_API_BASE_URL="https://api.${DOMAIN}"
        echo "Setting VITE_API_BASE_URL to: https://api.${DOMAIN}"
      else
        export VITE_API_BASE_URL="http://localhost:8000"
        echo "Using default VITE_API_BASE_URL: http://localhost:8000"
      fi
      npm install
      npm run build
```

### 2. Enhanced Frontend API Detection (`frontend/src/services/webhookService.ts`)

Added intelligent API base URL detection with multiple fallback strategies:

```typescript
// Determine API base URL with fallback logic for different deployment environments
const getApiBaseUrl = (): string => {
  // First check for explicit environment variable
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }

  // For production deployments, try to detect the API URL from current location
  if (typeof window !== 'undefined') {
    const currentHost = window.location.host;
    const currentProtocol = window.location.protocol;

    // If we're on a deployment platform (like Upsun), construct API URL
    if (currentHost.includes('.upsun.app') || currentHost.includes('.platformsh.site')) {
      return `${currentProtocol}//api.${currentHost}`;
    }
  }

  // Default fallback for development
  return 'http://localhost:8000';
};
```

### 3. Added Connection Testing and Debug Information

Enhanced the webhook service with:

- **Connection Testing**: Automatic API connectivity testing before data fetching
- **Detailed Error Reporting**: Better error messages with specific failure details
- **Debug Information Panel**: Temporary debug panel showing configuration details

### 4. Improved Error Handling

Updated the WebhookMonitorDashboard component to:

- Test connection before attempting to fetch data
- Provide detailed error messages
- Show debug information for troubleshooting

## Deployment Instructions

### 1. Deploy the Changes

```bash
# Commit the changes
git add .
git commit -m "Fix webhook monitor API connectivity for Upsun deployment"

# Push to Upsun
git push upsun main
```

### 2. Verify the Deployment

1. **Check Build Logs**: Look for the API base URL configuration messages in the frontend build logs
2. **Test the Webhook Monitor**: Navigate to the webhook monitor page and check the debug information panel
3. **Verify API Connectivity**: The debug panel will show connection test results

### 3. Expected Debug Information

When you visit the webhook monitor page, you should see a debug panel showing:

```
🔧 Debug Information (Deployment Troubleshooting)
Current URL: https://upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/organizations/4/projects/10/webhook-monitor
Current Host: upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site
API Base URL: https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site
Environment: production (Dev: No)
Connection Test: ✅ Success
```

### 4. Remove Debug Information (Production)

Once the issue is resolved, remove the debug panel by:

1. Removing the debug information section from `WebhookMonitorDashboard.tsx`
2. Removing the `testConnection` method calls
3. Cleaning up console.log statements

## Testing the Fix

### Manual Testing

1. **Visit the Webhook Monitor**: Go to the webhook monitor URL
2. **Check Debug Panel**: Verify the API base URL is correctly set
3. **Test API Calls**: The dashboard should load webhook data successfully
4. **Check Browser Console**: Look for successful API calls and no CORS errors

### API Endpoint Testing

Test the webhook endpoints directly:

```bash
# Test webhook metrics
curl "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/metrics/"

# Test webhook health
curl "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/health/"
```

## Troubleshooting

### If the Issue Persists

1. **Check Build Logs**: Verify the `VITE_API_BASE_URL` is being set correctly during build
2. **Verify Routes**: Ensure the API routes are properly configured in Upsun
3. **Check CORS Settings**: The Django backend has permissive CORS settings, but verify they include the frontend domain
4. **Test Backend Directly**: Use curl to test the backend API endpoints directly

### Common Issues

1. **CORS Errors**: Check Django CORS settings in `backend/config/settings.py`
2. **404 Errors**: Verify the API routes are correctly configured
3. **Build Failures**: Check that `jq` is available in the build environment

## Backend Configuration

The Django backend is already configured with:

- **Permissive CORS**: Allows all origins for development/testing
- **Webhook Endpoints**: All webhook monitoring endpoints are available
- **Health Checks**: API health endpoint for connectivity testing

## Security Considerations

- The debug information panel should be removed in production
- Consider restricting CORS origins to specific domains in production
- Ensure webhook authentication tokens are properly configured

## Next Steps

1. **Monitor the Deployment**: Check if the webhook monitor loads successfully
2. **Test Webhook Functionality**: Verify that webhook data is being collected and displayed
3. **Clean Up Debug Code**: Remove debug information once the issue is confirmed resolved
4. **Document the Solution**: Update deployment documentation with these configuration requirements

This fix addresses the core issue of API connectivity between the frontend and backend in the Upsun deployment environment.
