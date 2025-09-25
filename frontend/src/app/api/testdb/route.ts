import { NextResponse } from 'next/server';
import mongoose from 'mongoose';

export async function GET() {
  try {
    if (!process.env.MONGODB_URI) {
      throw new Error('MONGODB_URI is not defined');
    }

    console.log('Attempting to connect to MongoDB...');
    
    const conn = await mongoose.connect(process.env.MONGODB_URI);
    console.log('Connected to MongoDB:', conn.connection.host);
    
    return NextResponse.json({ 
      status: 'Connected successfully',
      host: conn.connection.host
    });
  } catch (error: any) {
    console.error('Connection error details:', {
      message: error.message,
      code: error.code,
      name: error.name
    });
    
    return NextResponse.json({ 
      error: 'Failed to connect',
      details: error.message
    }, { status: 500 });
  }
} 