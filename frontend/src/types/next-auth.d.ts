import 'next-auth';
import { JWT } from 'next-auth/jwt';

declare module 'next-auth' {
  interface User {
    id: string;
    firstName: string;
    lastName: string;
    isFirstLogin: boolean;
    profileCompleted: boolean;
    email?: string | null;
    name?: string | null;
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

declare module 'next-auth/jwt' {
  interface JWT {
    id: string;
    firstName: string;
    lastName: string;
    isFirstLogin: boolean;
    profileCompleted: boolean;
  }
} 