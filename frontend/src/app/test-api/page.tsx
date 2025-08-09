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
      
      console.log('Fetching http://localhost:8000/health');
      const response = await fetch('http://localhost:8000/health', {
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
      
      const url = 'http://localhost:8000/api/v1/public/tenants/validate?domain=demo.hse-system.com';
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
      console.log('Sending OPTIONS request to http://localhost:8000/health');
      const response = await fetch('http://localhost:8000/health', {
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
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">🔧 Developer Test Page</h1>
      
      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
        <h2 className="text-lg font-semibold mb-2">System Status</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Backend: http://localhost:8000</p>
            <p className="text-sm text-gray-600">Frontend: http://localhost:3000</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Component Status: {componentTest}</p>
            <p className="text-xs text-gray-500">Console (F12) for detailed logs</p>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-4 mb-6">
        <button
          onClick={testSimpleComponent}
          className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          Test Component (No API)
        </button>
        <button
          onClick={testHealthCheck}
          disabled={loading.health}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading.health ? 'Testing...' : 'Test Health'}
        </button>

        <button
          onClick={testCORSPreflight}
          disabled={loading.cors}
          className="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading.cors ? 'Testing...' : 'Test CORS'}
        </button>

        <button
          onClick={testTenantValidation}
          disabled={loading.tenant}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading.tenant ? 'Testing...' : 'Test Tenant API'}
        </button>

        <button
          onClick={testAllEndpoints}
          disabled={Object.values(loading).some(l => l)}
          className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Test All
        </button>

        <button
          onClick={clearResults}
          className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          Clear Results
        </button>
      </div>

      <div className="space-y-4">
        {Object.entries(results).map(([key, result]) => (
          <div key={key} className="border rounded-lg p-4">
            <h3 className="font-semibold mb-2 capitalize">{key} Test Result:</h3>
            <pre className="bg-gray-100 p-3 rounded text-sm overflow-x-auto whitespace-pre-wrap font-mono">
              {result}
            </pre>
          </div>
        ))}
        
        {Object.keys(results).length === 0 && (
          <div className="border rounded-lg p-4 bg-gray-50">
            <p className="text-gray-600">Click a button above to test API connections</p>
            <p className="text-sm text-gray-500 mt-2">
              If buttons don&apos;t work, check the browser console for errors (F12)
            </p>
          </div>
        )}
      </div>

      <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h3 className="font-semibold text-yellow-800 mb-2">Troubleshooting:</h3>
        <ul className="text-sm text-yellow-700 space-y-1">
          <li>• If page blocks: Check browser console for JavaScript errors</li>
          <li>• If requests fail: Ensure backend is running on port 8000</li>
          <li>• If CORS errors: Backend CORS configuration may need updating</li>
          <li>• Try the <a href="/test-api.html" className="underline">static HTML test page</a> as alternative</li>
        </ul>
      </div>
    </div>
  );
}