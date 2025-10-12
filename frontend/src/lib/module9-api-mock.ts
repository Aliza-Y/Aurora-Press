// Mock API for testing Module 9 frontend without backend
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

// Mock data
const mockTranscript: Transcript = {
  interview_id: "test-interview-123",
  segments: [
    {
      start: 0,
      end: 15.5,
      speaker: "SPEAKER_00",
      text: "Welcome to today's interview. Can you tell us about your experience with the new technology?",
      claim: 0,
      claim_conf: 0.85
    },
    {
      start: 15.5,
      end: 45.2,
      speaker: "SPEAKER_01",
      text: "Absolutely. I've been working with this technology for over two years now, and it has completely transformed our workflow. The efficiency gains have been remarkable - we've seen a 40% increase in productivity.",
      claim: 1,
      claim_conf: 0.92
    },
    {
      start: 45.2,
      end: 60.8,
      speaker: "SPEAKER_00",
      text: "That's impressive. What would you say are the main challenges you've faced?",
      claim: 0,
      claim_conf: 0.78
    },
    {
      start: 60.8,
      end: 90.1,
      speaker: "SPEAKER_01",
      text: "The biggest challenge was definitely the learning curve. Our team needed significant training, and there were some initial resistance issues. However, once people saw the benefits, adoption became much smoother.",
      claim: 0,
      claim_conf: 0.88
    }
  ]
};

const mockQuotes: Quotes = {
  interview_id: "test-interview-123",
  quotes: [
    {
      text: "I've been working with this technology for over two years now, and it has completely transformed our workflow.",
      start: 15.5,
      end: 25.2,
      score: 0.95,
      context: "Response to question about experience with new technology"
    },
    {
      text: "The efficiency gains have been remarkable - we've seen a 40% increase in productivity.",
      start: 25.2,
      end: 35.8,
      score: 0.92,
      context: "Quantifying the impact of the technology"
    },
    {
      text: "The biggest challenge was definitely the learning curve. Our team needed significant training, and there were some initial resistance issues.",
      start: 60.8,
      end: 75.3,
      score: 0.88,
      context: "Discussing challenges faced during implementation"
    }
  ]
};

const mockSummary: Summary = {
  interview_id: "test-interview-123",
  summary: "The interview covers a technology implementation that has significantly improved workflow efficiency. The interviewee discusses their two-year experience with the technology, highlighting a 40% productivity increase. Key challenges included the learning curve and initial team resistance, though adoption improved once benefits became apparent. The conversation provides valuable insights into both the positive outcomes and implementation challenges of new technology adoption.",
  angles: [
    "Technology Implementation Success Story: Focus on the 40% productivity increase and workflow transformation",
    "Change Management Challenges: Explore the learning curve and resistance issues during technology adoption",
    "ROI and Business Impact: Highlight the quantifiable benefits and efficiency gains from the technology"
  ]
};

// Mock functions
export const uploadInterview = async (file: File): Promise<UploadResponse> => {
  // Simulate upload delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  return {
    interview_id: `mock-${Date.now()}`,
    temp_file_path: `/mock/path/${file.name}`
  };
};

export const getPipelineStatus = async (interviewId: string): Promise<PipelineStatus> => {
  // Simulate different statuses based on time
  const elapsed = Date.now() - parseInt(interviewId.split('-')[1]);
  const status = elapsed < 5000 ? 'running' : 'completed';
  
  return {
    interview_id: interviewId,
    status,
    steps: status === 'completed' ? {
      ingestion: 'completed',
      transcription: 'completed',
      claim_classification: 'completed',
      quote_mining: 'completed',
      summary_generation: 'completed'
    } : {
      ingestion: 'completed',
      transcription: 'running',
      claim_classification: 'pending',
      quote_mining: 'pending',
      summary_generation: 'pending'
    },
    errors: []
  };
};

export const triggerPipelineTick = async (interviewId: string): Promise<PipelineStatus> => {
  return getPipelineStatus(interviewId);
};

export const getTranscript = async (interviewId: string): Promise<Transcript> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  return { ...mockTranscript, interview_id };
};

export const getQuotes = async (interviewId: string): Promise<Quotes> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  return { ...mockQuotes, interview_id };
};

export const getSummary = async (interviewId: string): Promise<Summary> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  return { ...mockSummary, interview_id };
};

export const getAnalysis = async (interviewId: string) => {
  await new Promise(resolve => setTimeout(resolve, 500));
  return {
    interview_id: interviewId,
    entities: [
      { text: "technology", label: "TECHNOLOGY", confidence: 0.95 },
      { text: "productivity", label: "BUSINESS", confidence: 0.88 },
      { text: "workflow", label: "PROCESS", confidence: 0.92 }
    ],
    sentiment: { positive: 0.7, negative: 0.2, neutral: 0.1 },
    claim_candidates: []
  };
};

export const getHandoff = async (interviewId: string) => {
  await new Promise(resolve => setTimeout(resolve, 500));
  return {
    interview_id: interviewId,
    payloads: {
      module3: { summary: mockSummary.summary, angles: mockSummary.angles },
      module6: { quotes: mockQuotes.quotes }
    }
  };
};

export const getSources = async () => {
  await new Promise(resolve => setTimeout(resolve, 500));
  return {
    sources: [],
    relationships: []
  };
};

export const getDebugAgents = async () => {
  await new Promise(resolve => setTimeout(resolve, 500));
  return {
    registered: ['IngestionAgent', 'TranscriptionAgent', 'ClaimClassifierAgent', 'QuoteMinerAgent', 'SummaryAnglesAgent']
  };
};

export const pollStatus = async (
  interviewId: string,
  onUpdate: (status: PipelineStatus) => void,
  onComplete: (status: PipelineStatus) => void,
  onError: (error: Error) => void,
  interval: number = 2000
): Promise<() => void> => {
  let isPolling = true;
  let pollCount = 0;

  const poll = async () => {
    if (!isPolling) return;

    try {
      const status = await getPipelineStatus(interviewId);
      onUpdate(status);

      pollCount++;
      if (status.status === 'completed' || status.status === 'failed' || pollCount >= 5) {
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

  return () => {
    isPolling = false;
  };
};


