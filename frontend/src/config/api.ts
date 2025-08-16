import axios from 'axios';

// Base API configuration - use nginx proxy for all requests
export const API_BASE_URL = 'http://localhost';

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable credentials to match backend CORS
});

// Request interceptor to add auth token and tenant info
apiClient.interceptors.request.use(
  (config) => {
    // Only access localStorage on client side
    if (typeof window !== 'undefined') {
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
    // Only access localStorage/window on client side
    if (typeof window !== 'undefined') {
      if (error.response?.status === 401) {
        // Unauthorized - clear auth and redirect to login
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        localStorage.removeItem('tenant_domain');
        localStorage.removeItem('tenant_id');
        window.location.href = '/auth/login';
      } else if (error.response?.status === 403) {
        // Forbidden - might be tenant access issue
        console.error('Access forbidden:', error.response.data);
      }
    }
    
    return Promise.reject(error);
  }
);

// Helper function for API calls without axios
export async function apiCall(endpoint: string, options?: RequestInit) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Don't set Content-Type for FormData (let browser set it with boundary)
  const isFormData = options?.body instanceof FormData;
  
  const headers: Record<string, string> = {
    ...(!isFormData && { 'Content-Type': 'application/json' }),
    ...(options?.headers as Record<string, string> || {}),
  };
  
  // Add auth headers if available
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const tenantDomain = localStorage.getItem('tenant_domain');
    if (tenantDomain) {
      headers['X-Tenant-Domain'] = tenantDomain;
    }
    
    const tenantId = localStorage.getItem('tenant_id');
    if (tenantId) {
      headers['X-Tenant-ID'] = tenantId;
    }
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => response.statusText);
      throw new Error(`API call failed: ${errorText}`);
    }
    
    return response.json();
  } catch (error) {
    // Check if it's a network error
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Cannot connect to backend. Please ensure the backend is running on http://localhost:8000');
    }
    throw error;
  }
}

export default apiClient;