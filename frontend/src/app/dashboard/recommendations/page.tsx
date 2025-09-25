'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { IconTrendingUp, IconStar } from '@tabler/icons-react';
import MainLayout from '@/components/layout/MainLayout';

interface Trend {
  _id: string;
  keyword: string;
  title: string;
  score: number;
  type: string;
  category: string;
  source: string;
  source_url: string;
  summary: string;
}

export default function Recommendations() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [recommendedTrends, setRecommendedTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generatingArticles, setGeneratingArticles] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/');
    }
  }, [status, router]);

  useEffect(() => {
    fetchRecommendedTrends();
  }, []);

  const fetchRecommendedTrends = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/recommended-topics');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Fetched recommended trends:', data);
      setRecommendedTrends(data.recommended || []);
    } catch (error) {
      console.error('Error fetching recommended trends:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch recommendations');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateArticle = async (trend: Trend) => {
    if (!trend._id) {
      console.error('Invalid trend ID');
      alert('Invalid trend ID. Please try again.');
      return;
    }

    try {
      setGeneratingArticles(prev => new Set([...prev, trend._id]));
      
      const response = await fetch(`http://localhost:8000/approve_trend/${trend._id}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      router.push(`/dashboard/articles/${result.article?._id || result._id}`);
    } catch (error) {
      console.error('Error generating article:', error);
      alert('Failed to generate article. Please try again.');
    } finally {
      setGeneratingArticles(prev => {
        const newSet = new Set(prev);
        newSet.delete(trend._id);
        return newSet;
      });
    }
  };

  return (
    <MainLayout>
      <div className="p-8">
        {/* Header with Stats */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <IconStar className="w-8 h-8 text-[#2DD4BF]" />
            <h1 className="text-3xl font-bold text-white">Top Recommended Trends</h1>
          </div>
          <p className="text-gray-400">
            Here are the highest-scoring trends curated just for you. These topics are trending and likely to engage your readers.
          </p>
        </div>

        {/* Stats Card */}
        <div className="bg-[#1E293B] p-6 rounded-xl mb-8">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-[#2DD4BF]/10 rounded-lg">
              <IconTrendingUp className="w-6 h-6 text-[#2DD4BF]" />
            </div>
            <div>
              <h3 className="text-sm text-gray-400">Recommended Trends</h3>
              <p className="text-2xl font-semibold text-white">{recommendedTrends.length}</p>
            </div>
          </div>
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
          ) : recommendedTrends.length === 0 ? (
            <div className="col-span-full text-center py-12 text-gray-400">
              No recommended trends available at the moment.
            </div>
          ) : (
            recommendedTrends.map((trend) => (
              <motion.div
                key={trend._id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-[#1E293B] p-6 rounded-xl hover:bg-gray-800/50 transition-colors cursor-pointer group"
                onClick={() => router.push(`/dashboard/trend/${trend._id}`)}
              >
                <div className="flex justify-between items-start mb-4">
                  <span className="px-3 py-1 text-xs font-medium bg-[#2DD4BF]/10 text-[#2DD4BF] rounded-full">
                    {trend.category?.charAt(0).toUpperCase() + trend.category?.slice(1) || 'Uncategorized'}
                  </span>
                  <span className="text-sm text-gray-400">
                    Score: {trend.score?.toFixed(2) || 'N/A'}
                  </span>
                </div>
                <h3 className="text-lg font-semibold mb-3 text-white group-hover:text-[#2DD4BF] transition-colors">
                  {trend.title || generateDetailedTitle(trend)}
                </h3>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">
                    Source: {trend.source || 'Unknown'}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleGenerateArticle(trend);
                    }}
                    disabled={generatingArticles.has(trend._id)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      generatingArticles.has(trend._id)
                        ? 'bg-[#2DD4BF]/50 cursor-not-allowed'
                        : 'bg-[#2DD4BF] hover:bg-[#2DD4BF]/90'
                    } text-white`}
                  >
                    {generatingArticles.has(trend._id) ? (
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

function generateDetailedTitle(trend: any) {
  return `Latest Updates on ${trend.keyword} in ${trend.category || 'General'}`;
} 