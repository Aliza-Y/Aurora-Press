'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { IconArrowLeft, IconFileText, IconCalendar, IconChartBar, IconShare, IconLoader } from '@tabler/icons-react';
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

export default function ArticleDetail({ params }: { params: { articleId: string } }) {
  const router = useRouter();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [publishing, setPublishing] = useState<string | null>(null);
  const [publishStatus, setPublishStatus] = useState<{[key: string]: string}>({});
  const [publishedUrls, setPublishedUrls] = useState<{[key: string]: string}>({});

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

  const publishToPlatform = async (platform: string) => {
    if (!article) return;
    
    setPublishing(platform);
    setPublishStatus(prev => ({ ...prev, [platform]: 'publishing' }));
    
    try {
      const response = await fetch(`http://localhost:8000/api/publishing/publish/${params.articleId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'default_user',
          target_platforms: [platform]
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log(`📊 Publishing response for ${platform}:`, result);
        
        // Check if this is a task start response or final result
        if (result.task_id) {
          // This is a task start response, wait for completion
          console.log(`⏳ Task started, waiting for completion: ${result.task_id}`);
          
          // Poll for task completion
          const pollForResult = async () => {
            try {
              const statusResponse = await fetch(`http://localhost:8000/api/publishing/task/${result.task_id}/status`);
              if (statusResponse.ok) {
                const taskResult = await statusResponse.json();
                console.log(`📊 Task status for ${platform}:`, taskResult);
                
                if (taskResult.state === 'SUCCESS') {
                  // Task completed successfully
                  const finalResult = taskResult.result;
                  if (finalResult && finalResult.overall_success) {
                    setPublishStatus(prev => ({ ...prev, [platform]: 'success' }));
                    
                    // Store published URLs for display
                    if (finalResult.platforms && finalResult.platforms[platform]) {
                      const platformResult = finalResult.platforms[platform];
                      if (platformResult.success && platformResult.tweet_url) {
                        setPublishedUrls(prev => ({ ...prev, [platform]: platformResult.tweet_url }));
                      } else if (platformResult.success && platformResult.post_url) {
                        setPublishedUrls(prev => ({ ...prev, [platform]: platformResult.post_url }));
                      }
                    }
                    
                    console.log(`✅ Published to ${platform}:`, finalResult);
                  } else {
                    setPublishStatus(prev => ({ ...prev, [platform]: 'error' }));
                    console.log(`❌ Publishing to ${platform} failed:`, finalResult);
                  }
                } else if (taskResult.state === 'FAILURE') {
                  setPublishStatus(prev => ({ ...prev, [platform]: 'error' }));
                  console.log(`❌ Publishing to ${platform} failed:`, taskResult);
                } else {
                  // Still processing, wait and try again
                  setTimeout(pollForResult, 1000);
                  return;
                }
              }
            } catch (error) {
              console.error(`❌ Error checking task status:`, error);
              setPublishStatus(prev => ({ ...prev, [platform]: 'error' }));
            }
          };
          
          // Start polling
          pollForResult();
        } else {
          // This is a direct result (fallback)
          const isOverallSuccess = result.success || result.overall_success;
          const platformSuccess = result.platforms && result.platforms[platform] && result.platforms[platform].success;
          
          if (isOverallSuccess || platformSuccess) {
            setPublishStatus(prev => ({ ...prev, [platform]: 'success' }));
            
            // Store published URLs for display
            if (result.platforms && result.platforms[platform]) {
              const platformResult = result.platforms[platform];
              if (platformResult.success && platformResult.tweet_url) {
                setPublishedUrls(prev => ({ ...prev, [platform]: platformResult.tweet_url }));
              } else if (platformResult.success && platformResult.post_url) {
                setPublishedUrls(prev => ({ ...prev, [platform]: platformResult.post_url }));
              }
            }
            
            console.log(`✅ Published to ${platform}:`, result);
          } else {
            setPublishStatus(prev => ({ ...prev, [platform]: 'error' }));
            console.log(`❌ Publishing to ${platform} failed:`, result);
          }
        }
      } else {
        throw new Error(`Failed to publish to ${platform}`);
      }
    } catch (error) {
      console.error(`❌ Error publishing to ${platform}:`, error);
      setPublishStatus(prev => ({ ...prev, [platform]: 'error' }));
    } finally {
      setPublishing(null);
    }
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
                {/* Header Image */}
                {article.visuals && article.visuals.find(v => v.image_type === 'header') && (
                  <div className="mb-8">
                    {(() => {
                      const headerImage = article.visuals!.find(v => v.image_type === 'header');
                      return headerImage ? (
                        <div className="relative">
                          <img
                            src={headerImage.image_data}
                            alt={headerImage.caption}
                            className="w-full h-64 md:h-80 object-cover rounded-lg shadow-lg"
                          />
                          <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-60 text-white p-4 rounded-b-lg">
                            <p className="text-sm italic">{headerImage.caption}</p>
                          </div>
                        </div>
                      ) : null;
                    })()}
                  </div>
                )}

                <div className="text-gray-300 mb-8 text-lg font-medium">
                  {article.summary}
                </div>
                
                {/* Article Content with Inline Images */}
                <div className="text-gray-300 whitespace-pre-wrap">
                  {article.visuals && article.visuals.find(v => v.image_type === 'inline') ? (
                    (() => {
                      const inlineImage = article.visuals!.find(v => v.image_type === 'inline');
                      const contentParts = article.content.split('\n\n');
                      const midPoint = Math.floor(contentParts.length / 2);
                      
                      return (
                        <>
                          {contentParts.slice(0, midPoint).join('\n\n')}
                          
                          {/* Inline Image */}
                          {inlineImage && (
                            <div className="my-8 flex justify-center">
                              <div className="max-w-md">
                                <img
                                  src={inlineImage.image_data}
                                  alt={inlineImage.caption}
                                  className="w-full rounded-lg shadow-lg"
                                />
                                <p className="text-sm text-gray-400 italic mt-2 text-center">
                                  {inlineImage.caption}
                                </p>
                              </div>
                            </div>
                          )}
                          
                          {contentParts.slice(midPoint).join('\n\n')}
                        </>
                      );
                    })()
                  ) : (
                    article.content
                  )}
                </div>
              </div>
            </div>

            {/* SEO Analysis Button */}
            {article.seo_optimized && article.seo_optimization && (
              <div className="mt-8">
                <div className="bg-[#1E293B] rounded-xl p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-[#2DD4BF]/20 rounded-lg flex items-center justify-center">
                        <span className="text-[#2DD4BF] text-sm font-bold">SEO</span>
                      </div>
                      <div>
                        <h2 className="text-lg font-semibold text-white">SEO Analysis Available</h2>
                        <p className="text-sm text-gray-400">This article has been optimized for SEO</p>
                      </div>
                      <div className="px-3 py-1 bg-[#2DD4BF]/10 text-[#2DD4BF] rounded-full text-sm font-medium">
                        Score: {article.seo_optimization.seo_score}/100
                      </div>
                    </div>
                    <button
                      onClick={() => router.push(`/dashboard/articles/${params.articleId}/seo`)}
                      className="px-6 py-3 bg-[#2DD4BF]/20 hover:bg-[#2DD4BF]/30 text-[#2DD4BF] rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                    >
                      <IconChartBar size={16} />
                      View Article Analysis
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Publishing Section */}
            <div className="mt-8">
              <div className="bg-[#1E293B] rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                      <span className="text-blue-400 text-sm font-bold">📢</span>
                    </div>
                    <div>
                      <h2 className="text-lg font-semibold text-white">Publish Article</h2>
                      <p className="text-sm text-gray-400">Share this article on social media platforms</p>
                    </div>
                  </div>
                </div>

                {/* Publishing Status Messages */}
                {publishing && (
                  <div className="mb-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                    <div className="flex items-center gap-3">
                      <IconLoader className="text-blue-400 animate-spin" size={20} />
                      <div>
                        <h3 className="text-blue-400 font-medium">Publishing to {publishing}...</h3>
                        <p className="text-blue-300 text-sm">Please wait while we publish your article</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Success Messages */}
                {Object.keys(publishedUrls).length > 0 && (
                  <div className="mb-6 p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                    <h3 className="text-green-400 font-medium mb-2">✅ Successfully Published!</h3>
                    <div className="space-y-2">
                      {Object.entries(publishedUrls).map(([platform, url]) => (
                        <div key={platform} className="flex items-center gap-2">
                          <span className="text-green-400 text-sm font-medium capitalize">{platform}:</span>
                          <a 
                            href={url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:text-blue-300 text-sm underline"
                          >
                            {url}
                          </a>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button
                    onClick={() => publishToPlatform('twitter')}
                    disabled={publishing === 'twitter'}
                    className={`p-4 rounded-lg transition-colors text-left ${
                      publishStatus.twitter === 'success' 
                        ? 'bg-green-500/20 border border-green-500/30' 
                        : publishStatus.twitter === 'error'
                        ? 'bg-red-500/20 border border-red-500/30'
                        : 'bg-gray-800/50 hover:bg-gray-700'
                    } ${publishing === 'twitter' ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                        {publishing === 'twitter' ? (
                          <IconLoader className="text-blue-400 animate-spin" size={16} />
                        ) : publishStatus.twitter === 'success' ? (
                          <span className="text-green-400 text-sm">✅</span>
                        ) : publishStatus.twitter === 'error' ? (
                          <span className="text-red-400 text-sm">❌</span>
                        ) : (
                          <span className="text-blue-400 text-sm">🐦</span>
                        )}
                      </div>
                      <div>
                        <h3 className="font-medium text-white">Twitter</h3>
                        <p className="text-sm text-gray-400">
                          {publishing === 'twitter' ? 'Publishing...' : 
                           publishStatus.twitter === 'success' ? 'Published successfully' :
                           publishStatus.twitter === 'error' ? 'Publishing failed' :
                           'Share on Twitter'}
                        </p>
                      </div>
                    </div>
                  </button>
                  
                  <button
                    onClick={() => publishToPlatform('linkedin')}
                    disabled={publishing === 'linkedin'}
                    className={`p-4 rounded-lg transition-colors text-left ${
                      publishStatus.linkedin === 'success' 
                        ? 'bg-green-500/20 border border-green-500/30' 
                        : publishStatus.linkedin === 'error'
                        ? 'bg-red-500/20 border border-red-500/30'
                        : 'bg-gray-800/50 hover:bg-gray-700'
                    } ${publishing === 'linkedin' ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-blue-600/20 rounded-lg flex items-center justify-center">
                        {publishing === 'linkedin' ? (
                          <IconLoader className="text-blue-400 animate-spin" size={16} />
                        ) : publishStatus.linkedin === 'success' ? (
                          <span className="text-green-400 text-sm">✅</span>
                        ) : publishStatus.linkedin === 'error' ? (
                          <span className="text-red-400 text-sm">❌</span>
                        ) : (
                          <span className="text-blue-400 text-sm">💼</span>
                        )}
                      </div>
                      <div>
                        <h3 className="font-medium text-white">LinkedIn</h3>
                        <p className="text-sm text-gray-400">
                          {publishing === 'linkedin' ? 'Publishing...' : 
                           publishStatus.linkedin === 'success' ? 'Published successfully' :
                           publishStatus.linkedin === 'error' ? 'Publishing failed' :
                           'Share on LinkedIn'}
                        </p>
                      </div>
                    </div>
                  </button>
                  
                  <button
                    onClick={() => publishToPlatform('wordpress')}
                    disabled={publishing === 'wordpress'}
                    className={`p-4 rounded-lg transition-colors text-left ${
                      publishStatus.wordpress === 'success' 
                        ? 'bg-green-500/20 border border-green-500/30' 
                        : publishStatus.wordpress === 'error'
                        ? 'bg-red-500/20 border border-red-500/30'
                        : 'bg-gray-800/50 hover:bg-gray-700'
                    } ${publishing === 'wordpress' ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-gray-500/20 rounded-lg flex items-center justify-center">
                        {publishing === 'wordpress' ? (
                          <IconLoader className="text-gray-400 animate-spin" size={16} />
                        ) : publishStatus.wordpress === 'success' ? (
                          <span className="text-green-400 text-sm">✅</span>
                        ) : publishStatus.wordpress === 'error' ? (
                          <span className="text-red-400 text-sm">❌</span>
                        ) : (
                          <span className="text-gray-400 text-sm">🌐</span>
                        )}
                      </div>
                      <div>
                        <h3 className="font-medium text-white">WordPress</h3>
                        <p className="text-sm text-gray-400">
                          {publishing === 'wordpress' ? 'Publishing...' : 
                           publishStatus.wordpress === 'success' ? 'Published successfully' :
                           publishStatus.wordpress === 'error' ? 'Publishing failed' :
                           'Publish to WordPress'}
                        </p>
                      </div>
                    </div>
                  </button>
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