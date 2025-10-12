const API_BASE_URL = 'http://localhost:8000/m9';

export interface UploadResponse {
  interview_id: string;
  temp_file_path: string;
}

export interface PipelineStatus {
  interview_id: string;
  status: string;
  steps: Record<string, any>;
  errors: any[];
}

export interface TranscriptSegment {
  start: number;
  end: number;
  speaker: string;
  text: string;
  claim?: number;
  claim_conf?: number;
}

export interface Transcript {
  interview_id: string;
  segments: TranscriptSegment[];
}

export interface Quote {
  text: string;
  start: number;
  end: number;
  score: number;
  context: string;
}

export interface Quotes {
  interview_id: string;
  quotes: Quote[];
}

export interface Summary {
  interview_id: string;
  summary: string;
  angles: string[];
}

export interface Analysis {
  interview_id: string;
  entities: any[];
  sentiment: any;
  claim_candidates: any[];
}

export interface Handoff {
  interview_id: string;
  payloads: Record<string, any>;
}

// Upload audio file
export const uploadInterview = async (file: File, title?: string): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  if (title) {
    formData.append('title', title);
  }

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status}`);
  }

  return response.json();
};

// Get pipeline status
export const getPipelineStatus = async (interviewId: string): Promise<PipelineStatus> => {
  const response = await fetch(`${API_BASE_URL}/pipeline/status?interview_id=${interviewId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get status: ${response.status}`);
  }

  return response.json();
};

// Trigger pipeline tick
export const triggerPipelineTick = async (interviewId: string): Promise<PipelineStatus> => {
  const response = await fetch(`${API_BASE_URL}/pipeline/tick?interview_id=${interviewId}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to trigger tick: ${response.status}`);
  }

  return response.json();
};

// Get transcript
export const getTranscript = async (interviewId: string): Promise<Transcript> => {
  const response = await fetch(`${API_BASE_URL}/transcript?interview_id=${interviewId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get transcript: ${response.status}`);
  }

  return response.json();
};

// Get quotes
export const getQuotes = async (interviewId: string): Promise<Quotes> => {
  const response = await fetch(`${API_BASE_URL}/quotes?interview_id=${interviewId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get quotes: ${response.status}`);
  }

  return response.json();
};

// Get summary
export const getSummary = async (interviewId: string): Promise<Summary> => {
  const response = await fetch(`${API_BASE_URL}/summary?interview_id=${interviewId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get summary: ${response.status}`);
  }

  return response.json();
};

// Get analysis
export const getAnalysis = async (interviewId: string): Promise<Analysis> => {
  const response = await fetch(`${API_BASE_URL}/analysis?interview_id=${interviewId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get analysis: ${response.status}`);
  }

  return response.json();
};

// Get handoff data
export const getHandoff = async (interviewId: string): Promise<Handoff> => {
  const response = await fetch(`${API_BASE_URL}/handoff?interview_id=${interviewId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get handoff: ${response.status}`);
  }

  return response.json();
};

// Get sources
export const getSources = async (): Promise<{ sources: any[]; relationships: any[] }> => {
  const response = await fetch(`${API_BASE_URL}/sources`);
  
  if (!response.ok) {
    throw new Error(`Failed to get sources: ${response.status}`);
  }

  return response.json();
};

// Debug agents
export const getDebugAgents = async (): Promise<{ registered: string[] }> => {
  const response = await fetch(`${API_BASE_URL}/debug/agents`);
  
  if (!response.ok) {
    throw new Error(`Failed to get debug info: ${response.status}`);
  }

  return response.json();
};

// Poll for status updates
export const pollStatus = async (
  interviewId: string,
  onUpdate: (status: PipelineStatus) => void,
  onComplete: (status: PipelineStatus) => void,
  onError: (error: Error) => void,
  interval: number = 2000
): Promise<() => void> => {
  let isPolling = true;
  let hasTriggeredProcessing = false;

  const poll = async () => {
    if (!isPolling) return;

    try {
      // First, trigger processing if we haven't already
      if (!hasTriggeredProcessing) {
        try {
          const response = await fetch(`${API_BASE_URL}/pipeline/tick?interview_id=${interviewId}`, {
            method: 'POST',
          });
          if (response.ok) {
            hasTriggeredProcessing = true;
          }
        } catch (error) {
          console.log('Processing already triggered or error:', error);
        }
      }

      const status = await getPipelineStatus(interviewId);
      onUpdate(status);

      if (status.status === 'completed' || status.status === 'failed') {
        onComplete(status);
        isPolling = false;
      } else {
        setTimeout(poll, interval);
      }
    } catch (error) {
      onError(error as Error);
      isPolling = false;
    }
  };

  poll();

  // Return cleanup function
  return () => {
    isPolling = false;
  };
};

// Get list of all interviews
export const getInterviews = async (): Promise<Interview[]> => {
  const response = await fetch(`${API_BASE_URL}/interviews`);
  if (!response.ok) {
    throw new Error('Failed to fetch interviews');
  }
  const data = await response.json();
  return data.interviews;
};

// Delete an interview
export const deleteInterview = async (interviewId: string): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/interviews/${interviewId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete interview');
  }
};

export interface Interview {
  interview_id: string;
  title: string;
  created_at: string;
  status: string;
}


