'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiCall } from '@/config/api';
import Link from 'next/link';

export default function TenantSelectPage() {
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
      const data = await apiCall(`/api/v1/public/tenants/validate?domain=${encodeURIComponent(domain)}`);
      
      if (data.valid) {
        localStorage.setItem('tenant_domain', domain);
        localStorage.setItem('tenant_id', data.tenant_id?.toString() || '');
        
        setMessage(`✅ CONNECTION ESTABLISHED: ${data.display_name}`);
        
        setTimeout(() => {
          router.push('/auth/login');
        }, 1200);
      } else {
        setMessage('❌ ORGANIZATION NOT FOUND OR INACTIVE');
      }
    } catch (error) {
      console.error('API Error:', error);
      setMessage(`❌ CONNECTION FAILED: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemo = async () => {
    setIsLoading(true);
    setMessage('');
    
    try {
      const demoDomain = 'test.hse-enterprise.local';
      const data = await apiCall(`/api/v1/public/tenants/validate?domain=${encodeURIComponent(demoDomain)}`);
      
      if (data.valid) {
        localStorage.setItem('tenant_domain', demoDomain);
        localStorage.setItem('tenant_id', data.tenant_id?.toString() || '');
        
        setMessage(`🚀 DEMO ENVIRONMENT LOADED: ${data.display_name}`);
        
        setTimeout(() => {
          router.push('/auth/login');
        }, 1200);
      } else {
        setMessage('❌ DEMO ENVIRONMENT UNAVAILABLE');
      }
    } catch (error) {
      console.error('Demo Error:', error);
      setMessage(`❌ DEMO LOAD FAILED: ${error instanceof Error ? error.message : 'Connection error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden">
      {/* Industrial Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M20 20v-4h-4v4h4zm4 0v-4h-4v4h4zm4 0v-4h-4v4h4z'/%3E%3C/g%3E%3C/svg%3E")`,
        }} />
      </div>

      {/* Header */}
      <div className="relative z-10">
        <div className="flex items-center justify-between p-6">
          <Link href="/" className="flex items-center space-x-3 text-slate-300 hover:text-white transition-colors">
            <span className="text-xl">←</span>
            <span className="text-sm uppercase tracking-wide">Back to Launch</span>
          </Link>
          
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-green-400 text-xs font-semibold uppercase tracking-wide">System Online</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex items-center justify-center px-8 py-16">
        <div className="max-w-lg w-full">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center mx-auto shadow-2xl mb-4">
                <span className="text-white font-black text-2xl">🏭</span>
              </div>
              <h1 className="text-4xl font-black text-white tracking-tight">
                ORGANIZATION
                <span className="block text-2xl font-light text-slate-300">Selection Protocol</span>
              </h1>
            </div>
            
            <p className="text-slate-400 text-sm uppercase tracking-wide">
              Secure multi-tenant access control system
            </p>
          </div>

          {/* Main Form Card */}
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="domain" className="block text-sm font-bold text-slate-200 uppercase tracking-wide mb-3">
                  Organization Domain
                </label>
                <div className="relative">
                  <input
                    id="domain"
                    name="domain"
                    type="text"
                    required
                    value={domain}
                    onChange={(e) => setDomain(e.target.value)}
                    placeholder="test.hse-enterprise.local"
                    className="w-full px-4 py-4 bg-slate-900/50 border border-slate-600/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent font-mono text-sm"
                  />
                  <div className="absolute right-4 top-4">
                    <div className="w-2 h-2 bg-slate-600 rounded-full"></div>
                  </div>
                </div>
              </div>

              {/* Status Message */}
              {message && (
                <div className={`p-4 rounded-xl border font-mono text-sm ${
                  message.includes('✅') || message.includes('🚀') 
                    ? 'bg-green-500/10 border-green-500/30 text-green-400' 
                    : 'bg-red-500/10 border-red-500/30 text-red-400'
                }`}>
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${
                      message.includes('✅') || message.includes('🚀') ? 'bg-green-400' : 'bg-red-400'
                    }`}></div>
                    <span>{message}</span>
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-4 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 disabled:from-slate-600 disabled:to-slate-700 text-white font-bold rounded-xl transition-all duration-200 transform hover:scale-[1.02] disabled:scale-100 shadow-lg disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    <span>CONNECTING...</span>
                  </div>
                ) : (
                  <span>🔗 CONNECT TO ORGANIZATION</span>
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="relative my-8">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-700/50" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-slate-800/40 text-slate-400 uppercase tracking-wide font-semibold">Or</span>
              </div>
            </div>

            {/* Demo Button */}
            <button
              type="button"
              onClick={handleDemo}
              disabled={isLoading}
              className="w-full py-4 bg-slate-900/50 hover:bg-slate-700/50 disabled:bg-slate-800/30 border border-slate-600/50 hover:border-slate-500 text-slate-300 hover:text-white font-bold rounded-xl transition-all duration-200 transform hover:scale-[1.02] disabled:scale-100 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-4 h-4 border-2 border-slate-400/30 border-t-slate-400 rounded-full animate-spin"></div>
                  <span>LOADING DEMO...</span>
                </div>
              ) : (
                <span>🧪 LOAD DEMO ENVIRONMENT</span>
              )}
            </button>
          </div>

          {/* Info Panel */}
          <div className="mt-8 p-6 bg-slate-900/30 backdrop-blur-sm border border-slate-700/30 rounded-xl">
            <h3 className="text-slate-200 font-bold uppercase tracking-wide text-xs mb-3">Demo Environment</h3>
            <div className="grid grid-cols-1 gap-3 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-500">Organization:</span>
                <span className="text-orange-400 font-mono">test.hse-enterprise.local</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Username:</span>
                <span className="text-orange-400 font-mono">admin</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Password:</span>
                <span className="text-orange-400 font-mono">HSEAdmin2024!</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}