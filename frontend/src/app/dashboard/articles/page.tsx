'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { IconArrowLeft, IconFileText, IconTrash, IconEye } from '@tabler/icons-react';
import MainLayout from '@/components/layout/MainLayout';

interface Article {
  _id: string;
  title: string;
  content: string;
  summary: string;
  metadata: {
    word_count: number;
    generated_timestamp: string;
  };
  trend_details: {
    category: string;
    source: string;
  };
}

export default function MyArticles() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingArticles, setDeletingArticles] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/');
    }
  }, [status, router]);

  useEffect(() => {
    fetchArticles();
  }, []);

  const fetchArticles = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/articles');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Fetched articles:', data);
      setArticles(data.articles || []);
    } catch (error) {
      console.error('Error fetching articles:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch articles');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (articleId: string) => {
    try {
      setDeletingArticles(prev => new Set([...prev, articleId]));
      const response = await fetch(`http://localhost:8000/api/articles/${articleId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete article');
      }

      // Remove the article from the list
      setArticles(prev => prev.filter(article => article._id !== articleId));
    } catch (err) {
      console.error('Error deleting article:', err);
      setError('Failed to delete article');
    } finally {
      setDeletingArticles(prev => {
        const newSet = new Set(prev);
        newSet.delete(articleId);
        return newSet;
      });
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      hour12: true
    });
  };

  const handleArticleClick = (articleId: string) => {
    router.push(`/dashboard/articles/${articleId}`);
  };

  return (
    <MainLayout>
      <div className="p-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2 text-white">My Articles</h1>
            <p className="text-gray-400">View and manage your generated articles</p>
          </div>
          <button
            onClick={() => router.push('/dashboard')}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#1E293B] text-gray-400 hover:bg-gray-800 transition-colors"
          >
            <IconArrowLeft size={20} />
            Back to Dashboard
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#2DD4BF]"></div>
          </div>
        ) : error ? (
          <div className="text-center py-12 text-red-400">
            {error}
          </div>
        ) : articles.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            No articles generated yet. Go to the dashboard to generate articles from trending topics.
          </div>
        ) : (
          <div className="space-y-4">
            {articles.map((article) => (
              <motion.div
                key={article._id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-[#1E293B] p-6 rounded-xl hover:bg-gray-800/50 transition-colors cursor-pointer"
                onClick={() => handleArticleClick(article._id)}
              >
                <div className="flex justify-between items-start mb-4">
                  <span className="px-3 py-1 text-xs font-medium bg-[#2DD4BF]/10 text-[#2DD4BF] rounded-full">
                    {article.trend_details.category.charAt(0).toUpperCase() + 
                     article.trend_details.category.slice(1)}
                  </span>
                  <span className="text-sm text-gray-400">
                    {article.metadata.word_count} words
                  </span>
                </div>
                <h3 className="text-xl font-semibold mb-3 text-white group-hover:text-[#2DD4BF] transition-colors">
                  {article.title}
                </h3>
                <p className="text-gray-400 mb-4 line-clamp-2">
                  {article.summary}
                </p>
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    <IconFileText size={16} />
                    Source: {article.trend_details.source}
                  </div>
                  <span className="text-sm text-gray-400">
                    {formatDate(article.metadata.generated_timestamp)}
                  </span>
                </div>
                <div className="flex space-x-2 mt-4">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleArticleClick(article._id);
                    }}
                    className="p-2 text-gray-400 hover:text-[#2DD4BF] rounded-full hover:bg-gray-800 transition-colors"
                    title="View Article"
                  >
                    <IconEye className="w-5 h-5" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(article._id);
                    }}
                    disabled={deletingArticles.has(article._id)}
                    className={`p-2 text-red-400 hover:text-red-500 rounded-full hover:bg-gray-800 transition-colors ${
                      deletingArticles.has(article._id) ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                    title="Delete Article"
                  >
                    <IconTrash className="w-5 h-5" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
} 