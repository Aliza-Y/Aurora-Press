'use client';

import { useState, useEffect } from 'react';

interface Trend {
  trend_id: string;
  keyword: string;
  title: string;
  score: number;
  category: string;
  summary: string;
}

export default function TestDashboard() {
  const [trends, setTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTrends();
  }, []);

  const fetchTrends = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Fetching trends from: http://localhost:8000/api/trends');
      
      // Add a timeout to prevent hanging
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      const response = await fetch('http://localhost:8000/api/trends', {
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      clearTimeout(timeoutId);
      
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Received trends:', data);
      
      if (!data.trends) {
        throw new Error('No trends data received');
      }
      
      setTrends(data.trends);
    } catch (error) {
      console.error('Error fetching trends:', error);
      if (error instanceof Error && error.name === 'AbortError') {
        setError('Request timed out after 10 seconds');
      } else {
        setError(error instanceof Error ? error.message : 'Failed to fetch trends');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p>Loading trends...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-500 mb-4">Error</h1>
          <p className="text-gray-300 mb-4">{error}</p>
          <button 
            onClick={fetchTrends}
            className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Test Dashboard - Trends</h1>
        
        <div className="mb-4">
          <p className="text-gray-300">Found {trends.length} trends</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {trends.map((trend) => (
            <div key={trend.trend_id} className="bg-gray-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">{trend.title}</h3>
              <p className="text-sm text-gray-400 mb-2">Keyword: {trend.keyword}</p>
              <p className="text-sm text-gray-400 mb-2">Category: {trend.category}</p>
              <p className="text-sm text-gray-400 mb-2">Score: {trend.score}</p>
              <p className="text-sm text-gray-300">{trend.summary}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
