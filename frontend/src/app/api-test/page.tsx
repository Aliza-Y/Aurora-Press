'use client';

import { useState } from 'react';

export default function ApiTest() {
  const [result, setResult] = useState<string>('Click to test');
  const [loading, setLoading] = useState(false);

  const testApi = async () => {
    setLoading(true);
    setResult('Testing...');
    
    try {
      console.log('Starting API test...');
      const response = await fetch('http://localhost:8000/api/trends', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      console.log('Response received:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Data received:', data);
      setResult(`Success! Received ${data.trends?.length || 0} trends`);
    } catch (error) {
      console.error('API test error:', error);
      setResult(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">API Test</h1>
      <button 
        onClick={testApi}
        disabled={loading}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? 'Testing...' : 'Test API'}
      </button>
      <div className="mt-4 p-4 bg-gray-100 rounded">
        <pre>{result}</pre>
      </div>
    </div>
  );
}









