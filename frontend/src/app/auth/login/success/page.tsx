'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { CheckCircleIcon } from '@heroicons/react/24/outline';

export default function LoginSuccess() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0D1117] p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md"
      >
        <div className="bg-[#1A1F2B] rounded-2xl p-8 shadow-xl border border-[#2DD4BF]/10">
          <div className="text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200, damping: 15 }}
              className="mx-auto flex items-center justify-center w-16 h-16 rounded-full bg-[#2DD4BF]/20 mb-6"
            >
              <CheckCircleIcon className="w-10 h-10 text-[#2DD4BF]" />
            </motion.div>
            
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-2xl font-bold text-white mb-4"
            >
              Welcome Back!
            </motion.h2>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-gray-400 mb-8"
            >
              You've successfully logged in to AuroraPress. Ready to continue your journey?
            </motion.p>

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
                Go to Dashboard
              </Link>
            </motion.div>
          </div>
        </div>
      </motion.div>
    </div>
  );
} 