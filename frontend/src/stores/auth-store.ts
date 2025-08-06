import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AuthStore, LoginRequest, RegisterRequest } from '@/types/auth';
import apiClient from '@/config/api';

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (credentials: LoginRequest) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await apiClient.post('/api/v1/auth/login', credentials);
          const { access_token, user, tenant } = response.data;
          
          // Store token and user info
          localStorage.setItem('auth_token', access_token);
          localStorage.setItem('user', JSON.stringify(user));
          localStorage.setItem('tenant_id', tenant.id.toString());
          localStorage.setItem('tenant_domain', tenant.domain || '');
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
        } catch (error: unknown) {
          const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Login failed';
          set({
            error: errorMessage,
            isLoading: false,
            isAuthenticated: false
          });
          throw error;
        }
      },

      register: async (data: RegisterRequest) => {
        set({ isLoading: true, error: null });
        
        try {
          await apiClient.post('/api/v1/auth/register', data);
          set({ isLoading: false });
        } catch (error: unknown) {
          const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Registration failed';
          set({
            error: errorMessage,
            isLoading: false
          });
          throw error;
        }
      },

      logout: () => {
        // Clear all stored data
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        localStorage.removeItem('tenant_id');
        localStorage.removeItem('tenant_domain');
        
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null
        });
      },

      refreshToken: async () => {
        set({ isLoading: true });
        
        try {
          const response = await apiClient.post('/api/v1/auth/refresh');
          const { access_token, user } = response.data;
          
          localStorage.setItem('auth_token', access_token);
          localStorage.setItem('user', JSON.stringify(user));
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false
          });
        } catch {
          // If refresh fails, logout user
          get().logout();
          set({ isLoading: false });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      }),
    }
  )
);