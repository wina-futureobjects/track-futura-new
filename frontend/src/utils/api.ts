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
    // In production, use the API subdomain
    const hostname = typeof window !== 'undefined' ? window.location.hostname : '';
    return 'https://api.' + hostname.replace(/^www\./, '');
  }
  
  // In development, use relative URLs which will be handled by the Vite proxy
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
    ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {})
  };
  
  return fetch(url, {
    ...options,
    headers
  });
}; 