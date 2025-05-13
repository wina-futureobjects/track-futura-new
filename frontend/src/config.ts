// Configuration for the application
const isDevelopment = import.meta.env.DEV;

// For production, prioritize any explicit backend URL from environment if available,
// otherwise construct it from the current domain
const explicitBackendUrl = import.meta.env.VITE_API_URL;
const defaultProductionApiUrl = 'https://api.' + window.location.host;
const productionApiUrl = explicitBackendUrl || defaultProductionApiUrl;

// Use relative URL for development (which gets proxied by Vite)
// and the configured API URL for production
export const API_BASE_URL = isDevelopment ? '' : productionApiUrl;

export default {
  API_BASE_URL
}; 