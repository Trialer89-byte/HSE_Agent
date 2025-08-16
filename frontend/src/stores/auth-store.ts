import { create } from 'zustand';
import { apiCall } from '@/config/api';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  tenant_id: number;
  permissions: string[];
}

interface LoginData {
  username: string;
  password: string;
  tenant_domain: string;
}

interface AuthStore {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (data: LoginData) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  
  login: async (data: LoginData) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await apiCall('/api/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          username: data.username,
          password: data.password,
          tenant_domain: data.tenant_domain,
        }),
      });
      
      if (response.access_token) {
        // Store auth data
        localStorage.setItem('auth_token', response.access_token);
        localStorage.setItem('user', JSON.stringify(response.user));
        
        set({
          user: response.user,
          token: response.access_token,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Login failed',
      });
      throw error;
    }
  },
  
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
    }
    set({ user: null, token: null, isAuthenticated: false, error: null });
  },
  
  clearError: () => set({ error: null }),
}));