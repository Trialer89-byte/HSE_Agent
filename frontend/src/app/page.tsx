'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden">
      {/* Industrial Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M30 30c0-11.046-8.954-20-20-20s-20 8.954-20 20 8.954 20 20 20 20-8.954 20-20zm-20-16a16 16 0 1 1 0 32 16 16 0 0 1 0-32z' /%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }} />
      </div>

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex">
        {/* Left Side - Hero Section */}
        <div className="flex-1 flex items-center justify-center px-8 lg:px-16">
          <div className="max-w-2xl">
            {/* Industrial Logo */}
            <div className="mb-8">
              <div className="inline-flex items-center space-x-4">
                <div className="relative">
                  <div className="w-20 h-20 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg flex items-center justify-center shadow-2xl">
                    <div className="text-white font-black text-3xl tracking-tight">HSE</div>
                    <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-pulse"></div>
                  </div>
                </div>
                <div>
                  <h1 className="text-5xl font-black text-white tracking-tight leading-none">
                    INDUSTRIAL
                    <span className="block text-orange-400 text-4xl font-light">Safety Platform</span>
                  </h1>
                </div>
              </div>
            </div>

            {/* Tagline */}
            <div className="mb-12">
              <p className="text-xl text-slate-300 leading-relaxed font-light">
                Advanced AI-powered workplace safety management for 
                <span className="text-orange-400 font-semibold"> industrial environments</span>
              </p>
              
              {/* Features */}
              <div className="grid grid-cols-2 gap-6 mt-8">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-slate-400 text-sm uppercase tracking-wide">Risk Assessment</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                  <span className="text-slate-400 text-sm uppercase tracking-wide">AI Analysis</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                  <span className="text-slate-400 text-sm uppercase tracking-wide">Compliance</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                  <span className="text-slate-400 text-sm uppercase tracking-wide">Real-time Monitoring</span>
                </div>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 mb-12 p-6 bg-slate-800/50 rounded-2xl border border-slate-700/50">
              <div className="text-center">
                <div className="text-3xl font-black text-green-400">99.8%</div>
                <div className="text-xs text-slate-400 uppercase tracking-wide">Uptime</div>
              </div>
              <div className="text-center border-x border-slate-700/50">
                <div className="text-3xl font-black text-blue-400">24/7</div>
                <div className="text-xs text-slate-400 uppercase tracking-wide">Monitoring</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-black text-orange-400">AI</div>
                <div className="text-xs text-slate-400 uppercase tracking-wide">Powered</div>
              </div>
            </div>

            {/* CTA Button */}
            <div className="space-y-4">
              <Link
                href="/tenant-select"
                className="inline-flex items-center space-x-3 px-8 py-4 bg-gradient-to-r from-orange-500 to-red-600 text-white font-bold rounded-xl hover:from-orange-600 hover:to-red-700 transition-all duration-300 transform hover:scale-105 shadow-2xl"
              >
                <span>🚀</span>
                <span>LAUNCH SYSTEM</span>
                <span className="text-orange-200">→</span>
              </Link>
              
              <p className="text-xs text-slate-500 ml-2">
                Select Organization → Authentication → Dashboard
              </p>
            </div>
          </div>
        </div>

        {/* Right Side - Control Panel */}
        <div className="w-96 bg-slate-800/30 backdrop-blur-sm border-l border-slate-700/50 p-8">
          <div className="space-y-8">
            {/* System Status */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-slate-200 font-bold uppercase tracking-wide text-sm">System Status</h3>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-green-400 text-xs font-semibold">OPERATIONAL</span>
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg border border-slate-700/30">
                  <span className="text-slate-400 text-sm">Safety Engine</span>
                  <span className="text-green-400 text-xs font-mono">ACTIVE</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg border border-slate-700/30">
                  <span className="text-slate-400 text-sm">Risk Analysis</span>
                  <span className="text-blue-400 text-xs font-mono">READY</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg border border-slate-700/30">
                  <span className="text-slate-400 text-sm">AI Module</span>
                  <span className="text-orange-400 text-xs font-mono">ONLINE</span>
                </div>
              </div>
            </div>

            {/* Quick Access */}
            <div>
              <h3 className="text-slate-200 font-bold uppercase tracking-wide text-sm mb-4">Quick Access</h3>
              
              <div className="space-y-3">
                <Link
                  href="/auth/login"
                  className="block w-full p-3 bg-slate-900/30 hover:bg-slate-700/50 rounded-lg border border-slate-700/30 hover:border-slate-600 transition-all duration-200 group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-slate-300 text-sm font-medium group-hover:text-white">Direct Login</span>
                    <span className="text-slate-500 text-xs">→</span>
                  </div>
                </Link>
                
                <Link
                  href="/dashboard"
                  className="block w-full p-3 bg-slate-900/30 hover:bg-slate-700/50 rounded-lg border border-slate-700/30 hover:border-slate-600 transition-all duration-200 group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-slate-300 text-sm font-medium group-hover:text-white">Dashboard</span>
                    <span className="text-slate-500 text-xs">→</span>
                  </div>
                </Link>
              </div>
            </div>

            {/* Demo Credentials */}
            <div className="p-4 bg-gradient-to-br from-slate-900/60 to-slate-800/60 rounded-xl border border-slate-700/50">
              <h3 className="text-slate-200 font-bold uppercase tracking-wide text-xs mb-3">Demo Access</h3>
              <div className="space-y-2">
                <div className="text-xs">
                  <span className="text-slate-500">User:</span>
                  <span className="text-orange-400 font-mono ml-2">admin</span>
                </div>
                <div className="text-xs">
                  <span className="text-slate-500">Pass:</span>
                  <span className="text-orange-400 font-mono ml-2">Admin123!</span>
                </div>
                <div className="text-xs">
                  <span className="text-slate-500">Org:</span>
                  <span className="text-orange-400 font-mono ml-2">demo.hse-system.com</span>
                </div>
              </div>
            </div>

            {/* Developer Tools */}
            <div>
              <h3 className="text-slate-200 font-bold uppercase tracking-wide text-sm mb-4">Developer</h3>
              
              <Link
                href="/test-api"
                className="block w-full p-3 bg-yellow-500/10 hover:bg-yellow-500/20 rounded-lg border border-yellow-500/30 hover:border-yellow-400 transition-all duration-200 group"
              >
                <div className="flex items-center justify-between">
                  <span className="text-yellow-400 text-sm font-medium group-hover:text-yellow-300">🔧 API Testing</span>
                  <span className="text-yellow-500 text-xs">→</span>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}