import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import bcrypt from 'bcryptjs';
import connectDB from '@/lib/mongodb';
import User from '@/models/User';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

// Extend the built-in types
declare module "next-auth" {
  interface User {
    firstName: string;
    lastName: string;
    isFirstLogin: boolean;
    profileCompleted: boolean;
  }
  
  interface Session {
    user: {
      id: string;
      firstName: string;
      lastName: string;
      isFirstLogin: boolean;
      profileCompleted: boolean;
      email?: string | null;
      name?: string | null;
    }
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id: string;
    firstName: string;
    lastName: string;
    isFirstLogin: boolean;
    profileCompleted: boolean;
  }
}

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error('Please enter an email and password');
        }

        const db = await connectDB();
        if (!db) {
          throw new Error('Database connection failed. Please try again later.');
        }

        // Find user
        const user = await User.findOne({ email: credentials.email });
        if (!user) {
          throw new Error('No user found');
        }

        // Check password
        const isPasswordValid = await bcrypt.compare(credentials.password, user.password);
        if (!isPasswordValid) {
          throw new Error('Invalid password');
        }

        // Update login status
        const isFirstLogin = user.isFirstLogin;
        await User.findByIdAndUpdate(user._id, {
          lastLogin: new Date(),
          isFirstLogin: false
        });

        return {
          id: user._id.toString(),
          name: user.name,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          isFirstLogin: isFirstLogin,
          profileCompleted: user.profileCompleted
        };
      }
    })
  ],
  session: {
    strategy: 'jwt'
  },
  secret: process.env.NEXTAUTH_SECRET || 'fallback-secret-for-development',
  pages: {
    signIn: '/auth',
    signOut: '/auth',
    error: '/auth'
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.firstName = user.firstName;
        token.lastName = user.lastName;
        token.isFirstLogin = user.isFirstLogin;
        token.profileCompleted = user.profileCompleted;
      }
      return token;
    },
    async session({ session, token }) {
      if (token && session.user) {
        session.user.id = token.id;
        session.user.firstName = token.firstName;
        session.user.lastName = token.lastName;
        session.user.isFirstLogin = token.isFirstLogin;
        session.user.profileCompleted = token.profileCompleted;
      }
      return session;
    },
    async redirect({ url, baseUrl }) {
      // Handle redirects based on login status
      if (url.startsWith(baseUrl)) {
        if (url.includes('/auth/callback')) {
          return baseUrl;
        }
        // Check token from session
        const session = await getServerSession(authOptions);
        if (session?.user?.isFirstLogin) {
          return `${baseUrl}/auth/welcome`;
        }
        return `${baseUrl}/auth/login/success`;
      }
      return baseUrl;
    }
  }
});

export { handler as GET, handler as POST }; 