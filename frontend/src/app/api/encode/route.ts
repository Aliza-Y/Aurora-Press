import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const uri = process.env.MONGODB_URI || '';
    
    // Extract current parts
    const matches = uri.match(/mongodb\+srv:\/\/([^:]+):([^@]+)@(.+)/);
    if (!matches) {
      throw new Error('Invalid connection string format');
    }

    const [_, username, password, rest] = matches;
    
    // Encode password and rebuild URI
    const encodedPassword = encodeURIComponent(password);
    
    // Build the new connection string with valid database name (using underscore instead of dot)
    const baseUri = `mongodb+srv://${username}:${encodedPassword}@${rest}`;
    const finalUri = baseUri.includes('/test_users?') ? baseUri : 
                    baseUri.replace('/?', '/test_users?');
    
    // Show both masked and actual connection strings
    return NextResponse.json({ 
      masked: finalUri.replace(encodedPassword, '****'),
      actual: finalUri,
      message: 'Copy the actual connection string to your .env file (using test_users as database name)'
    });
  } catch (error: any) {
    return NextResponse.json({ 
      error: 'Failed to encode connection string',
      details: error.message
    }, { status: 500 });
  }
} 