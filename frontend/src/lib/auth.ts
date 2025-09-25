import { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import bcrypt from 'bcryptjs';
import connectDB from '@/lib/mongodb';
import User from '@/models/User';

export const authOptions: NextAuthOptions = {
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

        await connectDB();

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
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  secret: process.env.NEXTAUTH_SECRET,
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
    }
  },
  cookies: {
    sessionToken: {
      name: 'next-auth.session-token',
      options: {
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production'
      }
    }
  }
}; 