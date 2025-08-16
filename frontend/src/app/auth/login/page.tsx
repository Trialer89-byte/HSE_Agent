'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiCall } from '@/config/api';
import Link from 'next/link';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [tenantDomain, setTenantDomain] = useState('');
  const router = useRouter();

  useEffect(() => {
    const domain = localStorage.getItem('tenant_domain');
    if (!domain) {
      router.push('/tenant-select');
      return;
    }
    setTenantDomain(domain);
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) return;

    setIsLoading(true);
    setError('');

    try {
      console.log('Attempting login with:', { username: username.trim(), tenant_domain: tenantDomain });
      const response = await apiCall('/api/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          username: username.trim(),
          password: password.trim(),
          tenant_domain: tenantDomain
        }),
      });
      console.log('Login response:', response);
      
      if (response.access_token) {
        localStorage.setItem('auth_token', response.access_token);
        localStorage.setItem('user', JSON.stringify(response.user));
        router.push('/dashboard');
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickLogin = (user: string, pass: string) => {
    setUsername(user);
    setPassword(pass);
  };

  if (!tenantDomain) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-orange-500/30 border-t-orange-500 rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-slate-400">Loading security protocols...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden">
      {/* Industrial Background */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M0 0h20v20H0zM40 0h20v20H40zM20 20h20v20H20zM0 40h20v20H0zM40 40h20v20H40z'/%3E%3C/g%3E%3C/svg%3E")`,
        }} />
      </div>

      {/* Header */}
      <div className="relative z-10">
        <div className="flex items-center justify-between p-6">
          <Link href="/tenant-select" className="flex items-center space-x-3 text-slate-300 hover:text-white transition-colors">
            <span className="text-xl">←</span>
            <span className="text-sm uppercase tracking-wide">Switch Organization</span>
          </Link>
          
          <div className="flex items-center space-x-4">
            <div className="px-3 py-1 bg-slate-800/50 rounded-full border border-slate-700/50">
              <span className="text-orange-400 text-xs font-mono">{tenantDomain}</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-green-400 text-xs font-semibold uppercase tracking-wide">Secure</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex items-center justify-center px-8 py-16">
        <div className="max-w-md w-full">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="mb-6">
              <div className="w-20 h-20 bg-gradient-to-br from-orange-500 to-red-600 rounded-2xl flex items-center justify-center mx-auto shadow-2xl mb-6 relative">
                <span className="text-white font-black text-2xl">🔐</span>
                <div className="absolute -top-1 -right-1 w-5 h-5 bg-green-400 rounded-full flex items-center justify-center">
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                </div>
              </div>
              <h1 className="text-4xl font-black text-white tracking-tight">
                SECURITY
                <span className="block text-2xl font-light text-slate-300">Authentication Portal</span>
              </h1>
            </div>
            
            <div className="px-4 py-2 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-xl inline-block">
              <p className="text-slate-400 text-sm uppercase tracking-wide">
                Accessing: <span className="text-orange-400 font-mono">{tenantDomain}</span>
              </p>
            </div>
          </div>

          {/* Login Form */}
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="username" className="block text-sm font-bold text-slate-200 uppercase tracking-wide mb-3">
                  User Identification
                </label>
                <div className="relative">
                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-4 py-4 bg-slate-900/50 border border-slate-600/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent font-mono"
                    placeholder="Enter username..."
                  />
                  <div className="absolute right-4 top-4">
                    <div className="w-2 h-2 bg-slate-600 rounded-full"></div>
                  </div>
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-bold text-slate-200 uppercase tracking-wide mb-3">
                  Security Key
                </label>
                <div className="relative">
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-4 bg-slate-900/50 border border-slate-600/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent font-mono"
                    placeholder="Enter password..."
                  />
                  <div className="absolute right-4 top-4">
                    <div className="w-2 h-2 bg-slate-600 rounded-full"></div>
                  </div>
                </div>
              </div>

              {error && (
                <div className="p-4 rounded-xl border bg-red-500/10 border-red-500/30 text-red-400 font-mono text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                    <span>❌ {error}</span>
                  </div>
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-4 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 disabled:from-slate-600 disabled:to-slate-700 text-white font-bold rounded-xl transition-all duration-200 transform hover:scale-[1.02] disabled:scale-100 shadow-lg disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    <span>AUTHENTICATING...</span>
                  </div>
                ) : (
                  <span>🚀 AUTHENTICATE & ACCESS</span>
                )}
              </button>
            </form>
          </div>

          {/* Quick Access Panel */}
          <div className="mt-8 p-6 bg-slate-900/30 backdrop-blur-sm border border-slate-700/30 rounded-xl">
            <h3 className="text-slate-200 font-bold uppercase tracking-wide text-xs mb-4">Quick Access</h3>
            <div className="space-y-3">
              <button
                onClick={() => handleQuickLogin('admin', 'Admin123!')}
                className="w-full p-3 text-left bg-slate-800/50 hover:bg-slate-700/50 rounded-lg border border-slate-700/30 hover:border-orange-500/50 transition-all duration-200 group"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-orange-400 font-semibold text-sm">Administrator</div>
                    <div className="text-slate-500 text-xs font-mono">admin / Admin123!</div>
                  </div>
                  <div className="text-orange-500 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-xs">→</span>
                  </div>
                </div>
              </button>
              
              <button
                onClick={() => handleQuickLogin('user', 'User123!')}
                className="w-full p-3 text-left bg-slate-800/50 hover:bg-slate-700/50 rounded-lg border border-slate-700/30 hover:border-blue-500/50 transition-all duration-200 group"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-blue-400 font-semibold text-sm">Standard User</div>
                    <div className="text-slate-500 text-xs font-mono">user / User123!</div>
                  </div>
                  <div className="text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-xs">→</span>
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Security Notice */}
          <div className="mt-6 text-center">
            <p className="text-xs text-slate-500 uppercase tracking-wide">
              Secure connection established • 256-bit encryption • ISO 27001 compliant
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}