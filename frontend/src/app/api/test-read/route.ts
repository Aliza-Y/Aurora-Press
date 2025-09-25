import { NextResponse } from 'next/server';
import connectDB from '@/lib/mongodb';
import Test from '@/models/Test';

export async function GET() {
  try {
    await connectDB();
    
    // Try to read data
    const data = await Test.find();
    console.log('Found data:', data);
    
    return NextResponse.json({ 
      success: true,
      data,
      count: data.length
    });
  } catch (error: any) {
    console.error('Error reading data:', error);
    return NextResponse.json({ 
      error: 'Failed to read data',
      details: error.message
    }, { status: 500 });
  }
} 