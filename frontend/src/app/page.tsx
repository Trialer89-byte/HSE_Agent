'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-xl">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
            <span className="text-white font-bold text-2xl">HSE</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            HSE Management System
          </h1>
          <p className="text-gray-600">
            Health, Safety & Environment Platform
          </p>
        </div>
        
        <div className="space-y-4 pt-6">
          <div className="border-t border-gray-200 pt-4">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-3">Produzione</p>
            
            <Link
              href="/tenant-select"
              className="block w-full text-center px-4 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
            >
              🚀 Accedi al Sistema
            </Link>
            
            <p className="text-xs text-gray-500 text-center mt-2">
              Seleziona tenant → Login → Dashboard
            </p>
          </div>
          
          <div className="border-t border-gray-200 pt-4">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-3">Quick Links</p>
            
            <div className="grid grid-cols-2 gap-2">
              <Link
                href="/auth/login"
                className="text-center px-3 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors text-sm"
              >
                Login Diretto
              </Link>
              
              <Link
                href="/dashboard"
                className="text-center px-3 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors text-sm"
              >
                Dashboard
              </Link>
            </div>
          </div>
          
          <div className="border-t border-gray-200 pt-4">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-3">Developer</p>
            
            <Link
              href="/test-api"
              className="block w-full text-center px-3 py-2 bg-yellow-50 text-yellow-700 rounded hover:bg-yellow-100 transition-colors text-sm border border-yellow-200"
            >
              🔧 Test API & Debug
            </Link>
          </div>
        </div>
        
        <div className="pt-4 border-t border-gray-200">
          <div className="text-xs text-gray-400 space-y-1 text-center">
            <p>Backend: localhost:8000 | Frontend: localhost:3000</p>
            <p>Demo: admin / Admin123! @ demo.hse-system.com</p>
          </div>
        </div>
      </div>
    </div>
  );
}