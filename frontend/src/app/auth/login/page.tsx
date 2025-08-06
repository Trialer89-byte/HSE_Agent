'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useTenantStore } from '@/stores/tenant-store';
import { useAuthStore } from '@/stores/auth-store';
import { TenantBranding } from '@/components/tenant/tenant-branding';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();
  
  const { tenant } = useTenantStore();
  const { login, isLoading, error, clearError } = useAuthStore();

  useEffect(() => {
    // If no tenant is selected, redirect to tenant selection
    if (!tenant) {
      router.push('/tenant-select');
      return;
    }

    // Clear any existing errors when component mounts
    clearError();
  }, [tenant, router, clearError]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim() || !tenant) return;

    try {
      await login({
        username: username.trim(),
        password: password.trim(),
        tenant_domain: tenant.domain
      });
      
      // Redirect to dashboard on successful login
      router.push('/dashboard');
    } catch (err) {
      // Error is handled by the store
      console.error('Login failed:', err);
    }
  };

  if (!tenant) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <TenantBranding tenant={tenant} />
        
        <div className="text-center mt-6">
          <h2 className="text-3xl font-bold text-gray-900">
            Welcome to {tenant.display_name}
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Sign in to your account
          </p>
        </div>

        <div className="mt-8 bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Username
              </label>
              <div className="mt-1">
                <input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <div className="text-center">
              <button
                type="button"
                onClick={() => router.push('/tenant-select')}
                className="text-sm text-blue-600 hover:text-blue-500"
              >
                Switch organization
              </button>
            </div>
          </div>
        </div>

        {/* Demo credentials for development */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <h3 className="text-sm font-medium text-yellow-800">Demo Credentials</h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p><strong>Admin:</strong> admin_{tenant.display_name} / Admin123!</p>
              <p><strong>User:</strong> user_{tenant.display_name} / User123!</p>
              <p><strong>Viewer:</strong> viewer_{tenant.display_name} / Viewer123!</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}