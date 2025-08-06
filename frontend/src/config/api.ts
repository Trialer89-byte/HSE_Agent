import axios from 'axios';

// Base API configuration
// Use different URLs for server-side (inside Docker) vs client-side (browser)
export const API_BASE_URL = typeof window === 'undefined' 
  ? (process.env.INTERNAL_API_URL || 'http://hse-agent-backend:8000')  // Server-side
  : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');      // Client-side

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token and tenant info
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add tenant information
    const tenantDomain = localStorage.getItem('tenant_domain');
    const tenantId = localStorage.getItem('tenant_id');
    
    if (tenantDomain) {
      config.headers['X-Tenant-Domain'] = tenantDomain;
    }
    
    if (tenantId) {
      config.headers['X-Tenant-ID'] = tenantId;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear auth and redirect to login
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/auth/login';
    } else if (error.response?.status === 403) {
      // Forbidden - might be tenant access issue
      console.error('Access forbidden:', error.response.data);
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;