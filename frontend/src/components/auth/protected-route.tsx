'use client';

import { useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import { useTenantStore } from '@/stores/tenant-store';

interface ProtectedRouteProps {
  children: ReactNode;
  requiredPermissions?: string[];
  requiredRole?: string;
}

export function ProtectedRoute({ 
  children, 
  requiredPermissions = [], 
  requiredRole 
}: ProtectedRouteProps) {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useAuthStore();
  const { tenant } = useTenantStore();

  useEffect(() => {
    // If no tenant selected, redirect to tenant selection
    if (!tenant) {
      router.push('/tenant-select');
      return;
    }

    // If not authenticated and not loading, redirect to login
    if (!isAuthenticated && !isLoading) {
      router.push('/auth/login');
      return;
    }

    // Check role requirements
    if (requiredRole && user && user.role !== requiredRole) {
      router.push('/unauthorized');
      return;
    }

    // Check permission requirements
    if (requiredPermissions.length > 0 && user) {
      const hasRequiredPermissions = requiredPermissions.every(permission =>
        user.permissions.includes(permission)
      );

      if (!hasRequiredPermissions) {
        router.push('/unauthorized');
        return;
      }
    }
  }, [tenant, isAuthenticated, isLoading, user, router, requiredPermissions, requiredRole]);

  // Show loading spinner while checking authentication
  if (isLoading || !tenant || !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}