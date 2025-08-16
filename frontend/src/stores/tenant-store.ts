import { create } from 'zustand';

interface Tenant {
  id: number;
  domain?: string;  // Make optional to match TenantInfo
  display_name: string;
  settings?: any;
}

interface TenantStore {
  tenant: Tenant | null;
  isLoading: boolean;
  error: string | null;
  setTenant: (tenant: Tenant | null) => void;
  clearTenant: () => void;
}

export const useTenantStore = create<TenantStore>((set) => ({
  tenant: null,
  isLoading: false,
  error: null,
  
  setTenant: (tenant) => set({ tenant, error: null }),
  
  clearTenant: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('tenant_domain');
      localStorage.removeItem('tenant_id');
    }
    set({ tenant: null, error: null });
  },
}));