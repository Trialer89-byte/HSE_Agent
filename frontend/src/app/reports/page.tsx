'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function ReportsPage() {
  const router = useRouter();
  const [dateRange, setDateRange] = useState('last30days');

  // Mock data for demonstration
  const stats = {
    totalPermits: 142,
    approvedPermits: 98,
    pendingPermits: 23,
    rejectedPermits: 21,
    highRiskActivities: 15,
    incidentsReported: 3,
    documentsProcessed: 256,
    complianceRate: 94.5,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Industrial Background */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M0 0h25v25H0zM75 0h25v25H75zM25 25h25v25H25zM0 75h25v25H0zM75 75h25v25H75z'/%3E%3C/g%3E%3C/svg%3E")`,
        }} />
      </div>

      {/* Header */}
      <header className="relative z-10 bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link
                href="/dashboard"
                className="flex items-center space-x-2 text-slate-300 hover:text-white transition-colors"
              >
                <span className="text-xl">←</span>
                <span className="text-sm uppercase tracking-wide">Control Center</span>
              </Link>
              <div className="w-px h-6 bg-slate-700"></div>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-black text-lg">📊</span>
                </div>
                <div>
                  <h1 className="text-xl font-black text-white tracking-tight">ANALYTICS</h1>
                  <p className="text-slate-400 text-xs uppercase tracking-wide">Performance & Compliance Reports</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 px-3 py-1 bg-slate-700/50 rounded-lg border border-slate-600/50">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-slate-300 text-xs font-semibold uppercase tracking-wide">Real-time Data</span>
              </div>
              <select
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="px-4 py-2 bg-slate-900/50 border border-slate-600/50 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent font-mono text-sm"
              >
                <option value="last7days">LAST 7 DAYS</option>
                <option value="last30days">LAST 30 DAYS</option>
                <option value="last90days">LAST 90 DAYS</option>
                <option value="lastyear">LAST YEAR</option>
              </select>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-bold text-slate-400 uppercase tracking-wide mb-2">Total Permits</div>
                <div className="text-3xl font-black text-white">{stats.totalPermits}</div>
              </div>
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-black text-xl">📋</span>
              </div>
            </div>
            <div className="mt-4 flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
              <span className="text-slate-500 text-xs uppercase tracking-wide">Active System</span>
            </div>
          </div>

          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-bold text-slate-400 uppercase tracking-wide mb-2">Approved</div>
                <div className="text-3xl font-black text-green-400">{stats.approvedPermits}</div>
              </div>
              <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-black text-xl">✓</span>
              </div>
            </div>
            <div className="mt-4 flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-slate-500 text-xs uppercase tracking-wide">Operational</span>
            </div>
          </div>

          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-bold text-slate-400 uppercase tracking-wide mb-2">Pending</div>
                <div className="text-3xl font-black text-orange-400">{stats.pendingPermits}</div>
              </div>
              <div className="w-14 h-14 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-black text-xl">🕰️</span>
              </div>
            </div>
            <div className="mt-4 flex items-center space-x-2">
              <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse"></div>
              <span className="text-slate-500 text-xs uppercase tracking-wide">Processing</span>
            </div>
          </div>

          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-bold text-slate-400 uppercase tracking-wide mb-2">High Risk</div>
                <div className="text-3xl font-black text-red-400">{stats.highRiskActivities}</div>
              </div>
              <div className="w-14 h-14 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-black text-xl">⚠️</span>
              </div>
            </div>
            <div className="mt-4 flex items-center space-x-2">
              <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse"></div>
              <span className="text-slate-500 text-xs uppercase tracking-wide">Alert Status</span>
            </div>
          </div>
        </div>

        {/* Compliance Section */}
        <div className="mb-8 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-black text-sm">✓</span>
            </div>
            <h3 className="text-xl font-black text-white tracking-tight">COMPLIANCE OVERVIEW</h3>
          </div>
          
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-bold text-slate-400 uppercase tracking-wide">Overall Compliance Rate</span>
              <span className="text-4xl font-black text-green-400">{stats.complianceRate}%</span>
            </div>
            <div className="h-3 bg-slate-700/50 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-green-500 to-green-400 rounded-full transition-all duration-1000"
                style={{ width: `${stats.complianceRate}%` }}
              ></div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
            <div className="p-4 bg-slate-900/30 border border-slate-700/30 rounded-xl">
              <div className="text-sm font-bold text-slate-400 uppercase tracking-wide mb-2">Documents Processed</div>
              <div className="text-2xl font-black text-white">{stats.documentsProcessed}</div>
              <div className="mt-2 flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span className="text-slate-500 text-xs uppercase tracking-wide">Archive</span>
              </div>
            </div>
            <div className="p-4 bg-slate-900/30 border border-slate-700/30 rounded-xl">
              <div className="text-sm font-bold text-slate-400 uppercase tracking-wide mb-2">Incidents Reported</div>
              <div className="text-2xl font-black text-orange-400">{stats.incidentsReported}</div>
              <div className="mt-2 flex items-center space-x-2">
                <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                <span className="text-slate-500 text-xs uppercase tracking-wide">Monitor</span>
              </div>
            </div>
            <div className="p-4 bg-slate-900/30 border border-slate-700/30 rounded-xl">
              <div className="text-sm font-bold text-slate-400 uppercase tracking-wide mb-2">Rejected Permits</div>
              <div className="text-2xl font-black text-red-400">{stats.rejectedPermits}</div>
              <div className="mt-2 flex items-center space-x-2">
                <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                <span className="text-slate-500 text-xs uppercase tracking-wide">Review</span>
              </div>
            </div>
          </div>
        </div>

        {/* Activity Chart Placeholder */}
        <div className="mb-8 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-black text-sm">📊</span>
            </div>
            <h3 className="text-xl font-black text-white tracking-tight">PERMIT ACTIVITY TREND</h3>
          </div>
          <div className="h-64 flex items-center justify-center bg-slate-900/30 border border-slate-700/30 rounded-xl">
            <div className="text-center">
              <div className="text-4xl mb-4">📈</div>
              <p className="text-slate-400 font-mono text-sm">REAL-TIME ANALYTICS MODULE</p>
              <p className="text-slate-500 text-xs mt-2 uppercase tracking-wide">Chart visualization interface loading...</p>
            </div>
          </div>
        </div>

        {/* Export Section */}
        <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-black text-sm">⬇️</span>
            </div>
            <div>
              <h3 className="text-xl font-black text-white tracking-tight">EXPORT REPORTS</h3>
              <p className="text-slate-400 text-sm">
                Generate compliance documentation and analytical reports
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <button className="flex items-center space-x-3 px-6 py-4 bg-slate-900/30 hover:bg-slate-700/40 border border-slate-700/30 hover:border-slate-600 rounded-xl transition-all duration-200 group">
              <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-red-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-black text-sm">📊</span>
              </div>
              <div className="text-left">
                <div className="text-white font-bold text-sm group-hover:text-orange-400 transition-colors">MONTHLY REPORT</div>
                <div className="text-slate-400 text-xs uppercase tracking-wide">PDF Format</div>
              </div>
            </button>
            
            <button className="flex items-center space-x-3 px-6 py-4 bg-slate-900/30 hover:bg-slate-700/40 border border-slate-700/30 hover:border-slate-600 rounded-xl transition-all duration-200 group">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-black text-sm">📈</span>
              </div>
              <div className="text-left">
                <div className="text-white font-bold text-sm group-hover:text-orange-400 transition-colors">COMPLIANCE REPORT</div>
                <div className="text-slate-400 text-xs uppercase tracking-wide">Excel Format</div>
              </div>
            </button>
            
            <button className="flex items-center space-x-3 px-6 py-4 bg-slate-900/30 hover:bg-slate-700/40 border border-slate-700/30 hover:border-slate-600 rounded-xl transition-all duration-200 group">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-black text-sm">📝</span>
              </div>
              <div className="text-left">
                <div className="text-white font-bold text-sm group-hover:text-orange-400 transition-colors">ACTIVITY SUMMARY</div>
                <div className="text-slate-400 text-xs uppercase tracking-wide">CSV Format</div>
              </div>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}