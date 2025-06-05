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
    // In production, use the same domain
    const hostname = typeof window !== 'undefined' ? window.location.hostname : '';

    // Use same domain for all environments
    return `https://${hostname}`;
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

  // Skip CSRF tokens completely for testing

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

  // Error handling
  return fetch(url, fetchOptions).catch(error => {
    throw error;
  });
};
