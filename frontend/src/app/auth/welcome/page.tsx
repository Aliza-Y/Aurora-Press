'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

// Extend Session type to include our custom fields
declare module "next-auth" {
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

export default function Welcome() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth');
    }
  }, [status, router]);

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0D1117]">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-[#2DD4BF]"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0D1117] p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-lg"
      >
        <div className="bg-[#1A1F2B] rounded-2xl p-8 shadow-xl border border-[#2DD4BF]/10">
          <div className="text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200, damping: 15 }}
              className="mx-auto flex items-center justify-center w-20 h-20 rounded-full bg-[#2DD4BF]/20 mb-6"
            >
              <span className="text-3xl text-[#2DD4BF]">👋</span>
            </motion.div>
            
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-3xl font-bold text-white mb-4"
            >
              Welcome, {session?.user?.firstName}!
            </motion.h2>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="space-y-4 text-left bg-[#0D1117]/50 p-6 rounded-xl mb-8"
            >
              <h3 className="text-[#2DD4BF] font-semibold text-lg mb-4">Your Account Details:</h3>
              <p className="text-gray-300">
                <span className="text-gray-400">Full Name:</span>{' '}
                {session?.user?.firstName} {session?.user?.lastName}
              </p>
              <p className="text-gray-300">
                <span className="text-gray-400">Email:</span>{' '}
                {session?.user?.email}
              </p>
              <p className="text-gray-300">
                <span className="text-gray-400">Account Created:</span>{' '}
                {new Date().toLocaleDateString()}
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="space-y-4"
            >
              <Link
                href="/dashboard"
                className="block w-full py-3 px-4 bg-gradient-to-r from-[#2DD4BF] to-[#3B82F6] text-white font-semibold rounded-lg hover:opacity-90 transition-opacity text-center"
              >
                Continue to Dashboard
              </Link>
              
              <p className="text-gray-400 text-sm">
                You can update your profile information in the dashboard settings.
              </p>
            </motion.div>
          </div>
        </div>
      </motion.div>
    </div>
  );
} 