import { NextResponse } from 'next/server';
import connectDB from '@/lib/mongodb';

export async function GET() {
  try {
    // Log the MongoDB URI (without sensitive info)
    const uri = process.env.MONGODB_URI || '';
    const sanitizedUri = uri.replace(/\/\/[^@]+@/, '//***:***@');
    console.log('Attempting connection with URI:', sanitizedUri);
    
    // Attempt connection
    await connectDB();
    
    return NextResponse.json({ 
      success: true,
      message: 'MongoDB connection successful'
    });
  } catch (error: any) {
    console.error('Connection test error:', error);
    return NextResponse.json({ 
      success: false,
      error: error.message
    }, { status: 500 });
  }
} 