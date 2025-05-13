# Deployment Guide for Track Futura

## Fixed Issue: Frontend API Connection

We fixed an issue where the frontend couldn't connect to the backend API when deployed to Upsun. The problem was:

1. In development, the Vite dev server proxies `/api` requests to the backend
2. But in production on Upsun, the backend is deployed at a different URL (`https://api.{domain}/`)
3. The frontend was still using relative URLs like `/api/track-accounts/folders/` which were returning HTML instead of JSON

### Solution

We created a configuration system that:

1. Detects whether the app is running in development or production
2. Uses the correct API URL: 
   - In development: relative URLs (which get proxied)
   - In production: absolute URLs to the API domain (`https://api.{domain}/`)

### Custom Backend URL

If your frontend and backend are on completely different domains, you can specify a custom backend URL:

1. Set the `VITE_API_URL` environment variable during build:
   ```
   VITE_API_URL=https://your-custom-api-domain.com npm run build
   ```

2. Or use the custom build script if deploying on Upsun:
   ```
   BACKEND_URL=https://your-custom-api-domain.com npm run build:custom
   ```

### Changes Made

1. Added a new configuration file: `frontend/src/config.ts` 
2. Added an API utility: `frontend/src/utils/api.ts`
3. Updated the frontend components to use the API utility
4. Modified the Vite config to only use the proxy in development mode

### Redeploying the App

To redeploy with these changes:

1. Commit the changes to your repository
2. Push to your Upsun repository:
   ```
   git push upsun main
   ```

3. The deployment will automatically trigger, and the frontend should now be able to communicate with the backend correctly.

## Troubleshooting

If you still encounter issues after deploying:

1. Check the browser console for network errors
2. Verify that the API URL is correctly set to `https://api.{domain}/` in production
3. Ensure that the CORS settings in the Django backend allow requests from your frontend domain

You can add more debugging info by modifying the `apiRequest` function in `frontend/src/utils/api.ts` to log the complete URL being used:

```javascript
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  console.log('API Request to:', url);
  // rest of the function
}
``` 