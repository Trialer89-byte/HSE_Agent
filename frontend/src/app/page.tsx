'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useTenantStore } from '@/stores/tenant-store';
import { useAuthStore } from '@/stores/auth-store';

export default function Home() {
  const router = useRouter();
  const { tenant } = useTenantStore();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    // If user is authenticated, redirect to dashboard
    if (isAuthenticated) {
      router.push('/dashboard');
      return;
    }

    // If tenant is selected, redirect to login
    if (tenant) {
      router.push('/auth/login');
      return;
    }

    // Otherwise, redirect to tenant selection
    router.push('/tenant-select');
  }, [tenant, isAuthenticated, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading HSE Management System...</p>
      </div>
    </div>
  );
}
