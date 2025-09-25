'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';

interface TrendDetail {
  trend_id: string;
  keyword: string;
  title: string;
  score: number;
  type: string;
  category: string;
  source: string;
  summary: string;
  source_link: string;
  source_name: string;
  published: string;
}

export default function TrendDetail({ params }: { params: { trendId: string } }) {
  const [trendDetail, setTrendDetail] = useState<TrendDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetchTrendDetail();
  }, [params.trendId]);

  const fetchTrendDetail = async () => {
    try {
      const response = await fetch(`/api/trends/${params.trendId}`);
      const data = await response.json();
      setTrendDetail(data);
    } catch (error) {
      console.error('Error fetching trend detail:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateArticle = async () => {
    try {
      const response = await fetch(`/approve_trend/${params.trendId}`, {
        method: 'POST',
      });
      
      if (response.ok) {
        router.push('/dashboard/articles');
      }
    } catch (error) {
      console.error('Error generating article:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-aurora-primary"></div>
      </div>
    );
  }

  if (!trendDetail) {
    return (
      <div className="p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Trend not found</h1>
          <Link href="/dashboard/trend-analysis" className="text-aurora-primary hover:underline">
            Back to Trend Analysis
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <Link 
          href="/dashboard/trend-analysis"
          className="text-aurora-text-secondary hover:text-aurora-primary transition-colors"
        >
          ← Back to Trend Analysis
        </Link>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-aurora-card rounded-lg p-6"
      >
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white mb-2">{trendDetail.title}</h1>
          <div className="flex flex-wrap gap-2 mb-4">
            <span className="px-3 py-1 rounded-full bg-aurora-secondary text-aurora-text-secondary text-sm">
              {trendDetail.category}
            </span>
            <span className="px-3 py-1 rounded-full bg-aurora-background text-aurora-text-secondary text-sm">
              Score: {trendDetail.score.toFixed(1)}
            </span>
            <span className="px-3 py-1 rounded-full bg-aurora-background text-aurora-text-secondary text-sm">
              Source: {trendDetail.source}
            </span>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-lg font-semibold text-white mb-3">Summary</h2>
          <p className="text-aurora-text-secondary leading-relaxed">
            {trendDetail.summary}
          </p>
        </div>

        <div className="mb-8">
          <h2 className="text-lg font-semibold text-white mb-3">Source</h2>
          {trendDetail.source_link ? (
            <a
              href={trendDetail.source_link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-aurora-primary hover:underline"
            >
              {trendDetail.source_name} (Published: {new Date(trendDetail.published).toLocaleDateString()})
            </a>
          ) : (
            <p className="text-aurora-text-secondary">No source link available</p>
          )}
        </div>

        <div className="flex justify-end">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleGenerateArticle}
            className="px-6 py-3 bg-aurora-primary text-white rounded-lg hover:bg-aurora-primary/90 transition-colors"
          >
            Generate Article
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
} 