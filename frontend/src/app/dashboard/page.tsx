'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [tenantDomain, setTenantDomain] = useState('');
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const userData = localStorage.getItem('user');
    const domain = localStorage.getItem('tenant_domain');
    
    if (!token || !userData) {
      router.push('/auth/login');
      return;
    }
    
    try {
      setUser(JSON.parse(userData));
      setTenantDomain(domain || 'Unknown Organization');
    } catch (error) {
      console.error('Error parsing user data:', error);
      router.push('/auth/login');
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    localStorage.removeItem('tenant_domain');
    localStorage.removeItem('tenant_id');
    router.push('/');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-orange-500/30 border-t-orange-500 rounded-full animate-spin mx-auto"></div>
          <p className="mt-6 text-slate-400 font-medium">Initializing Workspace...</p>
        </div>
      </div>
    );
  }

  const modules = [
    {
      id: 'work-permits',
      title: 'WORK PERMITS',
      description: 'Risk Assessment & Authorization',
      icon: '🏗️',
      href: '/work-permits',
      color: 'from-orange-500 to-red-600',
      status: 'Active',
      count: '12 Pending'
    },
    {
      id: 'documents',
      title: 'DOCUMENTATION',
      description: 'HSE Procedures & Standards',
      icon: '📋',
      href: '/documents',
      color: 'from-blue-500 to-blue-600',
      status: 'Online',
      count: '247 Files'
    },
    {
      id: 'analytics',
      title: 'ANALYTICS',
      description: 'Safety Metrics & Reports',
      icon: '📊',
      href: '/reports',
      color: 'from-green-500 to-green-600',
      status: 'Updated',
      count: 'Real-time'
    },
    {
      id: 'incidents',
      title: 'INCIDENTS',
      description: 'Safety Event Management',
      icon: '⚠️',
      href: '/incidents',
      color: 'from-yellow-500 to-orange-500',
      status: 'Monitor',
      count: '2 Open'
    },
    {
      id: 'training',
      title: 'TRAINING',
      description: 'Safety Certification Portal',
      icon: '🎓',
      href: '/training',
      color: 'from-purple-500 to-purple-600',
      status: 'Available',
      count: '8 Courses'
    },
    {
      id: 'audit',
      title: 'AUDIT TRAIL',
      description: 'Compliance & Tracking',
      icon: '🔍',
      href: '/audit',
      color: 'from-slate-500 to-slate-600',
      status: 'Logging',
      count: 'All Events'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Industrial Background */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M0 0h20v20H0zM60 0h20v20H60zM20 20h20v20H20zM0 60h20v20H0zM60 60h20v20H60z'/%3E%3C/g%3E%3C/svg%3E")`,
        }} />
      </div>

      {/* Header */}
      <header className="relative z-10 bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-black text-xl">HSE</span>
              </div>
              <div>
                <h1 className="text-2xl font-black text-white tracking-tight">
                  CONTROL CENTER
                </h1>
                <p className="text-slate-400 text-sm font-mono">{tenantDomain}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-slate-700 rounded-lg flex items-center justify-center">
                  <span className="text-slate-300 text-sm">👤</span>
                </div>
                <div className="text-right">
                  <div className="text-white font-semibold text-sm">
                    {user?.full_name || user?.username}
                  </div>
                  <div className="text-slate-400 text-xs uppercase tracking-wide">
                    {user?.role || 'User'}
                  </div>
                </div>
              </div>
              
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-slate-700/50 hover:bg-slate-600/50 border border-slate-600/50 hover:border-slate-500 text-slate-300 hover:text-white rounded-lg transition-all duration-200 text-sm font-medium"
              >
                LOGOUT
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {/* System Status */}
        <div className="mb-8 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-black text-green-400">ONLINE</div>
                <div className="text-xs text-slate-400 uppercase tracking-wide">System Status</div>
              </div>
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            </div>
          </div>
          
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-black text-blue-400">24/7</div>
                <div className="text-xs text-slate-400 uppercase tracking-wide">Monitoring</div>
              </div>
              <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse"></div>
            </div>
          </div>
          
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-black text-orange-400">AI</div>
                <div className="text-xs text-slate-400 uppercase tracking-wide">Powered</div>
              </div>
              <div className="w-3 h-3 bg-orange-400 rounded-full animate-pulse"></div>
            </div>
          </div>
          
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-black text-purple-400">SECURE</div>
                <div className="text-xs text-slate-400 uppercase tracking-wide">Connection</div>
              </div>
              <div className="w-3 h-3 bg-purple-400 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>

        {/* Modules Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((module) => (
            <Link
              key={module.id}
              href={module.href}
              className="group block bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 hover:bg-slate-700/40 hover:border-slate-600/50 transition-all duration-300 transform hover:scale-[1.02]"
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`w-14 h-14 bg-gradient-to-br ${module.color} rounded-xl flex items-center justify-center text-2xl`}>
                  {module.icon}
                </div>
                <div className="text-right">
                  <div className="text-xs text-slate-400 uppercase tracking-wide">
                    {module.status}
                  </div>
                  <div className="text-sm font-mono text-slate-300">
                    {module.count}
                  </div>
                </div>
              </div>
              
              <h3 className="text-xl font-black text-white tracking-tight mb-2 group-hover:text-orange-400 transition-colors">
                {module.title}
              </h3>
              <p className="text-slate-400 text-sm mb-4">
                {module.description}
              </p>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-xs text-slate-500 uppercase tracking-wide">Ready</span>
                </div>
                <span className="text-slate-500 group-hover:text-orange-400 transition-colors">→</span>
              </div>
            </Link>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="mt-12">
          <h2 className="text-lg font-bold text-slate-200 uppercase tracking-wide mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button className="p-4 bg-orange-500/10 hover:bg-orange-500/20 border border-orange-500/30 hover:border-orange-400 rounded-xl transition-all duration-200 group">
              <div className="text-orange-400 text-2xl mb-2">⚡</div>
              <div className="text-orange-400 font-semibold text-sm group-hover:text-orange-300">Emergency Protocol</div>
            </button>
            
            <button className="p-4 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 hover:border-blue-400 rounded-xl transition-all duration-200 group">
              <div className="text-blue-400 text-2xl mb-2">🔔</div>
              <div className="text-blue-400 font-semibold text-sm group-hover:text-blue-300">Alert System</div>
            </button>
            
            <button className="p-4 bg-green-500/10 hover:bg-green-500/20 border border-green-500/30 hover:border-green-400 rounded-xl transition-all duration-200 group">
              <div className="text-green-400 text-2xl mb-2">📞</div>
              <div className="text-green-400 font-semibold text-sm group-hover:text-green-300">Support Center</div>
            </button>
            
            <button className="p-4 bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 hover:border-purple-400 rounded-xl transition-all duration-200 group">
              <div className="text-purple-400 text-2xl mb-2">⚙️</div>
              <div className="text-purple-400 font-semibold text-sm group-hover:text-purple-300">System Config</div>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}