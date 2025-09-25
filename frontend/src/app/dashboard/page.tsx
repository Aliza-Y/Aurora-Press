'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { IconTrendingUp, IconArticle } from '@tabler/icons-react';
import MainLayout from '@/components/layout/MainLayout';

interface Category {
  id: string;
  name: string;
}

interface Trend {
  trend_id: string;
  keyword: string;
  title: string;
  score: number;
  type: string;
  category: string;
  source: string;
  source_url: string;
  summary: string;
}

export default function Dashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [activeCategory, setActiveCategory] = useState('all');
  const [trends, setTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<Category[]>([
    { id: 'all', name: 'All' }
  ]);
  const [generatingArticle, setGeneratingArticle] = useState<string | null>(null);
  const [generatedArticlesCount, setGeneratedArticlesCount] = useState(0);

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/');
    }
  }, [status, router]);

  useEffect(() => {
    fetchCategories();
    fetchGeneratedArticlesCount();
  }, []);

  useEffect(() => {
    if (activeCategory) {
      fetchTrends();
    }
  }, [activeCategory]);

  const fetchCategories = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/categories');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      
      // Transform categories into the required format
      const formattedCategories = [
        { id: 'all', name: 'All' },
        ...data.categories.map((cat: string) => ({
          id: cat,
          name: cat.charAt(0).toUpperCase() + cat.slice(1)
        }))
      ];
      
      setCategories(formattedCategories);
      console.log('Available categories:', formattedCategories);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchGeneratedArticlesCount = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/articles');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setGeneratedArticlesCount(data.count || 0);
    } catch (error) {
      console.error('Error fetching generated articles count:', error);
    }
  };

  const fetchTrends = async () => {
    try {
      setLoading(true);
      setError(null);
      const url = activeCategory === 'all' 
        ? 'http://localhost:8000/api/trends'
        : `http://localhost:8000/api/trends?category=${activeCategory}`;
      
      console.log('Fetching trends from:', url);
      const response = await fetch(url);
      
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
      setError(error instanceof Error ? error.message : 'Failed to fetch trends');
      setTrends([]);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateArticle = async (trendId: string) => {
    try {
      setGeneratingArticle(trendId);
      const response = await fetch(`http://localhost:8000/approve_trend/${trendId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      // After successful generation, update the count
      fetchGeneratedArticlesCount();
      router.push(`/dashboard/articles/${result.article?._id || result._id}`);
    } catch (error) {
      console.error('Error generating article:', error);
      alert('Failed to generate article. Please try again.');
    } finally {
      setGeneratingArticle(null);
    }
  };

  if (status === 'loading' || !session) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <MainLayout>
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2 text-white">Welcome back, {session?.user?.name}</h1>
          <p className="text-gray-400">Here are the latest trending topics for you to explore.</p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-[#1E293B] p-6 rounded-xl">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-[#2DD4BF]/10 rounded-lg">
                <IconTrendingUp className="w-6 h-6 text-[#2DD4BF]" />
              </div>
              <div>
                <h3 className="text-sm text-gray-400">Active Trends</h3>
                <p className="text-2xl font-semibold text-white">{trends.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-[#1E293B] p-6 rounded-xl">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-[#2DD4BF]/10 rounded-lg">
                <IconArticle className="w-6 h-6 text-[#2DD4BF]" />
              </div>
              <div>
                <h3 className="text-sm text-gray-400">Generated Articles</h3>
                <p className="text-2xl font-semibold text-white">{generatedArticlesCount}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap gap-2 mb-6 overflow-x-auto">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setActiveCategory(category.id)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap ${
                activeCategory === category.id
                  ? 'bg-[#2DD4BF] text-white'
                  : 'bg-[#1E293B] text-gray-400 hover:bg-gray-800'
              }`}
            >
              {category.name}
            </button>
          ))}
        </div>

        {/* Trends Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            <div className="col-span-full flex justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#2DD4BF]"></div>
            </div>
          ) : error ? (
            <div className="col-span-full text-center py-12 text-red-400">
              {error}
            </div>
          ) : trends.length === 0 ? (
            <div className="col-span-full text-center py-12 text-gray-400">
              No trends found for this category.
            </div>
          ) : (
            trends.map((trend) => (
              <motion.div
                key={trend.trend_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-[#1E293B] p-6 rounded-xl hover:bg-gray-800/50 transition-colors cursor-pointer group"
                onClick={() => router.push(`/dashboard/trend/${trend.trend_id}`)}
              >
                <div className="flex justify-between items-start mb-4">
                  <span className="px-3 py-1 text-xs font-medium bg-[#2DD4BF]/10 text-[#2DD4BF] rounded-full">
                    {trend.category.charAt(0).toUpperCase() + trend.category.slice(1)}
                  </span>
                  <span className="text-sm text-gray-400">
                    Score: {trend.score.toFixed(2)}
                  </span>
                </div>
                <h3 className="text-lg font-semibold mb-3 text-white group-hover:text-[#2DD4BF] transition-colors">
                  {trend.title}
                </h3>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">
                    Source: {trend.source}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleGenerateArticle(trend.trend_id);
                    }}
                    disabled={!!generatingArticle}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      generatingArticle === trend.trend_id
                        ? 'bg-[#2DD4BF]/50 cursor-not-allowed'
                        : 'bg-[#2DD4BF] hover:bg-[#2DD4BF]/90'
                    } text-white`}
                  >
                    {generatingArticle === trend.trend_id ? (
                      <span className="flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Generating...
                      </span>
                    ) : (
                      'Generate Article'
                    )}
                  </button>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </MainLayout>
  );
} 