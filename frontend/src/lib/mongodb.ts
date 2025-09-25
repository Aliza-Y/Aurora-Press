import mongoose from 'mongoose';

declare global {
  var mongoose: {
    conn: mongoose.Connection | null;
    promise: Promise<mongoose.Connection> | null;
  };
}

if (!process.env.MONGODB_URI) {
  throw new Error('Please define the MONGODB_URI environment variable inside .env');
}

const MONGODB_URI = process.env.MONGODB_URI;

let cached = global.mongoose;

if (!cached) {
  cached = global.mongoose = { conn: null, promise: null };
}

async function connectDB(): Promise<mongoose.Connection> {
  try {
    if (cached.conn) {
      console.log('Using cached MongoDB connection');
      return cached.conn;
    }

    if (!cached.promise) {
      const opts = {
        bufferCommands: true,
        maxPoolSize: 10,
        serverSelectionTimeoutMS: 5000,
        socketTimeoutMS: 45000,
        dbName: 'test'
      };

      console.log('Connecting to MongoDB...');
      
      const baseUri = MONGODB_URI.split('?')[0];
      const queryParams = MONGODB_URI.includes('?') ? MONGODB_URI.split('?')[1] : '';
      const uriWithoutDB = baseUri.split('/').slice(0, -1).join('/');
      const finalUri = queryParams ? `${uriWithoutDB}/?${queryParams}` : `${uriWithoutDB}/?`;
      
      console.log('Using connection string pattern:', finalUri.replace(/\/\/[^@]+@/, '//***:***@'));
      
      cached.promise = mongoose.connect(finalUri, opts).then((mongoose) => {
        console.log('MongoDB connected successfully');
        return mongoose.connection;
      });
    }

    try {
      cached.conn = await cached.promise;
      return cached.conn;
    } catch (e) {
      cached.promise = null;
      console.error('MongoDB connection error:', e);
      throw e;
    }
  } catch (error) {
    console.error('MongoDB connection error:', error);
    throw new Error('Failed to connect to MongoDB');
  }
}

// Add connection event handlers
mongoose.connection.on('connected', () => {
  console.log('MongoDB connected successfully');
});

mongoose.connection.on('error', (err) => {
  console.error('MongoDB connection error:', err);
});

mongoose.connection.on('disconnected', () => {
  console.log('MongoDB disconnected');
});

process.on('SIGINT', async () => {
  await mongoose.connection.close();
  process.exit(0);
});

export default connectDB; 