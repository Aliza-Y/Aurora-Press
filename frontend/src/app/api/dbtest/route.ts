import { NextResponse } from 'next/server';
import mongoose from 'mongoose';

export async function GET() {
  try {
    if (!process.env.MONGODB_URI) {
      throw new Error('MONGODB_URI is not defined');
    }

    // Log connection attempt
    const maskedUri = process.env.MONGODB_URI.replace(
      /(mongodb\+srv:\/\/[^:]+:)([^@]+)(@.*)/,
      '$1****$3'
    );
    console.log('Attempting to connect with:', maskedUri);

    // Configure mongoose
    mongoose.set('strictQuery', false);
    
    // Try to connect
    const conn = await mongoose.connect(process.env.MONGODB_URI, {
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
    });

    // Log success
    console.log('Connected to MongoDB:', {
      host: conn.connection.host,
      database: conn.connection.name,
      port: conn.connection.port,
      readyState: conn.connection.readyState
    });
    
    return NextResponse.json({ 
      status: 'Connected successfully',
      details: {
        host: conn.connection.host,
        database: conn.connection.name,
        port: conn.connection.port,
        readyState: conn.connection.readyState
      }
    });
  } catch (error: any) {
    // Log detailed error information
    console.error('Connection error details:', {
      message: error.message,
      code: error.code,
      name: error.name,
      stack: error.stack,
      uri: process.env.MONGODB_URI?.includes('<') ? 
        'Contains unescaped characters (<)' : 
        'URI format looks correct'
    });
    
    return NextResponse.json({ 
      error: 'Failed to connect',
      details: error.message,
      code: error.code,
      name: error.name
    }, { status: 500 });
  }
} 