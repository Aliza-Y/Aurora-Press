'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';

interface Trend {
  trend_id: string;
  keyword: string;
  title: string;
  score: number;
  type: string;
  category: string;
  source: string;
}

const categories = [
  { id: 'all', name: 'All' },
  { id: 'politics', name: 'Politics' },
  { id: 'technology', name: 'Technology' },
  { id: 'science', name: 'Science' },
  { id: 'business', name: 'Business' },
  { id: 'entertainment', name: 'Entertainment' },
  { id: 'sports', name: 'Sports' },
  { id: 'conflict', name: 'Conflict' }
];

const API_BASE_URL = 'http://localhost:8000';

export default function TrendAnalysis() {
  const [activeCategory, setActiveCategory] = useState('all');
  const [trends, setTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetchTrends();
  }, [activeCategory]);

  const fetchTrends = async () => {
    try {
      setLoading(true);
      const url = activeCategory === 'all' 
        ? `${API_BASE_URL}/api/trends`
        : `${API_BASE_URL}/api/trends?category=${activeCategory.toLowerCase()}`;
      
      console.log('Fetching trends from:', url);
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Trends data:', data);
      setTrends(data.trends || []);
    } catch (error) {
      console.error('Error fetching trends:', error);
      setTrends([]);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateArticle = async (trendId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/approve_trend/${trendId}`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      router.push('/dashboard/articles');
    } catch (error) {
      console.error('Error generating article:', error);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Trending Topics</h1>
        <p className="text-gray-400">
          Discover and generate articles from trending topics across different categories
        </p>
      </div>

      {/* Category filters */}
      <div className="flex flex-wrap gap-2 mb-8">
        {categories.map((category) => (
          <button
            key={category.id}
            onClick={() => setActiveCategory(category.id)}
            className={`
              px-4 py-2 rounded-full text-sm font-medium transition-all duration-200
              ${activeCategory === category.id
                ? 'bg-aurora-primary text-white shadow-lg shadow-aurora-primary/20'
                : 'bg-[#1e2a4a] text-aurora-text-secondary hover:bg-aurora-secondary/30'
              }
            `}
          >
            {category.name}
          </button>
        ))}
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-aurora-primary"></div>
        </div>
      )}

      {/* Empty state */}
      {!loading && trends.length === 0 && (
        <div className="text-center py-12 bg-aurora-card rounded-lg">
          <p className="text-aurora-text-secondary mb-2">No trends found for this category</p>
          <button
            onClick={() => setActiveCategory('all')}
            className="text-aurora-primary hover:underline"
          >
            View all trends
          </button>
        </div>
      )}

      {/* Trend cards grid */}
      {!loading && trends.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {trends.map((trend) => (
            <motion.div
              key={trend.trend_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              whileHover={{ scale: 1.02 }}
              className="bg-aurora-card rounded-lg p-6 border border-aurora-border hover:border-aurora-primary/20 transition-all duration-200"
            >
              <Link href={`/dashboard/trend-analysis/${trend.trend_id}`}>
                <div className="mb-4 cursor-pointer">
                  <h3 className="text-xl font-semibold text-white mb-3 hover:text-aurora-primary transition-colors">
                    {trend.title || trend.keyword}
                  </h3>
                  <div className="flex flex-wrap items-center gap-2 mb-3">
                    <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-[#1e2a4a] text-aurora-text-secondary">
                      {trend.category}
                    </span>
                    <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-aurora-primary/10 text-aurora-primary">
                      Score: {trend.score.toFixed(1)}
                    </span>
                  </div>
                  <p className="text-aurora-text-secondary text-sm">
                    Click to view more details about this trending topic and its context.
                  </p>
                </div>
              </Link>

              <div className="flex items-center justify-between mt-6 pt-4 border-t border-aurora-border">
                <span className="text-aurora-text-secondary text-sm">
                  Source: {trend.source}
                </span>
                <button
                  onClick={() => handleGenerateArticle(trend.trend_id)}
                  className="inline-flex items-center px-4 py-2 bg-aurora-primary text-white rounded-full hover:bg-aurora-primary/90 transition-all duration-200 text-sm font-medium shadow-lg shadow-aurora-primary/20"
                >
                  <span className="mr-1">+</span> Generate Article
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
} 