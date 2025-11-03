'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { IconArrowLeft, IconFileText, IconCalendar, IconChartBar } from '@tabler/icons-react';
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
  visuals?: Array<{
    image_id: string;
    image_type: 'header' | 'inline';
    image_data: string;
    caption: string;
    style: 'realistic' | 'artistic';
  }>;
  visual_generation_metadata?: {
    generated: boolean;
    total_images: number;
    generation_time: number;
  };
  seo_optimization?: {
    optimized_title: string;
    meta_description: string;
    optimized_content: string;
    keywords: {
      primary: string[];
      secondary: string[];
      long_tail: string[];
    };
    intent: string;
    readability: {
      flesch: number;
      grade: number;
      gunning_fog: number;
    };
    structure: {
      paragraphs: number;
      avg_sentences_per_para: number;
      avg_sentence_length: number;
    };
    seo_score: number;
    slug: string;
    optimized_at: string;
    processing_time: number;
  };
  seo_optimized?: boolean;
}

export default function ArticleAnalysis({ params }: { params: { articleId: string } }) {
  const router = useRouter();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [seoExpanded, setSeoExpanded] = useState(true);

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

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-500/20 text-green-400';
    if (score >= 60) return 'bg-yellow-500/20 text-yellow-400';
    if (score >= 40) return 'bg-orange-500/20 text-orange-400';
    return 'bg-red-500/20 text-red-400';
  };

  return (
    <MainLayout>
      <div className="p-8">
        {/* Back Button */}
        <button
          onClick={() => router.push(`/dashboard/articles/${params.articleId}`)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#1E293B] text-gray-400 hover:bg-gray-800 transition-colors mb-8"
        >
          <IconArrowLeft size={20} />
          Back to Original Article
        </button>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#2DD4BF]"></div>
          </div>
        ) : error ? (
          <div className="text-center py-12 text-red-400">
            {error}
          </div>
        ) : article && article.seo_optimized && article.seo_optimization ? (
          <div className="max-w-4xl mx-auto">
            {/* Page Header */}
            <div className="mb-8">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 bg-[#2DD4BF]/20 rounded-lg flex items-center justify-center">
                  <IconChartBar className="text-[#2DD4BF]" size={20} />
                </div>
                <h1 className="text-3xl font-bold text-white">Article Analysis</h1>
              </div>
              <div className="flex items-center gap-2 mb-4">
                <span className="px-3 py-1 text-sm font-medium bg-[#2DD4BF]/10 text-[#2DD4BF] rounded-full">
                  {article.trend_details.category.charAt(0).toUpperCase() + 
                   article.trend_details.category.slice(1)}
                </span>
                <span className="text-gray-400">•</span>
                <span className="text-gray-400">{article.metadata.word_count} words</span>
                <span className="text-gray-400">•</span>
                <span className="text-gray-400">{formatDate(article.metadata.generated_timestamp)}</span>
              </div>
            </div>

            {/* SEO Optimization Section */}
            <div className="bg-[#1E293B] rounded-xl p-6 mb-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-[#2DD4BF]/20 rounded-lg flex items-center justify-center">
                    <span className="text-[#2DD4BF] text-sm font-bold">SEO</span>
                  </div>
                  <h2 className="text-xl font-semibold text-white">SEO Optimization</h2>
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreBgColor(article.seo_optimization.seo_score)}`}>
                    Score: {article.seo_optimization.seo_score}/100
                  </div>
                </div>
                <button
                  onClick={() => setSeoExpanded(!seoExpanded)}
                  className="px-4 py-2 bg-[#2DD4BF]/20 hover:bg-[#2DD4BF]/30 text-[#2DD4BF] rounded-lg text-sm transition-colors"
                >
                  {seoExpanded ? 'Hide Details' : 'Show Details'}
                </button>
              </div>

              {/* SEO Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Readability</div>
                  <div className={`text-lg font-semibold ${getScoreColor(article.seo_optimization.readability.flesch)}`}>
                    {article.seo_optimization.readability.flesch.toFixed(0)}/100
                  </div>
                  <div className="text-xs text-gray-500">
                    Grade {article.seo_optimization.readability.grade.toFixed(1)}
                  </div>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Keywords</div>
                  <div className="text-lg font-semibold text-white">
                    {article.seo_optimization.keywords.primary.length + 
                     article.seo_optimization.keywords.secondary.length}
                  </div>
                  <div className="text-xs text-gray-500">
                    {article.seo_optimization.keywords.primary.length} primary
                  </div>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Structure</div>
                  <div className="text-lg font-semibold text-white">
                    {article.seo_optimization.structure.paragraphs}
                  </div>
                  <div className="text-xs text-gray-500">
                    paragraphs
                  </div>
                </div>
              </div>

              {/* SEO Details (Expandable) */}
              {seoExpanded && (
                <div className="space-y-4">
                  {/* Keywords */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-300 mb-2">Keywords</h3>
                    <div className="space-y-2">
                      <div>
                        <span className="text-xs text-gray-400">Primary: </span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {article.seo_optimization.keywords.primary.map((keyword, index) => (
                            <span key={index} className="px-2 py-1 bg-[#2DD4BF]/20 text-[#2DD4BF] rounded text-xs">
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <span className="text-xs text-gray-400">Secondary: </span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {article.seo_optimization.keywords.secondary.map((keyword, index) => (
                            <span key={index} className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Meta Description */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-300 mb-2">Meta Description</h3>
                    <p className="text-sm text-gray-400 bg-gray-800/50 p-3 rounded-lg">
                      {article.seo_optimization.meta_description}
                    </p>
                  </div>

                  {/* Intent */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-300 mb-2">Content Intent</h3>
                    <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm">
                      {article.seo_optimization.intent}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Optimized Article Content */}
            <div className="bg-[#1E293B] rounded-xl p-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">SEO Optimized Article</h2>
                <div className="text-sm text-gray-400">
                  Optimized on {formatDate(article.seo_optimization.optimized_at)}
                </div>
              </div>
              
              <div className="prose prose-invert max-w-none">
                <div className="text-gray-300 whitespace-pre-wrap">
                  {article.seo_optimization.optimized_content}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-400">
            <div className="mb-4">
              <IconChartBar size={48} className="mx-auto text-gray-600" />
            </div>
            <h2 className="text-xl font-semibold mb-2">No SEO Analysis Available</h2>
            <p className="text-gray-500 mb-4">This article hasn't been optimized for SEO yet.</p>
            <button
              onClick={() => router.push(`/dashboard/articles/${params.articleId}`)}
              className="px-4 py-2 bg-[#2DD4BF]/20 hover:bg-[#2DD4BF]/30 text-[#2DD4BF] rounded-lg transition-colors"
            >
              View Original Article
            </button>
          </div>
        )}
      </div>
    </MainLayout>
  );
}





