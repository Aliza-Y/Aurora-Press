'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import MainLayout from '@/components/layout/MainLayout';
import { IconArrowLeft } from '@tabler/icons-react';

interface Trend {
  trend_id: string;
  keyword: string;
  title: string;
  score: number;
  type: string;
  category: string;
  source: string;
  summary: string;
  source_url: string;
  publication_date?: string;
}

export default function TrendDetail({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [trend, setTrend] = useState<Trend | null>(null);
  const [loading, setLoading] = useState(true);
  const [generatingArticle, setGeneratingArticle] = useState(false);

  useEffect(() => {
    fetchTrendDetail();
  }, [params.id]);

  const fetchTrendDetail = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/trends/${params.id}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setTrend(data);
    } catch (error) {
      console.error('Error fetching trend detail:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatSourceDisplay = (source: string, source_url: string) => {
    try {
      // Extract domain from URL
      const domain = new URL(source_url).hostname.replace('www.', '');
      return `${source}/${domain}`;
    } catch (e) {
      return source;
    }
  };

  const handleGenerateArticle = async () => {
    if (!trend) return;
    
    try {
      setGeneratingArticle(true);
      const response = await fetch(`http://localhost:8000/approve_trend/${trend.trend_id}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      router.push(`/dashboard/articles/${result.article_id}`);
    } catch (error) {
      console.error('Error generating article:', error);
      alert('Failed to generate article. Please try again.');
    } finally {
      setGeneratingArticle(false);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#2DD4BF]"></div>
        </div>
      </MainLayout>
    );
  }

  if (!trend) {
    return (
      <MainLayout>
        <div className="p-8">
          <div className="text-center text-gray-400">Trend not found.</div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="p-8">
        {/* Back Button */}
        <Link 
          href="/dashboard" 
          className="inline-flex items-center text-gray-400 hover:text-white mb-6 transition-colors"
        >
          <IconArrowLeft className="mr-2" size={20} />
          Back to Dashboard
        </Link>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-[#1E293B] rounded-xl p-8"
        >
          {/* Header */}
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-2xl font-bold text-white mb-2">{trend.title}</h1>
              <div className="flex items-center gap-3">
                <span className="px-3 py-1 text-sm font-medium bg-[#2DD4BF]/10 text-[#2DD4BF] rounded-full">
                  {trend.category}
                </span>
                <span className="text-sm text-gray-400">
                  Score: {trend.score.toFixed(1)}
                </span>
              </div>
            </div>
            <button
              onClick={handleGenerateArticle}
              disabled={generatingArticle}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                generatingArticle
                  ? 'bg-[#2DD4BF]/50 cursor-not-allowed'
                  : 'bg-[#2DD4BF] hover:bg-[#2DD4BF]/90'
              } text-white`}
            >
              {generatingArticle ? (
                <span className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Generating...
                </span>
              ) : (
                'Generate Article'
              )}
            </button>
          </div>

          {/* Summary */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-white mb-2">Summary</h2>
            <p className="text-gray-400 leading-relaxed whitespace-pre-wrap">
              {trend.summary || "No summary available for this trend."}
            </p>
          </div>

          {/* Source */}
          <div>
            <h2 className="text-lg font-semibold text-white mb-2">Source</h2>
            <a
              href={trend.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#2DD4BF] hover:underline inline-block"
            >
              {formatSourceDisplay(trend.source, trend.source_url)}
              {trend.publication_date && ` (Published: ${new Date(trend.publication_date).toLocaleDateString()})`}
            </a>
          </div>
        </motion.div>
      </div>
    </MainLayout>
  );
} 