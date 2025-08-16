'use client';

import { useState, useCallback } from 'react';

export default function TestApiPage() {
  const [results, setResults] = useState<{[key: string]: string}>({});
  const [loading, setLoading] = useState<{[key: string]: boolean}>({});
  const [componentTest, setComponentTest] = useState('Component OK');

  const addResult = useCallback((key: string, message: string) => {
    console.log(`[${key}] ${message}`);
    setResults(prev => ({...prev, [key]: message}));
  }, []);

  const testHealthCheck = useCallback(async () => {
    console.log('Starting health check...');
    setLoading(prev => ({...prev, health: true}));
    addResult('health', 'Testing health endpoint...');
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        console.log('Health check timeout triggered');
        controller.abort();
      }, 5000);
      
      console.log(`Fetching ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/health`);
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/health`, {
        signal: controller.signal,
        mode: 'cors',
        credentials: 'omit'
      });
      
      clearTimeout(timeoutId);
      console.log('Health check response received:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Health check data:', data);
      addResult('health', '✅ Health Check Success:\n' + JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('Health check error:', error);
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          addResult('health', '❌ Request timed out after 5 seconds\nCheck if backend is running on port 8000');
        } else {
          addResult('health', '❌ Health Check Failed:\n' + error.message);
        }
      } else {
        addResult('health', '❌ Health Check Failed:\n' + String(error));
      }
    } finally {
      setLoading(prev => ({...prev, health: false}));
    }
  }, [addResult]);

  const testTenantValidation = useCallback(async () => {
    console.log('Starting tenant validation...');
    setLoading(prev => ({...prev, tenant: true}));
    addResult('tenant', 'Testing tenant validation...');
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        console.log('Tenant validation timeout triggered');
        controller.abort();
      }, 5000);
      
      const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/public/tenants/validate?domain=demo.hse-system.com`;
      console.log('Fetching:', url);
      
      const response = await fetch(url, {
        signal: controller.signal,
        mode: 'cors',
        credentials: 'omit'
      });
      
      clearTimeout(timeoutId);
      console.log('Tenant validation response received:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => '');
        throw new Error(`HTTP ${response.status}: ${response.statusText}\n${errorText}`);
      }
      
      const data = await response.json();
      console.log('Tenant validation data:', data);
      addResult('tenant', '✅ Tenant Validation Success:\n' + JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('Tenant validation error:', error);
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          addResult('tenant', '❌ Request timed out after 5 seconds');
        } else {
          addResult('tenant', '❌ Tenant Validation Failed:\n' + error.message);
        }
      } else {
        addResult('tenant', '❌ Tenant Validation Failed:\n' + String(error));
      }
    } finally {
      setLoading(prev => ({...prev, tenant: false}));
    }
  }, [addResult]);

  const testCORSPreflight = useCallback(async () => {
    console.log('Starting CORS preflight test...');
    setLoading(prev => ({...prev, cors: true}));
    addResult('cors', 'Testing CORS preflight...');
    
    try {
      console.log(`Sending OPTIONS request to ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/health`);
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/health`, {
        method: 'OPTIONS',
        headers: {
          'Origin': 'http://localhost:3000',
          'Access-Control-Request-Method': 'GET',
          'Access-Control-Request-Headers': 'Content-Type'
        }
      });
      
      console.log('CORS response received:', response.status);
      
      const corsHeaders = {
        'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
        'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
        'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
      };
      
      console.log('CORS headers:', corsHeaders);
      
      const isConfigured = corsHeaders['Access-Control-Allow-Origin'] !== null;
      addResult('cors', (isConfigured ? '✅' : '❌') + ' CORS Headers:\n' + JSON.stringify(corsHeaders, null, 2));
    } catch (error) {
      console.error('CORS test error:', error);
      addResult('cors', '❌ CORS Test Failed:\n' + String(error));
    } finally {
      setLoading(prev => ({...prev, cors: false}));
    }
  }, [addResult]);

  const testAllEndpoints = useCallback(async () => {
    console.log('Testing all endpoints...');
    await testHealthCheck();
    await new Promise(resolve => setTimeout(resolve, 100));
    await testCORSPreflight();
    await new Promise(resolve => setTimeout(resolve, 100));
    await testTenantValidation();
  }, [testHealthCheck, testCORSPreflight, testTenantValidation]);

  const clearResults = useCallback(() => {
    setResults({});
  }, []);

  // Test semplice senza API
  const testSimpleComponent = useCallback(() => {
    setComponentTest('Testing...');
    setTimeout(() => {
      setComponentTest('✅ Component works without blocking!');
    }, 1000);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Industrial Background */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M0 0h25v25H0zM75 0h25v25H75zM25 25h25v25H25zM0 75h25v25H0zM75 75h25v25H75z'/%3E%3C/g%3E%3C/svg%3E")`,
        }} />
      </div>

      <div className="relative z-10 p-8 max-w-6xl mx-auto">
        <div className="flex items-center space-x-4 mb-8">
          <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-xl flex items-center justify-center">
            <span className="text-white font-black text-2xl">🔧</span>
          </div>
          <div>
            <h1 className="text-3xl font-black text-white tracking-tight">DEVELOPER DIAGNOSTICS</h1>
            <p className="text-slate-400 text-sm uppercase tracking-wide">System Testing & Validation Interface</p>
          </div>
        </div>
      
        <div className="mb-8 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-black text-sm">✓</span>
            </div>
            <h2 className="text-xl font-black text-white tracking-tight">SYSTEM STATUS</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <div className="font-mono text-sm">
                  <span className="text-slate-400">Backend:</span>
                  <span className="text-blue-400 ml-2">{process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}</span>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <div className="font-mono text-sm">
                  <span className="text-slate-400">Frontend:</span>
                  <span className="text-green-400 ml-2">{typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000'}</span>
                </div>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                <div className="font-mono text-sm">
                  <span className="text-slate-400">Component:</span>
                  <span className="text-orange-400 ml-2">{componentTest}</span>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                <div className="font-mono text-sm">
                  <span className="text-slate-400">Console:</span>
                  <span className="text-purple-400 ml-2">F12 for detailed logs</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mb-8 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-black text-sm">⚙️</span>
            </div>
            <h2 className="text-xl font-black text-white tracking-tight">TEST CONTROLS</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <button
              onClick={testSimpleComponent}
              className="flex items-center space-x-3 px-6 py-4 bg-slate-900/50 hover:bg-slate-700/50 border border-slate-600/50 rounded-xl transition-all duration-200 group"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-slate-500 to-slate-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-black text-xs">✓</span>
              </div>
              <div className="text-left">
                <div className="text-white font-bold text-sm group-hover:text-orange-400 transition-colors">COMPONENT TEST</div>
                <div className="text-slate-400 text-xs uppercase tracking-wide">No API Required</div>
              </div>
            </button>

            <button
              onClick={testHealthCheck}
              disabled={loading.health}
              className="flex items-center space-x-3 px-6 py-4 bg-slate-900/50 hover:bg-slate-700/50 border border-slate-600/50 rounded-xl transition-all duration-200 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-black text-xs">❤️</span>
              </div>
              <div className="text-left">
                <div className="text-white font-bold text-sm group-hover:text-orange-400 transition-colors">
                  {loading.health ? 'TESTING...' : 'HEALTH CHECK'}
                </div>
                <div className="text-slate-400 text-xs uppercase tracking-wide">Backend Status</div>
              </div>
            </button>

            <button
              onClick={testCORSPreflight}
              disabled={loading.cors}
              className="flex items-center space-x-3 px-6 py-4 bg-slate-900/50 hover:bg-slate-700/50 border border-slate-600/50 rounded-xl transition-all duration-200 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-black text-xs">🔄</span>
              </div>
              <div className="text-left">
                <div className="text-white font-bold text-sm group-hover:text-orange-400 transition-colors">
                  {loading.cors ? 'TESTING...' : 'CORS TEST'}
                </div>
                <div className="text-slate-400 text-xs uppercase tracking-wide">Cross-Origin</div>
              </div>
            </button>

            <button
              onClick={testTenantValidation}
              disabled={loading.tenant}
              className="flex items-center space-x-3 px-6 py-4 bg-slate-900/50 hover:bg-slate-700/50 border border-slate-600/50 rounded-xl transition-all duration-200 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-black text-xs">🏢</span>
              </div>
              <div className="text-left">
                <div className="text-white font-bold text-sm group-hover:text-orange-400 transition-colors">
                  {loading.tenant ? 'TESTING...' : 'TENANT API'}
                </div>
                <div className="text-slate-400 text-xs uppercase tracking-wide">Multi-tenant</div>
              </div>
            </button>

            <button
              onClick={testAllEndpoints}
              disabled={Object.values(loading).some(l => l)}
              className="flex items-center space-x-3 px-6 py-4 bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 rounded-xl transition-all duration-200 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                <span className="text-white font-black text-xs">⚡</span>
              </div>
              <div className="text-left">
                <div className="text-white font-bold text-sm group-hover:text-purple-200 transition-colors">RUN ALL TESTS</div>
                <div className="text-purple-200 text-xs uppercase tracking-wide">Full Suite</div>
              </div>
            </button>

            <button
              onClick={clearResults}
              className="flex items-center space-x-3 px-6 py-4 bg-slate-900/50 hover:bg-slate-700/50 border border-slate-600/50 rounded-xl transition-all duration-200 group"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-red-500 to-red-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-black text-xs">🗑️</span>
              </div>
              <div className="text-left">
                <div className="text-white font-bold text-sm group-hover:text-orange-400 transition-colors">CLEAR RESULTS</div>
                <div className="text-slate-400 text-xs uppercase tracking-wide">Reset Output</div>
              </div>
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {Object.entries(results).map(([key, result]) => (
            <div key={key} className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-black text-xs">📊</span>
                </div>
                <h3 className="text-lg font-black text-white tracking-tight capitalize">{key} TEST RESULT</h3>
              </div>
              <div className="bg-slate-900/50 border border-slate-700/30 rounded-xl p-4">
                <pre className="text-sm overflow-x-auto whitespace-pre-wrap font-mono text-slate-200">
                  {result}
                </pre>
              </div>
            </div>
          ))}
          
          {Object.keys(results).length === 0 && (
            <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 text-center">
              <div className="w-16 h-16 bg-slate-700/50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-slate-400 text-2xl">📊</span>
              </div>
              <p className="text-slate-300 font-semibold mb-2">AWAITING TEST EXECUTION</p>
              <p className="text-slate-400 text-sm mb-4">
                Select a test button above to validate API connections and system functionality
              </p>
              <div className="px-4 py-2 bg-slate-700/30 border border-slate-600/30 rounded-xl inline-block">
                <p className="text-xs text-slate-400 uppercase tracking-wide">
                  Press F12 to monitor console output during testing
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="mt-8 bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/30 rounded-2xl p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-black text-sm">⚠️</span>
            </div>
            <h3 className="text-lg font-black text-orange-300 tracking-tight">TROUBLESHOOTING GUIDE</h3>
          </div>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2 flex-shrink-0"></div>
              <div className="text-sm text-yellow-200">
                <strong>Page Blocks:</strong> Check browser console (F12) for JavaScript errors
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2 flex-shrink-0"></div>
              <div className="text-sm text-yellow-200">
                <strong>Request Failures:</strong> Ensure backend service is active on port 8000
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2 flex-shrink-0"></div>
              <div className="text-sm text-yellow-200">
                <strong>CORS Errors:</strong> Backend cross-origin configuration requires updating
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2 flex-shrink-0"></div>
              <div className="text-sm text-yellow-200">
                <strong>Alternative:</strong> <a href="/test-api.html" className="underline text-orange-400 hover:text-orange-300">Static HTML test interface</a> available
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}