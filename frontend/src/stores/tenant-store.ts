import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { TenantInfo } from '@/types/tenant';
import { TenantDetection } from '@/lib/tenant-detection';

interface TenantState {
  // State
  tenant: TenantInfo | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setTenant: (tenant: TenantInfo | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  loadTenantByDomain: (domain: string) => Promise<void>;
  loadTenantBySubdomain: (subdomain: string) => Promise<void>;
  validateTenantAccess: (domain?: string, subdomain?: string) => Promise<boolean>;
  autoDetectTenant: () => Promise<void>;
  clearTenant: () => void;
}

export const useTenantStore = create<TenantState>()(
  persist(
    (set, get) => ({
      // Initial state
      tenant: null,
      isLoading: false,
      error: null,

      // Actions
      setTenant: (tenant) => {
        set({ tenant, error: null });
        if (tenant) {
          TenantDetection.storeTenantInfo(tenant);
        } else {
          TenantDetection.clearTenantInfo();
        }
      },

      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error, isLoading: false }),

      loadTenantByDomain: async (domain) => {
        set({ isLoading: true, error: null });
        try {
          const tenant = await TenantDetection.getTenantByDomain(domain);
          get().setTenant(tenant);
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to load tenant';
          get().setError(errorMessage);
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      loadTenantBySubdomain: async (subdomain) => {
        set({ isLoading: true, error: null });
        try {
          const tenant = await TenantDetection.getTenantBySubdomain(subdomain);
          get().setTenant(tenant);
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to load tenant';
          get().setError(errorMessage);
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      validateTenantAccess: async (domain, subdomain) => {
        set({ isLoading: true, error: null });
        try {
          const validation = await TenantDetection.validateTenantAccess(domain, subdomain);
          set({ isLoading: false });
          return validation.valid;
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to validate tenant';
          get().setError(errorMessage);
          return false;
        }
      },

      autoDetectTenant: async () => {
        set({ isLoading: true, error: null });
        try {
          const tenant = await TenantDetection.autoDetectTenant();
          get().setTenant(tenant);
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to auto-detect tenant';
          get().setError(errorMessage);
        } finally {
          set({ isLoading: false });
        }
      },

      clearTenant: () => {
        set({ tenant: null, error: null });
        TenantDetection.clearTenantInfo();
      },
    }),
    {
      name: 'tenant-storage',
      partialize: (state) => ({ 
        tenant: state.tenant 
      }),
    }
  )
);