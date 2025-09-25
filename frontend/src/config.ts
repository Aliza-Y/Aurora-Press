// API configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Backend routes that don't use /api prefix
export const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL?.replace('/api', '') || 'http://localhost:8000';

// Other configuration constants can be added here
export const APP_NAME = 'AuroraPress';
export const APP_DESCRIPTION = 'AI-Powered News Article Generation Platform'; 