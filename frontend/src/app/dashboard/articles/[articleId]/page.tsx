'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { IconArrowLeft, IconFileText, IconCalendar } from '@tabler/icons-react';
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
    keyword: string;
    category: string;
    source: string;
  };
}

export default function ArticleDetail({ params }: { params: { articleId: string } }) {
  const router = useRouter();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchArticle();
  }, [params.articleId]);

  const fetchArticle = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/articles/${params.articleId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setArticle(data);
    } catch (error) {
      console.error('Error fetching article:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch article');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      hour12: true
    });
  };

  return (
    <MainLayout>
      <div className="p-8">
        {/* Back Button */}
        <button
          onClick={() => router.push('/dashboard/articles')}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#1E293B] text-gray-400 hover:bg-gray-800 transition-colors mb-8"
        >
          <IconArrowLeft size={20} />
          Back to Articles
        </button>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#2DD4BF]"></div>
          </div>
        ) : error ? (
          <div className="text-center py-12 text-red-400">
            {error}
          </div>
        ) : article ? (
          <div className="max-w-4xl mx-auto">
            {/* Article Header */}
            <div className="mb-8">
              <div className="flex items-center gap-2 mb-4">
                <span className="px-3 py-1 text-sm font-medium bg-[#2DD4BF]/10 text-[#2DD4BF] rounded-full">
                  {article.trend_details.category.charAt(0).toUpperCase() + 
                   article.trend_details.category.slice(1)}
                </span>
                <span className="text-gray-400">•</span>
                <span className="text-gray-400">{article.metadata.word_count} words</span>
              </div>
              <h1 className="text-3xl font-bold mb-4 text-white">{article.title}</h1>
              <div className="flex items-center gap-4 text-gray-400">
                <div className="flex items-center gap-2">
                  <IconFileText size={16} />
                  <span>Source: {article.trend_details.source}</span>
                </div>
                <div className="flex items-center gap-2">
                  <IconCalendar size={16} />
                  <span>{formatDate(article.metadata.generated_timestamp)}</span>
                </div>
              </div>
            </div>

            {/* Article Content */}
            <div className="bg-[#1E293B] rounded-xl p-8">
              <div className="prose prose-invert max-w-none">
                <div className="text-gray-300 mb-8 text-lg font-medium">
                  {article.summary}
                </div>
                <div className="text-gray-300 whitespace-pre-wrap">
                  {article.content}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-400">
            Article not found
          </div>
        )}
      </div>
    </MainLayout>
  );
} 