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
    // In production (Upsun/Platform.sh), use the api subdomain as configured in .upsun/config.yaml
    const hostname = typeof window !== 'undefined' ? window.location.hostname : '';
    
    // Handle different cloud environments
    if (hostname.includes('platformsh.site') || hostname.includes('upsun.app')) {
      // Use same domain for Platform.sh/Upsun deployments
      return `https://${hostname}`;
    }
    
    return `https://api.${hostname}`;
  }
  
  // In development, try to use the direct backend URL if proxy is not working
  // Check if we're running on localhost:5173 (Vite dev server)
  if (typeof window !== 'undefined' && window.location.port === '5173') {
    // Use direct backend URL to bypass potential proxy issues
    return 'http://localhost:8000';
  }
  
  // Default: use relative URLs which will be handled by the Vite proxy
  return '';
};

/**
 * Creates a complete API URL by combining the base URL with the endpoint
 */
export const createApiUrl = (endpoint: string): string => {
  const baseUrl = getApiBaseUrl();
  // Ensure endpoint starts with /api/
  const formattedEndpoint = endpoint.startsWith('/api/') ? endpoint : `/api/${endpoint.replace(/^\//, '')}`;
  return `${baseUrl}${formattedEndpoint}`;
};

/**
 * Wrapper for the fetch API that automatically adds the API base URL and auth token
 * Now with enhanced error handling and cloud environment compatibility
 */
export const apiFetch = (endpoint: string, options?: RequestInit): Promise<Response> => {
  const url = createApiUrl(endpoint);
  
  // Get auth token from localStorage if available
  const token = localStorage.getItem('authToken');
  
  // Get CSRF token from cookie if it exists
  const csrfToken = document.cookie
    .split(';')
    .map(cookie => cookie.trim())
    .find(cookie => cookie.startsWith('csrftoken='))
    ?.split('=')[1];
  
  // Prepare headers with Authorization if token exists and CSRF token if it exists
  const headers = {
    ...(options?.headers || {}),
    ...(token ? { 'Authorization': `Token ${token}` } : {}),
    ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
    // Add headers for cross-origin compatibility
    'Accept': 'application/json',
    // Only add Content-Type if it's not FormData (for file uploads)
    ...(!options?.body || !(options.body instanceof FormData) ? { 'Content-Type': 'application/json' } : {})
  };
  
  const fetchOptions = {
    ...options,
    headers,
    // Enable credentials for cross-origin requests
    credentials: 'include' as RequestCredentials,
    // Set mode to handle CORS more permissively  
    mode: 'cors' as RequestMode
  };
  
  // Enhanced error handling with retry logic for cloud environments
  return fetch(url, fetchOptions).catch(error => {
    console.error('API fetch error:', error);
    // If it's a network error, try without credentials as fallback
    if (error.name === 'TypeError' || error.message.includes('NetworkError')) {
      console.log('Retrying without credentials...');
      return fetch(url, {
        ...fetchOptions,
        credentials: 'omit'
      });
    }
    throw error;
  });
}; 