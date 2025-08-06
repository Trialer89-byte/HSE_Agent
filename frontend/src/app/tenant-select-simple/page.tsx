'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function TenantSelectSimplePage() {
  const [domain, setDomain] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!domain.trim()) return;

    setIsLoading(true);
    setMessage('');

    try {
      // Direct API call without store
      const response = await fetch(`/api/v1/public/tenants/validate?domain=${encodeURIComponent(domain)}`);
      const data = await response.json();
      
      if (data.valid) {
        // Store tenant info in localStorage directly
        localStorage.setItem('tenant_domain', domain);
        localStorage.setItem('tenant_id', data.tenant_id?.toString() || '');
        
        setMessage(`Success! Found tenant: ${data.display_name}`);
        
        // Redirect after a brief delay
        setTimeout(() => {
          router.push('/auth/login');
        }, 1000);
      } else {
        setMessage('Tenant not found or inactive');
      }
    } catch (error) {
      console.error('API Error:', error);
      setMessage(`Error: ${error instanceof Error ? error.message : 'Failed to validate tenant'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemo = async () => {
    setIsLoading(true);
    setMessage('');
    
    try {
      const demoDomain = 'demo.hse-system.com';
      const response = await fetch(`/api/v1/public/tenants/validate?domain=${encodeURIComponent(demoDomain)}`);
      const data = await response.json();
      
      if (data.valid) {
        localStorage.setItem('tenant_domain', demoDomain);
        localStorage.setItem('tenant_id', data.tenant_id?.toString() || '');
        
        setMessage(`Demo loaded! Tenant: ${data.display_name}`);
        
        setTimeout(() => {
          router.push('/auth/login');
        }, 1000);
      } else {
        setMessage('Demo tenant not available');
      }
    } catch (error) {
      console.error('Demo Error:', error);
      setMessage(`Error: ${error instanceof Error ? error.message : 'Failed to load demo'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">HSE Management System</h1>
          <p className="mt-2 text-sm text-gray-600">Simple Tenant Selection</p>
        </div>

        <div className="mt-8 bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="domain" className="block text-sm font-medium text-gray-700">
                Organization Domain
              </label>
              <div className="mt-1">
                <input
                  id="domain"
                  name="domain"
                  type="text"
                  required
                  value={domain}
                  onChange={(e) => setDomain(e.target.value)}
                  placeholder="e.g., demo.hse-system.com"
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>

            {message && (
              <div className={`p-4 rounded ${message.includes('Success') || message.includes('Demo loaded') 
                ? 'bg-green-50 border border-green-200 text-green-700' 
                : 'bg-red-50 border border-red-200 text-red-700'}`}>
                {message}
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Connecting...' : 'Continue'}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Or</span>
              </div>
            </div>

            <div className="mt-6">
              <button
                type="button"
                onClick={handleDemo}
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                Try Demo
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}