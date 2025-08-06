'use client';

import { useState } from 'react';

export default function TestPage() {
  const [count, setCount] = useState(0);
  const [message, setMessage] = useState('');

  const handleClick = () => {
    setCount(count + 1);
    setMessage(`Button clicked ${count + 1} times`);
  };

  const testApiCall = async () => {
    try {
      const response = await fetch('/api/health');
      if (response.ok) {
        const data = await response.json();
        setMessage(`API Response: ${JSON.stringify(data)}`);
      } else {
        setMessage('API call failed');
      }
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 px-6">
      <div className="mx-auto max-w-md">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Test Page</h1>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="mb-4">Count: {count}</p>
          <p className="mb-4 text-sm text-gray-600">{message}</p>
          
          <div className="space-y-4">
            <button
              onClick={handleClick}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Test Click Handler
            </button>
            
            <button
              onClick={testApiCall}
              className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Test API Call
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}