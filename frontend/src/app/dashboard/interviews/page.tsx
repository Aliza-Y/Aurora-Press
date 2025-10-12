'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { IconArrowLeft, IconClock, IconFileText, IconQuote, IconTrash, IconEye } from '@tabler/icons-react';

interface Interview {
  interview_id: string;
  title: string;
  created_at: string;
  status: string;
}

interface InterviewWithDetails extends Interview {
  transcript?: {
    segments: any[];
  };
  quotes?: {
    quotes: any[];
  };
  summary?: {
    summary: string;
    angles: string[];
  };
}

export default function InterviewsHistoryPage() {
  const router = useRouter();
  const [interviews, setInterviews] = useState<InterviewWithDetails[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedInterview, setSelectedInterview] = useState<InterviewWithDetails | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);

  useEffect(() => {
    fetchInterviews();
  }, []);

  const fetchInterviews = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/m9/interviews');
      if (!response.ok) {
        throw new Error('Failed to fetch interviews');
      }
      const data = await response.json();
      setInterviews(data.interviews || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch interviews');
    } finally {
      setLoading(false);
    }
  };

  const fetchInterviewDetails = async (interviewId: string) => {
    try {
      const [transcriptRes, quotesRes, summaryRes] = await Promise.all([
        fetch(`/api/m9/transcript?interview_id=${interviewId}`),
        fetch(`/api/m9/quotes?interview_id=${interviewId}`),
        fetch(`/api/m9/summary?interview_id=${interviewId}`)
      ]);

      const transcript = transcriptRes.ok ? await transcriptRes.json() : null;
      const quotes = quotesRes.ok ? await quotesRes.json() : null;
      const summary = summaryRes.ok ? await summaryRes.json() : null;

      return { transcript, quotes, summary };
    } catch (err) {
      console.error('Error fetching interview details:', err);
      return { transcript: null, quotes: null, summary: null };
    }
  };

  const handleViewInterview = async (interview: Interview) => {
    const details = await fetchInterviewDetails(interview.interview_id);
    setSelectedInterview({
      ...interview,
      ...details
    });
  };

  const handleDeleteClick = (interviewId: string) => {
    setShowDeleteConfirm(interviewId);
  };

  const handleDeleteConfirm = async () => {
    if (!showDeleteConfirm) return;

    try {
      setDeletingId(showDeleteConfirm);
      setError(null);
      setSuccessMessage(null);
      setShowDeleteConfirm(null);

      const response = await fetch(`/api/m9/interviews/${showDeleteConfirm}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        // Remove from local state immediately
        setInterviews(interviews.filter(i => i.interview_id !== showDeleteConfirm));
        if (selectedInterview?.interview_id === showDeleteConfirm) {
          setSelectedInterview(null);
        }
        
        setSuccessMessage('Interview deleted successfully');
        
        // Clear success message after 3 seconds
        setTimeout(() => setSuccessMessage(null), 3000);
        
        // Refresh the data to ensure consistency
        await fetchInterviews();
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Failed to delete interview (${response.status})`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete interview');
    } finally {
      setDeletingId(null);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteConfirm(null);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={() => router.back()}
                className="mr-4 p-2 text-gray-400 hover:text-white transition-colors"
              >
                <IconArrowLeft className="w-6 h-6" />
              </button>
              <div>
                <h1 className="text-3xl font-bold text-white">Interview History</h1>
                <p className="text-gray-400">View and manage your processed interviews</p>
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-900/20 border border-red-500/50 rounded-lg">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {successMessage && (
          <div className="mb-6 p-4 bg-green-900/20 border border-green-500/50 rounded-lg">
            <p className="text-green-400">{successMessage}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Interviews List */}
          <div className="bg-gray-800 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">All Interviews</h2>
            {interviews.length === 0 ? (
              <div className="text-center py-8">
                <IconFileText className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                <p className="text-gray-400">No interviews found</p>
              </div>
            ) : (
              <div className="space-y-3">
                {interviews.map((interview) => (
                  <div
                    key={interview.interview_id}
                    className="p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-white truncate">
                          {interview.title || 'Untitled Interview'}
                        </h3>
                        <div className="flex items-center text-sm text-gray-400 mt-1">
                          <IconClock className="w-4 h-4 mr-1" />
                          {formatDate(interview.created_at)}
                        </div>
                        <div className="flex items-center mt-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            interview.status === 'completed' 
                              ? 'bg-green-900/20 text-green-400' 
                              : 'bg-yellow-900/20 text-yellow-400'
                          }`}>
                            {interview.status}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2 ml-4">
                        <button
                          onClick={() => handleViewInterview(interview)}
                          className="p-2 text-gray-400 hover:text-blue-400 transition-colors"
                          title="View Details"
                        >
                          <IconEye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteClick(interview.interview_id)}
                          disabled={deletingId === interview.interview_id}
                          className={`p-2 transition-colors ${
                            deletingId === interview.interview_id
                              ? 'text-gray-600 cursor-not-allowed'
                              : 'text-gray-400 hover:text-red-400'
                          }`}
                          title={deletingId === interview.interview_id ? 'Deleting...' : 'Delete'}
                        >
                          {deletingId === interview.interview_id ? (
                            <div className="w-4 h-4 border-2 border-gray-600 border-t-transparent rounded-full animate-spin" />
                          ) : (
                            <IconTrash className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Interview Details */}
          <div className="bg-gray-800 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Interview Details</h2>
            {selectedInterview ? (
              <div className="space-y-6">
                {/* Basic Info */}
                <div>
                  <h3 className="font-medium text-white mb-2">Basic Information</h3>
                  <div className="bg-gray-700 rounded-lg p-4">
                    <p className="text-sm text-gray-300">
                      <span className="font-medium">Title:</span> {selectedInterview.title || 'Untitled Interview'}
                    </p>
                    <p className="text-sm text-gray-300 mt-1">
                      <span className="font-medium">Status:</span> {selectedInterview.status}
                    </p>
                    <p className="text-sm text-gray-300 mt-1">
                      <span className="font-medium">Created:</span> {formatDate(selectedInterview.created_at)}
                    </p>
                  </div>
                </div>

                {/* Summary */}
                {selectedInterview.summary?.summary && (
                  <div>
                    <h3 className="font-medium text-white mb-2">Summary</h3>
                    <div className="bg-gray-700 rounded-lg p-4">
                      <p className="text-sm text-gray-300">{selectedInterview.summary.summary}</p>
                    </div>
                  </div>
                )}

                {/* Quotes */}
                {selectedInterview.quotes?.quotes && selectedInterview.quotes.quotes.length > 0 && (
                  <div>
                    <h3 className="font-medium text-white mb-2">Key Quotes</h3>
                    <div className="space-y-2">
                      {selectedInterview.quotes.quotes.slice(0, 3).map((quote: any, index: number) => (
                        <div key={index} className="bg-gray-700 rounded-lg p-3">
                          <p className="text-sm text-gray-300">"{quote.text}"</p>
                          <p className="text-xs text-gray-500 mt-1">
                            {quote.speaker} • Confidence: {(quote.confidence * 100).toFixed(1)}%
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Transcript Stats */}
                {selectedInterview.transcript?.segments && (
                  <div>
                    <h3 className="font-medium text-white mb-2">Transcript Statistics</h3>
                    <div className="bg-gray-700 rounded-lg p-4">
                      <p className="text-sm text-gray-300">
                        <span className="font-medium">Segments:</span> {selectedInterview.transcript.segments.length}
                      </p>
                      <p className="text-sm text-gray-300 mt-1">
                        <span className="font-medium">Duration:</span> {
                          selectedInterview.transcript.segments.length > 0 
                            ? `${Math.round(selectedInterview.transcript.segments[selectedInterview.transcript.segments.length - 1]?.end || 0)}s`
                            : '0s'
                        }
                      </p>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <IconFileText className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                <p className="text-gray-400">Select an interview to view details</p>
              </div>
            )}
          </div>
        </div>

        {/* Delete Confirmation Dialog */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-xl p-6 max-w-md w-full mx-4">
              <h3 className="text-lg font-semibold text-white mb-4">Confirm Delete</h3>
              <p className="text-gray-300 mb-6">
                Are you sure you want to delete this interview? This action cannot be undone and will permanently remove all associated data including transcripts, quotes, and analysis.
              </p>
              <div className="flex gap-3 justify-end">
                <button
                  onClick={handleDeleteCancel}
                  className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteConfirm}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                >
                  Delete Interview
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}



