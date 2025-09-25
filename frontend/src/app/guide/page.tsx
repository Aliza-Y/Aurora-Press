'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { IconArrowLeft } from '@tabler/icons-react';

export default function GuidePage() {
  const steps = [
    {
      number: '01',
      title: 'Sign Up & Login',
      description: 'Create your account and access your personalized dashboard.'
    },
    {
      number: '02',
      title: 'Choose Your Topic',
      description: 'Select a trending topic or input your own story idea.'
    },
    {
      number: '03',
      title: 'Research & Write',
      description: 'Use our research tools to gather verified information and write your article.'
    },
    {
      number: '04',
      title: 'Review & Optimize',
      description: 'Let our tools check facts, optimize SEO, and ensure quality.'
    },
    {
      number: '05',
      title: 'Publish',
      description: 'Publish directly to your preferred platforms and track engagement.'
    }
  ];

  return (
    <main className="min-h-screen bg-[#0F172A] text-white pt-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto relative">
        <Link 
          href="/"
          className="absolute -left-4 -top-12 flex items-center text-gray-400 hover:text-[#2DD4BF] transition-colors group"
        >
          <IconArrowLeft className="w-6 h-6 mr-2 transform group-hover:-translate-x-1 transition-transform" />
          <span>Back to Home</span>
        </Link>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-4xl font-bold mb-8 bg-gradient-to-r from-[#2DD4BF] to-blue-500 text-transparent bg-clip-text">
            Quick Start Guide
          </h1>
          <p className="text-xl text-gray-400 mb-12">
            Follow these simple steps to get started with AuroraPress
          </p>

          <div className="space-y-6">
            {steps.map((step) => (
              <motion.div
                key={step.number}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
                className="flex items-start bg-[#1E293B] rounded-lg p-6"
              >
                <span className="text-2xl font-bold text-[#2DD4BF] mr-6">
                  {step.number}
                </span>
                <div>
                  <h2 className="text-xl font-semibold text-white mb-2">
                    {step.title}
                  </h2>
                  <p className="text-gray-400">
                    {step.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="mt-24 pb-12 border-t border-gray-800">
            <div className="pt-8 text-center text-sm text-gray-400">
              <p>© {new Date().getFullYear()} AuroraPress. All rights reserved.</p>
              <p className="mt-2">Empowering journalists with intelligent automation</p>
            </div>
          </div>
        </motion.div>
      </div>
    </main>
  );
} 