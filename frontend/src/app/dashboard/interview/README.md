# Module 9 - Interview Intelligence Frontend

This module provides a comprehensive frontend interface for AuroraPress's Interview Intelligence system, allowing journalists to upload audio interviews and receive AI-powered analysis, transcription, and insights.

## Features

### 🎤 Audio Upload
- **Drag & Drop Interface**: Intuitive file upload with visual feedback
- **File Validation**: Supports MP3, M4A, and WAV files up to 100MB
- **Real-time Status**: Live updates during processing with progress indicators

### 📝 Transcript Analysis
- **Speaker Identification**: Automatic speaker diarization with visual indicators
- **Claim Detection**: AI-powered claim classification with confidence scores
- **Time Stamps**: Precise timing for each segment
- **Filtering**: Filter by specific speakers or view all

### 💬 Key Quotes Extraction
- **Intelligent Scoring**: TF-IDF and sentiment-based quote ranking
- **Contextual Information**: Additional context for each quote
- **Visual Highlighting**: Color-coded importance indicators

### 📊 Summary & Story Angles
- **AI-Generated Summaries**: Comprehensive interview summaries
- **Story Angles**: Multiple narrative perspectives for article writing
- **Structured Display**: Clean, organized presentation of insights

## File Structure

```
frontend/src/app/dashboard/interview/
├── page.tsx                    # Main interview management page
├── [id]/
│   └── page.tsx               # Interview detail/results page
└── README.md                  # This documentation

frontend/src/lib/
└── module9-api.ts            # API integration utilities
```

## API Integration

The frontend integrates with the Module 9 backend through a comprehensive API utility (`module9-api.ts`) that provides:

- **Upload Management**: File upload with progress tracking
- **Pipeline Monitoring**: Real-time status updates and polling
- **Data Retrieval**: Access to transcripts, quotes, summaries, and analysis
- **Error Handling**: Robust error management and user feedback

### Key API Functions

```typescript
// Upload and process
uploadInterview(file: File): Promise<UploadResponse>
pollStatus(interviewId, onUpdate, onComplete, onError): Promise<() => void>

// Data retrieval
getTranscript(interviewId): Promise<Transcript>
getQuotes(interviewId): Promise<Quotes>
getSummary(interviewId): Promise<Summary>
getAnalysis(interviewId): Promise<Analysis>
```

## User Interface

### Main Page (`/dashboard/interview`)
- **Upload Section**: Large, accessible drag-and-drop area
- **Interview List**: Recent interviews with status indicators
- **Real-time Updates**: Live polling for processing status
- **Error Handling**: Clear error messages and recovery options

### Detail Page (`/dashboard/interview/[id]`)
- **Tabbed Interface**: Organized view of transcript, quotes, and summary
- **Statistics Overview**: Key metrics and processing status
- **Interactive Elements**: Speaker filtering, time navigation
- **Responsive Design**: Works on desktop and mobile devices

## Design System

The Module 9 frontend follows AuroraPress's established design system:

- **Color Scheme**: Dark theme with `#2DD4BF` accent color
- **Typography**: Clean, readable fonts with proper hierarchy
- **Components**: Consistent with existing dashboard modules
- **Animations**: Smooth transitions using Framer Motion
- **Icons**: Tabler Icons for consistency

## Navigation Integration

Module 9 is integrated into the main navigation:
- **Icon**: Microphone icon (`IconMicrophone`)
- **Position**: Between "My Articles" and "Audience Engagement"
- **Route**: `/dashboard/interview`

## Technical Implementation

### State Management
- **React Hooks**: useState, useEffect for local state
- **Real-time Updates**: Polling mechanism for live status updates
- **Error Boundaries**: Comprehensive error handling

### Performance Optimizations
- **Parallel API Calls**: Efficient data fetching
- **Conditional Rendering**: Only load data when needed
- **Memoization**: Optimized re-renders

### Accessibility
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader Support**: Proper ARIA labels
- **Visual Feedback**: Clear status indicators and loading states

## Usage

1. **Upload Audio**: Drag and drop or click to upload an audio file
2. **Monitor Progress**: Watch real-time processing updates
3. **View Results**: Click "View Results" when processing completes
4. **Explore Data**: Navigate through transcript, quotes, and summary tabs
5. **Extract Insights**: Use the analysis for article writing

## Error Handling

The system handles various error scenarios:
- **Upload Failures**: File validation and network errors
- **Processing Errors**: Pipeline failures with detailed error messages
- **Data Loading**: Graceful handling of missing or incomplete data
- **Network Issues**: Retry mechanisms and user feedback

## Future Enhancements

Potential improvements for future versions:
- **Audio Playback**: Built-in audio player with transcript sync
- **Export Options**: Download transcripts and summaries
- **Batch Processing**: Multiple file upload support
- **Advanced Filtering**: More sophisticated search and filter options
- **Collaboration**: Share interviews with team members

## Dependencies

- **Next.js**: React framework
- **Framer Motion**: Animations and transitions
- **Tabler Icons**: Icon library
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling framework

## Backend Integration

Requires the Module 9 backend to be running on `http://localhost:8000` with the following endpoints:
- `POST /m9/upload` - File upload
- `GET /m9/pipeline/status` - Status checking
- `GET /m9/transcript` - Transcript data
- `GET /m9/quotes` - Quotes data
- `GET /m9/summary` - Summary data
- `GET /m9/analysis` - Analysis data


