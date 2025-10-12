'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { IconArrowLeft, IconMicrophone, IconFileText, IconQuote, IconBulb, IconClock, IconCheck, IconX } from '@tabler/icons-react';
import MainLayout from '@/components/layout/MainLayout';
// Switch between real and mock API
const USE_MOCK_API = process.env.NODE_ENV === 'development' && process.env.NEXT_PUBLIC_USE_MOCK_API === 'true';

// Import both APIs
import { getTranscript as getTranscriptMock, getQuotes as getQuotesMock, getSummary as getSummaryMock, Transcript, Quotes, Summary } from '@/lib/module9-api-mock';
import { getTranscript as getTranscriptReal, getQuotes as getQuotesReal, getSummary as getSummaryReal } from '@/lib/module9-api';

// Use the appropriate API based on environment
const getTranscript = USE_MOCK_API ? getTranscriptMock : getTranscriptReal;
const getQuotes = USE_MOCK_API ? getQuotesMock : getQuotesReal;
const getSummary = USE_MOCK_API ? getSummaryMock : getSummaryReal;

interface InterviewData {
  transcript: Transcript | null;
  quotes: Quotes | null;
  summary: Summary | null;
}

export default function InterviewDetail({ params }: { params: { id: string } }) {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [interviewData, setInterviewData] = useState<InterviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'transcript' | 'quotes' | 'summary'>('transcript');
  const [selectedSpeaker, setSelectedSpeaker] = useState<string>('all');

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/');
    }
  }, [status, router]);

  useEffect(() => {
    if (params.id) {
      fetchInterviewData();
    }
  }, [params.id]);

  const fetchInterviewData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all data in parallel
      const [transcript, quotes, summary] = await Promise.allSettled([
        getTranscript(params.id),
        getQuotes(params.id),
        getSummary(params.id)
      ]);

      const transcriptData = transcript.status === 'fulfilled' ? transcript.value : null;
      const quotesData = quotes.status === 'fulfilled' ? quotes.value : null;
      const summaryData = summary.status === 'fulfilled' ? summary.value : null;

      if (!transcriptData) {
        throw new Error('Interview data not found');
      }

      setInterviewData({
        transcript: transcriptData,
        quotes: quotesData,
        summary: summaryData
      });
    } catch (error) {
      console.error('Error fetching interview data:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch interview data');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getSpeakers = () => {
    if (!interviewData?.transcript?.segments) return [];
    const speakers = new Set(interviewData.transcript.segments.map(seg => seg.speaker));
    return Array.from(speakers).sort();
  };

  const getFilteredSegments = () => {
    if (!interviewData?.transcript?.segments) return [];
    if (selectedSpeaker === 'all') return interviewData.transcript.segments;
    return interviewData.transcript.segments.filter(seg => seg.speaker === selectedSpeaker);
  };

  const getClaimColor = (claim: number, confidence: number) => {
    if (claim === 1) {
      if (confidence > 0.8) return 'bg-red-500/20 text-red-400 border-red-500/30';
      if (confidence > 0.6) return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    }
    return 'bg-green-500/20 text-green-400 border-green-500/30';
  };

  if (status === 'loading' || !session) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#2DD4BF]"></div>
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="p-8">
          <div className="text-center py-12">
            <div className="text-red-400 mb-4">{error}</div>
            <button
              onClick={() => router.push('/dashboard/interview')}
              className="px-4 py-2 bg-[#2DD4BF] text-white rounded-lg hover:bg-[#2DD4BF]/90 transition-colors"
            >
              Back to Interviews
            </button>
          </div>
        </div>
      </MainLayout>
    );
  }

  const speakers = getSpeakers();
  const filteredSegments = getFilteredSegments();

  return (
    <MainLayout>
      <div className="p-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => router.push('/dashboard/interview')}
            className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
          >
            <IconArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-white">Interview Analysis</h1>
            <p className="text-gray-400">Detailed analysis and insights from your interview</p>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-[#1E293B] p-6 rounded-xl">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-[#2DD4BF]/10 rounded-lg">
                <IconMicrophone className="w-6 h-6 text-[#2DD4BF]" />
              </div>
              <div>
                <h3 className="text-sm text-gray-400">Duration</h3>
                <p className="text-2xl font-semibold text-white">
                  {interviewData?.transcript?.segments?.length 
                    ? formatTime(Math.max(...interviewData.transcript.segments.map(s => s.end)))
                    : '0:00'
                  }
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-[#1E293B] p-6 rounded-xl">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-[#2DD4BF]/10 rounded-lg">
                <IconFileText className="w-6 h-6 text-[#2DD4BF]" />
              </div>
              <div>
                <h3 className="text-sm text-gray-400">Segments</h3>
                <p className="text-2xl font-semibold text-white">
                  {interviewData?.transcript?.segments?.length || 0}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-[#1E293B] p-6 rounded-xl">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-[#2DD4BF]/10 rounded-lg">
                <IconQuote className="w-6 h-6 text-[#2DD4BF]" />
              </div>
              <div>
                <h3 className="text-sm text-gray-400">Key Quotes</h3>
                <p className="text-2xl font-semibold text-white">
                  {interviewData?.quotes?.quotes?.length || 0}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-[#1E293B] p-6 rounded-xl">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-[#2DD4BF]/10 rounded-lg">
                <IconBulb className="w-6 h-6 text-[#2DD4BF]" />
              </div>
              <div>
                <h3 className="text-sm text-gray-400">Story Angles</h3>
                <p className="text-2xl font-semibold text-white">
                  {interviewData?.summary?.angles?.length || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-8">
          {[
            { id: 'transcript', label: 'Transcript', icon: IconFileText },
            { id: 'quotes', label: 'Key Quotes', icon: IconQuote },
            { id: 'summary', label: 'Summary & Angles', icon: IconBulb }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-[#2DD4BF] text-white'
                    : 'bg-[#1E293B] text-gray-400 hover:bg-gray-800'
                }`}
              >
                <Icon className="w-5 h-5" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="bg-[#1E293B] rounded-xl p-6">
          {activeTab === 'transcript' && (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">Transcript</h2>
                {speakers.length > 1 && (
                  <div className="flex gap-2">
                    <select
                      value={selectedSpeaker}
                      onChange={(e) => setSelectedSpeaker(e.target.value)}
                      className="px-4 py-2 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-[#2DD4BF] focus:outline-none"
                    >
                      <option value="all">All Speakers</option>
                      {speakers.map(speaker => (
                        <option key={speaker} value={speaker}>{speaker}</option>
                      ))}
                    </select>
                  </div>
                )}
              </div>

              <div className="space-y-4 max-h-96 overflow-y-auto">
                {filteredSegments.map((segment, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 bg-gray-800/50 rounded-lg"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-[#2DD4BF]/20 rounded-full flex items-center justify-center">
                          <span className="text-xs font-medium text-[#2DD4BF]">
                            {segment.speaker.replace('SPEAKER_', '')}
                          </span>
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-sm text-gray-400">
                            {formatTime(segment.start)} - {formatTime(segment.end)}
                          </span>
                        </div>
                        <p className="text-white leading-relaxed">{segment.text}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'quotes' && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-6">Key Quotes</h2>
              {interviewData?.quotes?.quotes?.length ? (
                <div className="space-y-4">
                  {interviewData.quotes.quotes.map((quote, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-6 bg-gray-800/50 rounded-lg border-l-4 border-[#2DD4BF]"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-400">
                            {formatTime(quote.start)} - {formatTime(quote.end)}
                          </span>
                        </div>
                      </div>
                      <blockquote className="text-lg text-white italic mb-3">
                        "{quote.text}"
                      </blockquote>
                      {quote.context && (
                        <p className="text-sm text-gray-400">
                          <span className="font-medium">Context:</span> {quote.context}
                        </p>
                      )}
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-400">
                  <IconQuote className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>No key quotes found for this interview.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'summary' && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-6">Summary & Story Angles</h2>
              
              {interviewData?.summary?.summary && (
                <div className="mb-8">
                  <h3 className="text-lg font-medium text-white mb-4">Summary</h3>
                  <div className="p-6 bg-gray-800/50 rounded-lg">
                    <p className="text-gray-300 leading-relaxed">
                      {interviewData.summary.summary}
                    </p>
                  </div>
                </div>
              )}

              {interviewData?.summary?.angles?.length > 0 && (
                <div>
                  <h3 className="text-lg font-medium text-white mb-4">Story Angles</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {interviewData.summary.angles.map((angle, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="p-4 bg-gray-800/50 rounded-lg border border-[#2DD4BF]/20"
                      >
                        <div className="flex items-start gap-3">
                          <div className="w-6 h-6 bg-[#2DD4BF]/20 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                            <span className="text-xs font-medium text-[#2DD4BF]">
                              {index + 1}
                            </span>
                          </div>
                          <p className="text-gray-300">{angle}</p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}

              {!interviewData?.summary?.summary && !interviewData?.summary?.angles?.length && (
                <div className="text-center py-12 text-gray-400">
                  <IconBulb className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>No summary or story angles available for this interview.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
