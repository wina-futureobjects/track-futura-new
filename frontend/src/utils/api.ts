/**
 * Returns the base URL for API requests, automatically handling development vs production environments
 */
export const getApiBaseUrl = (): string => {
  // Use the global API base URL if available
  if (typeof window !== 'undefined' && (window as any).API_BASE_URL !== undefined) {
    return (window as any).API_BASE_URL;
  }

  // Fall back to environment-specific logic
  if (import.meta.env.PROD) {
    // In production, get the current hostname
    const hostname = typeof window !== 'undefined' ? window.location.hostname : '';
    const protocol = typeof window !== 'undefined' ? window.location.protocol : 'https:';

    console.log('🔍 Production API Detection:', { hostname, protocol });

    // 🚨 SPECIFIC FIX FOR UPSUN DEPLOYMENT 🚨
    // If we're on the Upsun domain, use the exact API URL
    if (hostname.includes('upsun-deployment') || hostname.includes('.platformsh.site')) {
      const apiUrl = `${protocol}//${hostname}`;
      console.log('✅ Using Upsun API URL:', apiUrl);
      return apiUrl;
    }

    // For other production environments, use same domain
    const apiUrl = `${protocol}//${hostname}`;
    console.log('✅ Using production API URL:', apiUrl);
    return apiUrl;
  }

  // In development, try to use the direct backend URL if proxy is not working
  // Check if we're running on localhost:5173 (Vite dev server)
  if (typeof window !== 'undefined' && window.location.port === '5173') {
    // Use direct backend URL to bypass potential proxy issues
    console.log('✅ Using development direct API URL: http://localhost:8000');
    return 'http://localhost:8000';
  }

  // Default: use relative URLs which will be handled by the Vite proxy
  console.log('✅ Using relative API URLs (proxy)');
  return '';
};

/**
 * Creates a complete API URL by combining the base URL with the endpoint
 */
export const createApiUrl = (endpoint: string): string => {
  const baseUrl = getApiBaseUrl();
  // Ensure endpoint starts with /api/
  const formattedEndpoint = endpoint.startsWith('/api/') ? endpoint : `/api/${endpoint.replace(/^\//, '')}`;
  const fullUrl = `${baseUrl}${formattedEndpoint}`;

  console.log('🔗 API URL Created:', { endpoint, baseUrl, fullUrl });
  return fullUrl;
};

/**
 * Wrapper for the fetch API that automatically adds the API base URL and auth token
 * Now with enhanced error handling and cloud environment compatibility
 */
export const apiFetch = (endpoint: string, options?: RequestInit): Promise<Response> => {
  const url = createApiUrl(endpoint);
  console.log('📡 API Fetch:', { endpoint, url, method: options?.method || 'GET' });

  // Get auth token from localStorage if available
  const token = localStorage.getItem('authToken');

  // Prepare headers with minimal requirements for testing
  const headers = {
    ...(options?.headers || {}),
    ...(token ? { 'Authorization': `Token ${token}` } : {}),
    // Basic headers for cross-origin compatibility
    'Accept': 'application/json',
    // Only add Content-Type if it's not FormData (for file uploads)
    ...(!options?.body || !(options.body instanceof FormData) ? { 'Content-Type': 'application/json' } : {})
  };

  const fetchOptions = {
    ...options,
    headers,
    // Try without credentials first for maximum compatibility
    credentials: 'omit' as RequestCredentials,
    // Set mode to handle CORS more permissively
    mode: 'cors' as RequestMode
  };

  console.log('📤 Fetch Options:', { url, headers, method: options?.method });

  // Enhanced error handling with logging
  return fetch(url, fetchOptions)
    .then(response => {
      console.log('📥 Response received:', {
        status: response.status,
        statusText: response.statusText,
        contentType: response.headers.get('content-type'),
        url: response.url
      });
      return response;
    })
    .catch(error => {
      console.error('❌ Fetch Error:', { url, error: error.message, stack: error.stack });
      throw error;
    });
};
