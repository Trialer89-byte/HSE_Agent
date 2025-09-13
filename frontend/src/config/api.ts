import axios from 'axios';

// Base API configuration - point directly to backend
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
  // Use longer timeout for document-related and AI analysis endpoints
  const timeout = endpoint.includes('/documents') || endpoint.includes('/permits') || endpoint.includes('/work-permits') 
    ? 120000 : 10000; // 2 minutes for documents and permits (AI analysis), 10 seconds for others
  return apiCallWithTimeout(endpoint, options, timeout);
}

// Helper function for API calls with custom timeout
export async function apiCallWithTimeout(endpoint: string, options?: RequestInit, timeoutMs: number = 10000) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Don't set Content-Type for FormData (let browser set it with boundary)
  const isFormData = options?.body instanceof FormData;
  
  const headers: Record<string, string> = {
    ...(!isFormData && { 'Content-Type': 'application/json' }),
    // Prevent caching of API responses to ensure fresh data
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
    ...(options?.headers as Record<string, string> || {}),
  };
  
  // Add auth headers if available (but NOT for login/auth endpoints)
  if (typeof window !== 'undefined' && !endpoint.includes('/auth/')) {
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
      signal: AbortSignal.timeout(timeoutMs), // Custom timeout
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => response.statusText);
      throw new Error(`API call failed: ${errorText}`);
    }
    
    return response.json();
  } catch (error) {
    // Log the actual error for debugging
    console.error('API call error:', error);
    console.error('URL attempted:', url);
    console.error('Error type:', typeof error);
    console.error('Error message:', error instanceof Error ? error.message : String(error));
    
    // Check if it's a network error or timeout
    if (error instanceof TypeError && (error.message.includes('fetch') || error.message.includes('Failed to fetch'))) {
      throw new Error(`Cannot connect to backend. Please ensure the backend is running on http://127.0.0.1:8000. Original error: ${error.message}`);
    }
    
    // Check if it's a timeout error
    if (error instanceof DOMException && error.name === 'TimeoutError') {
      const timeoutSeconds = Math.round(timeoutMs / 1000);
      throw new Error(`Operation timed out after ${timeoutSeconds} seconds. AI analysis may take longer than expected. Please try again.`);
    }
    
    // Check for AbortError (can also indicate timeout)
    if (error instanceof DOMException && error.name === 'AbortError') {
      const timeoutSeconds = Math.round(timeoutMs / 1000);
      throw new Error(`Request was aborted after ${timeoutSeconds} seconds. AI analysis may take longer than expected. Please try again.`);
    }
    throw error;
  }
}

export default apiClient;