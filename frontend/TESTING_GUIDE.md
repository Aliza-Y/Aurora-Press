# Module 9 Frontend Testing Guide

## 🚀 Quick Start

### Option 1: Test with Mock Data (No Backend Required)
```bash
cd frontend
# Set environment variable to use mock API
echo "NEXT_PUBLIC_USE_MOCK_API=true" >> .env.local
npm run dev
```

### Option 2: Test with Real Backend
```bash
# Terminal 1: Start backend
cd /path/to/aurorapress
python run_m9_agentic.py

# Terminal 2: Start frontend
cd frontend
npm run dev
```

## 🧪 Testing Scenarios

### 1. **Basic Upload Test**
1. Go to `http://localhost:3000/dashboard/interview`
2. Upload any audio file (MP3, M4A, WAV)
3. Watch the status change from "running" to "completed"
4. Click "View Results" to see the analysis

### 2. **File Validation Test**
- Try uploading non-audio files (.txt, .pdf, .jpg)
- Try uploading files larger than 100MB
- Verify error messages appear

### 3. **Drag & Drop Test**
- Drag an audio file over the upload area
- Verify the border changes color
- Drop the file and check upload starts

### 4. **UI Navigation Test**
- Test all tabs: Transcript, Key Quotes, Summary & Angles
- Test speaker filtering in transcript view
- Test responsive design on different screen sizes

## 🔧 Mock API Features

When using `NEXT_PUBLIC_USE_MOCK_API=true`, you get:

- **Realistic Data**: Sample transcript with multiple speakers
- **Simulated Processing**: 5-second processing time
- **Error Simulation**: Various error states for testing
- **No Backend Required**: Works completely offline

### Mock Data Includes:
- 4 transcript segments with different speakers
- 3 key quotes with scores and context
- AI-generated summary and 3 story angles
- Claim classification with confidence scores

## 🐛 Debugging

### Check Console Logs
Open browser DevTools (F12) and check the Console tab for:
- API call logs
- Error messages
- Status updates

### Common Issues:
1. **CORS Errors**: Make sure backend is running on port 8000
2. **File Upload Fails**: Check file size and type
3. **Status Not Updating**: Check network tab for API calls

### Environment Variables
Create `.env.local` in the frontend directory:
```env
# Use mock API (no backend required)
NEXT_PUBLIC_USE_MOCK_API=true

# Or use real API (backend required)
NEXT_PUBLIC_USE_MOCK_API=false
```

## 📱 Mobile Testing

Test on mobile devices:
1. Open Chrome DevTools
2. Click device toggle (Ctrl+Shift+M)
3. Select a mobile device
4. Test touch interactions and responsive layout

## 🎯 Expected Behavior

### Upload Process:
1. File validation (type and size)
2. Upload starts with loading spinner
3. Status shows "running" with progress steps
4. After 5 seconds (mock) or real processing, status becomes "completed"
5. "View Results" button appears

### Results Page:
1. Statistics show duration, segments, quotes, angles
2. Transcript tab shows speaker-separated text
3. Quotes tab shows scored quotes with context
4. Summary tab shows AI summary and story angles

## 🔄 Switching Between Mock and Real API

To switch between mock and real API:

1. **Use Mock API** (no backend needed):
   ```bash
   echo "NEXT_PUBLIC_USE_MOCK_API=true" >> .env.local
   npm run dev
   ```

2. **Use Real API** (backend required):
   ```bash
   echo "NEXT_PUBLIC_USE_MOCK_API=false" >> .env.local
   # Start your backend
   npm run dev
   ```

## 📊 Performance Testing

Test with different file sizes:
- Small files (< 1MB): Should upload quickly
- Medium files (1-10MB): Should show progress
- Large files (10-100MB): Should handle gracefully

## 🎨 UI/UX Testing

- **Dark Theme**: Verify all elements are visible
- **Hover States**: Check button and card hover effects
- **Loading States**: Verify spinners and progress indicators
- **Error States**: Test error message display
- **Empty States**: Test when no interviews exist

## 🚨 Error Testing

Test error scenarios:
1. Backend not running (with real API)
2. Invalid file types
3. Files too large
4. Network errors
5. Malformed responses

## 📝 Test Checklist

- [ ] Upload interface works
- [ ] File validation works
- [ ] Drag & drop works
- [ ] Status updates in real-time
- [ ] Results page loads correctly
- [ ] All tabs work (Transcript, Quotes, Summary)
- [ ] Speaker filtering works
- [ ] Mobile responsive
- [ ] Error handling works
- [ ] Navigation works
- [ ] Mock API works (if enabled)
- [ ] Real API works (if backend running)


