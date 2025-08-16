'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiCall } from '@/config/api';
import Link from 'next/link';

interface WorkPermit {
  id: number;
  permit_number?: string;
  title: string;
  description: string;
  work_type?: string;
  location?: string;
  status?: string;
  risk_level?: string;
  start_date?: string;
  end_date?: string;
  created_by?: string;
  created_at: string;
  approved_by?: string;
  approved_at?: string;
}

export default function WorkPermitsPage() {
  const [permits, setPermits] = useState<WorkPermit[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchPermits();
  }, []);

  const fetchPermits = async () => {
    try {
      setIsLoading(true);
      const response = await apiCall('/api/v1/permits/', {
        method: 'GET',
      });
      setPermits(response.permits || []);
    } catch (error: any) {
      console.error('Error fetching permits:', error);
      setError(error.message || 'Failed to fetch work permits');
      if (error.message?.includes('401') || error.message?.includes('Unauthorized')) {
        router.push('/auth/login');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string | undefined) => {
    if (!status) return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
    
    switch (status.toLowerCase()) {
      case 'approved':
      case 'approvato':
        return 'bg-green-500/20 text-green-300 border-green-500/30';
      case 'pending':
      case 'in_attesa':
        return 'bg-orange-500/20 text-orange-300 border-orange-500/30';
      case 'rejected':
      case 'rifiutato':
        return 'bg-red-500/20 text-red-300 border-red-500/30';
      case 'expired':
      case 'scaduto':
        return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
      case 'draft':
      case 'bozza':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      default:
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
    }
  };

  const getRiskColor = (risk: string | undefined) => {
    if (!risk) return 'text-slate-400';
    
    switch (risk.toLowerCase()) {
      case 'high':
      case 'alto':
        return 'text-red-400';
      case 'medium':
      case 'medio':
        return 'text-orange-400';
      case 'low':
      case 'basso':
        return 'text-green-400';
      default:
        return 'text-slate-400';
    }
  };

  const getRiskIcon = (risk: string | undefined) => {
    if (!risk) return '❓';
    
    switch (risk.toLowerCase()) {
      case 'high':
      case 'alto':
        return '🔴';
      case 'medium':
      case 'medio':
        return '🟡';
      case 'low':
      case 'basso':
        return '🟢';
      default:
        return '❓';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-orange-500/30 border-t-orange-500 rounded-full animate-spin mx-auto"></div>
          <p className="mt-6 text-slate-400 font-medium">Loading permit database...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center p-8 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl">
          <div className="text-4xl mb-4">⚠️</div>
          <p className="text-red-400 font-mono text-sm mb-6">ERROR: {error}</p>
          <Link
            href="/dashboard"
            className="px-6 py-3 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white font-bold rounded-xl transition-all duration-200"
          >
            ← RETURN TO CONTROL CENTER
          </Link>
        </div>
      </div>
    );
  }

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
                <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-black text-lg">🏗️</span>
                </div>
                <div>
                  <h1 className="text-xl font-black text-white tracking-tight">WORK PERMITS</h1>
                  <p className="text-slate-400 text-xs uppercase tracking-wide">Risk Authorization System</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 px-3 py-1 bg-slate-700/50 rounded-lg border border-slate-600/50">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-slate-300 text-xs font-semibold uppercase tracking-wide">System Active</span>
              </div>
              <button
                onClick={() => router.push('/work-permits/new')}
                className="px-6 py-2 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white font-bold rounded-xl transition-all duration-200 text-sm"
              >
                + NEW PERMIT
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {permits.length === 0 ? (
          <div className="text-center py-24">
            <div className="w-24 h-24 bg-slate-800/40 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <span className="text-4xl">📋</span>
            </div>
            <h3 className="text-2xl font-black text-white mb-2">NO ACTIVE PERMITS</h3>
            <p className="text-slate-400 mb-8">Initialize your first work authorization</p>
            <button
              onClick={() => router.push('/work-permits/new')}
              className="px-8 py-4 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white font-bold rounded-xl transition-all duration-200 transform hover:scale-105"
            >
              🚀 CREATE FIRST PERMIT
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {permits.map((permit) => (
              <Link
                key={permit.id}
                href={`/work-permits/${permit.id}`}
                className="block bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 hover:bg-slate-700/40 hover:border-slate-600/50 transition-all duration-300 group"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                      <span className="text-white font-bold text-lg">#{permit.id}</span>
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white group-hover:text-orange-400 transition-colors">
                        {permit.permit_number || `PERMIT-${String(permit.id).padStart(4, '0')}`}
                      </h3>
                      <p className="text-slate-400 text-sm">{permit.title}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="text-lg">{getRiskIcon(permit.risk_level)}</span>
                        <span className={`text-sm font-semibold uppercase tracking-wide ${getRiskColor(permit.risk_level)}`}>
                          {permit.risk_level || 'Unknown'} Risk
                        </span>
                      </div>
                      <span
                        className={`px-3 py-1 text-xs font-semibold rounded-lg border uppercase tracking-wide ${getStatusColor(permit.status)}`}
                      >
                        {permit.status || 'Unknown'}
                      </span>
                    </div>
                    
                    <div className="text-slate-500 group-hover:text-orange-400 transition-colors">
                      <span className="text-xl">→</span>
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-500">📍</span>
                    <span className="text-slate-300">
                      {permit.location || 'Location not specified'}
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-500">📅</span>
                    <span className="text-slate-300 font-mono text-xs">
                      {permit.start_date ? new Date(permit.start_date).toLocaleDateString() : 'TBD'}
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-500">👷</span>
                    <span className="text-slate-300">
                      {permit.created_by || 'System'}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}