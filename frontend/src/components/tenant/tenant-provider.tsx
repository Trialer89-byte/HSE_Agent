'use client';

import { ReactNode, useEffect } from 'react';
import { useTenantStore } from '@/stores/tenant-store';
import { TenantDetection } from '@/lib/tenant-detection';

interface TenantProviderProps {
  children: ReactNode;
}

export function TenantProvider({ children }: TenantProviderProps) {
  const { tenant, isLoading } = useTenantStore();

  // Initialize tenant info from localStorage on client-side
  useEffect(() => {
    if (typeof window !== 'undefined' && !tenant) {
      const storedTenant = TenantDetection.getStoredTenantInfo();
      if (storedTenant) {
        useTenantStore.getState().setTenant(storedTenant);
      }
    }
  }, [tenant]);

  return <>{children}</>;
}