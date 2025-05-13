import { API_BASE_URL } from '../config';

/**
 * Utility function to make API requests with the correct base URL
 */
export const apiRequest = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Debug log in production to help troubleshoot API URL issues
  if (!import.meta.env.DEV) {
    console.log(`API Request to: ${url}`);
  }
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  const response = await fetch(url, config);
  return response;
};

export default {
  async get(endpoint: string, options = {}) {
    return apiRequest(endpoint, { ...options, method: 'GET' });
  },

  async post(endpoint: string, data: any, options = {}) {
    return apiRequest(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async put(endpoint: string, data: any, options = {}) {
    return apiRequest(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async patch(endpoint: string, data: any, options = {}) {
    return apiRequest(endpoint, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  async delete(endpoint: string, options = {}) {
    return apiRequest(endpoint, { ...options, method: 'DELETE' });
  },
}; 