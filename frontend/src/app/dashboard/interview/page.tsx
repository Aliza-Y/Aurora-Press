'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { IconUpload, IconMicrophone, IconFileText, IconClock, IconCheck, IconX, IconEye, IconHistory } from '@tabler/icons-react';
import MainLayout from '@/components/layout/MainLayout';
// Switch between real and mock API
const USE_MOCK_API = process.env.NODE_ENV === 'development' && process.env.NEXT_PUBLIC_USE_MOCK_API === 'true';

// Import both APIs
import { uploadInterview as uploadInterviewMock, pollStatus as pollStatusMock, PipelineStatus } from '@/lib/module9-api-mock';
import { uploadInterview as uploadInterviewReal, pollStatus as pollStatusReal } from '@/lib/module9-api';

// Use the appropriate API based on environment
const uploadInterview = USE_MOCK_API ? uploadInterviewMock : uploadInterviewReal;
const pollStatus = USE_MOCK_API ? pollStatusMock : pollStatusReal;

interface Interview {
  interview_id: string;
  status?: string;
  steps: Record<string, any>;
  errors: any[];
  created_at?: string;
  title?: string;
  duration?: number;
}


export default function InterviewIntelligence() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [interviewTitle, setInterviewTitle] = useState('');

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/');
    }
  }, [status, router]);

  useEffect(() => {
    // Try to load from localStorage first for immediate display
    const savedInterviews = localStorage.getItem('aurorapress_interviews');
    if (savedInterviews) {
      try {
        setInterviews(JSON.parse(savedInterviews));
      } catch (e) {
        console.error('Error parsing saved interviews:', e);
      }
    }
    
    // Then fetch fresh data from server
    fetchInterviews();
  }, []);

  // Refresh interviews when the page becomes visible (user navigates back)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        fetchInterviews();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  const fetchInterviews = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/m9/interviews');
      if (!response.ok) {
        throw new Error('Failed to fetch interviews');
      }
      const data = await response.json();
      const interviewsData = data.interviews || [];
      setInterviews(interviewsData);
      
      // Persist to localStorage
      localStorage.setItem('aurorapress_interviews', JSON.stringify(interviewsData));
    } catch (error) {
      console.error('Error fetching interviews:', error);
      setError('Failed to fetch interviews');
      
      // Try to load from localStorage as fallback
      const savedInterviews = localStorage.getItem('aurorapress_interviews');
      if (savedInterviews) {
        try {
          setInterviews(JSON.parse(savedInterviews));
        } catch (e) {
          console.error('Error parsing saved interviews:', e);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!file) return;

    // Validate file type
    const allowedTypes = ['audio/mp3', 'audio/mpeg', 'audio/m4a', 'audio/mp4', 'audio/x-m4a', 'audio/wav', 'audio/x-wav'];
    const allowedExtensions = ['.mp3', '.m4a', '.wav', '.mp4'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      setError(`Please upload a valid audio file (MP3, M4A, or WAV). Detected type: ${file.type}, extension: ${fileExtension}`);
      return;
    }

    // Validate file size (max 100MB)
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
      setError('File size must be less than 100MB');
      return;
    }

    try {
      setUploading(true);
      setError(null);

      const result = await uploadInterview(file, interviewTitle.trim() || undefined);
      
      // Add the new interview to the list
      const newInterview: Interview = {
        interview_id: result.interview_id,
        status: 'running',
        steps: {},
        errors: [],
        created_at: new Date().toISOString(),
        title: interviewTitle.trim() || file.name.replace(/\.[^/.]+$/, ""), // Use custom title or filename without extension
        duration: 0
      };

      const updatedInterviews = [newInterview, ...interviews];
      setInterviews(updatedInterviews);
      
      // Persist to localStorage
      localStorage.setItem('aurorapress_interviews', JSON.stringify(updatedInterviews));
      
      // Clear the title input
      setInterviewTitle('');
      
      // Start polling for status updates
      pollInterviewStatus(result.interview_id);
      
    } catch (error) {
      console.error('Upload error:', error);
      setError(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const pollInterviewStatus = async (interviewId: string) => {
    pollStatus(
      interviewId,
      (status: PipelineStatus) => {
        setInterviews(prev => {
          const updated = prev.map(interview => 
            interview.interview_id === interviewId 
              ? { ...interview, ...status }
              : interview
          );
          // Persist updated interviews
          localStorage.setItem('aurorapress_interviews', JSON.stringify(updated));
          return updated;
        });
      },
      (status: PipelineStatus) => {
        setInterviews(prev => {
          const updated = prev.map(interview => 
            interview.interview_id === interviewId 
              ? { ...interview, ...status }
              : interview
          );
          // Persist updated interviews
          localStorage.setItem('aurorapress_interviews', JSON.stringify(updated));
          return updated;
        });
      },
      (error: Error) => {
        console.error('Error polling status:', error);
      }
    );
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const getStatusIcon = (status: string | undefined) => {
    switch (status) {
      case 'completed':
        return <IconCheck className="w-5 h-5 text-green-400" />;
      case 'failed':
        return <IconX className="w-5 h-5 text-red-400" />;
      case 'running':
        return <div className="w-5 h-5 border-2 border-[#2DD4BF] border-t-transparent rounded-full animate-spin" />;
      default:
        return <IconClock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string | undefined) => {
    switch (status) {
      case 'completed':
        return 'text-green-400';
      case 'failed':
        return 'text-red-400';
      case 'running':
        return 'text-[#2DD4BF]';
      default:
        return 'text-gray-400';
    }
  };

  if (status === 'loading' || !session) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <MainLayout>
      <div className="p-8">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2 text-white">Interview Intelligence</h1>
              <p className="text-gray-400">Upload audio interviews and get AI-powered analysis, transcription, and insights.</p>
            </div>
            <button
              onClick={() => router.push('/dashboard/interviews')}
              className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <IconHistory className="w-4 h-4 mr-2" />
              View History
            </button>
          </div>
        </div>

        {/* Upload Section */}
        <div className="mb-8">
          {/* Interview Title Input */}
          <div className="mb-6">
            <label htmlFor="interview-title" className="block text-sm font-medium text-gray-300 mb-2">
              Interview Title (Optional)
            </label>
            <input
              id="interview-title"
              type="text"
              value={interviewTitle}
              onChange={(e) => setInterviewTitle(e.target.value)}
              placeholder="Enter a title for this interview..."
              className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-[#2DD4BF] focus:outline-none focus:ring-1 focus:ring-[#2DD4BF]"
              disabled={uploading}
            />
            <p className="mt-1 text-xs text-gray-500">
              If left empty, a title will be generated automatically
            </p>
          </div>

          <div
            className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
              dragActive
                ? 'border-[#2DD4BF] bg-[#2DD4BF]/5'
                : 'border-gray-600 hover:border-gray-500'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept="audio/*"
              onChange={handleFileInput}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              disabled={uploading}
            />
            
            <div className="space-y-4">
              <div className="mx-auto w-16 h-16 bg-[#2DD4BF]/10 rounded-full flex items-center justify-center">
                {uploading ? (
                  <div className="w-8 h-8 border-2 border-[#2DD4BF] border-t-transparent rounded-full animate-spin" />
                ) : (
                  <IconUpload className="w-8 h-8 text-[#2DD4BF]" />
                )}
              </div>
              
              <div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {uploading ? 'Processing...' : 'Upload Audio Interview'}
                </h3>
                <p className="text-gray-400 mb-4">
                  Drag and drop your audio file here, or click to browse
                </p>
                <p className="text-sm text-gray-500">
                  Supports MP3, M4A, and WAV files up to 100MB
                </p>
              </div>
            </div>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
              {error}
            </div>
          )}
        </div>

        {/* Interviews List */}
        <div>
          <h2 className="text-2xl font-bold mb-6 text-white">Recent Interviews</h2>
          
          {loading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#2DD4BF]"></div>
            </div>
          ) : interviews.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <IconMicrophone className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>No interviews uploaded yet. Upload your first audio file to get started.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {interviews.filter(interview => interview && interview.interview_id).map((interview) => (
                <motion.div
                  key={interview.interview_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-[#1E293B] p-6 rounded-xl hover:bg-gray-800/50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-[#2DD4BF]/10 rounded-lg">
                        <IconFileText className="w-6 h-6 text-[#2DD4BF]" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">
                          {interview.title || `Interview ${interview.interview_id.slice(0, 8)}`}
                        </h3>
                        <div className="flex items-center gap-4 mt-1">
                          <span className={`flex items-center gap-2 text-sm ${getStatusColor(interview.status)}`}>
                            {getStatusIcon(interview.status)}
                            {(interview.status || 'pending').charAt(0).toUpperCase() + (interview.status || 'pending').slice(1)}
                          </span>
                          {interview.created_at && (
                            <span className="text-sm text-gray-400">
                              {new Date(interview.created_at).toLocaleString()}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      {interview.status === 'completed' && (
                        <button
                          onClick={() => router.push(`/dashboard/interview/${interview.interview_id}`)}
                          className="flex items-center gap-2 px-4 py-2 bg-[#2DD4BF] hover:bg-[#2DD4BF]/90 text-white rounded-lg transition-colors"
                        >
                          <IconEye className="w-4 h-4" />
                          View Results
                        </button>
                      )}
                      
                      {interview.status === 'running' && (
                        <div className="flex items-center gap-2 text-sm text-gray-400">
                          <div className="w-4 h-4 border-2 border-[#2DD4BF] border-t-transparent rounded-full animate-spin" />
                          Processing...
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Pipeline Steps Progress */}
                  {interview.status === 'running' && Object.keys(interview.steps).length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-700">
                      <div className="text-sm text-gray-400 mb-2">Processing Steps:</div>
                      <div className="space-y-2">
                        {Object.entries(interview.steps).map(([step, status]) => (
                          <div key={step} className="flex items-center gap-2 text-sm">
                            <div className={`w-2 h-2 rounded-full ${
                              status === 'completed' ? 'bg-green-400' : 
                              status === 'running' ? 'bg-[#2DD4BF]' : 'bg-gray-600'
                            }`} />
                            <span className="text-gray-300 capitalize">
                              {step.replace(/_/g, ' ')}
                            </span>
                            {status === 'completed' && <IconCheck className="w-4 h-4 text-green-400" />}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Errors */}
                  {interview.errors && interview.errors.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-red-500/20">
                      <div className="text-sm text-red-400 mb-2">Errors:</div>
                      <div className="space-y-1">
                        {interview.errors.map((error, index) => (
                          <div key={index} className="text-sm text-red-300">
                            {typeof error === 'string' ? error : JSON.stringify(error)}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
