'use client';

import React from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { BeakerIcon, NewspaperIcon, SparklesIcon, ShieldCheckIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';

const features = [
  {
    name: 'AI-Powered Research',
    description: 'Advanced algorithms assist in gathering and verifying information from multiple sources.',
    icon: BeakerIcon,
  },
  {
    name: 'Automated Publishing',
    description: 'Streamlined workflow for content distribution across multiple platforms.',
    icon: NewspaperIcon,
  },
  {
    name: 'Smart Analytics',
    description: 'Real-time insights into content performance and audience engagement.',
    icon: SparklesIcon,
  },
  {
    name: 'Quality Assurance',
    description: 'Automated fact-checking and compliance verification systems.',
    icon: ShieldCheckIcon,
  },
];

export default function About() {
  return (
    <main className="min-h-screen bg-[#0D1117]">
      <div className="relative pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        {/* Back to Home Button */}
        <div className="max-w-7xl mx-auto relative">
          <Link 
            href="/"
            className="absolute -left-4 -top-12 flex items-center text-gray-400 hover:text-[#2DD4BF] transition-colors group"
          >
            <ArrowLeftIcon className="w-5 h-5 mr-2 transform group-hover:-translate-x-1 transition-transform" />
            <span>Back to Home</span>
          </Link>
        </div>

        <div className="max-w-7xl mx-auto relative">
          {/* Hero Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center"
          >
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              <span className="bg-gradient-to-r from-[#2DD4BF] to-[#3B82F6] bg-clip-text text-transparent">
                About AuroraPress
              </span>
            </h1>
            <p className="text-gray-400 text-lg max-w-3xl mx-auto mb-12">
              AuroraPress is revolutionizing journalism by combining cutting-edge AI technology 
              with traditional journalistic values. We empower journalists to create impactful 
              stories while maintaining the highest standards of accuracy and integrity.
            </p>
          </motion.div>

          {/* Features Grid */}
          <div className="mt-16 grid gap-8 grid-cols-1 md:grid-cols-2">
            {features.map((feature, index) => (
              <motion.div
                key={feature.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="relative group bg-[#1E293B] rounded-xl p-6 hover:bg-[#1E293B]/80 transition-colors"
              >
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <feature.icon 
                      className="h-8 w-8 text-[#2DD4BF]" 
                      aria-hidden="true" 
                    />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-xl font-semibold text-white">
                      {feature.name}
                    </h3>
                    <p className="mt-2 text-gray-400">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Mission Statement */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="mt-16 bg-[#1E293B] rounded-xl p-8 text-center"
          >
            <h2 className="text-2xl font-bold text-[#2DD4BF] mb-4">
              Our Mission
            </h2>
            <p className="text-gray-400 max-w-3xl mx-auto">
              To empower journalists with intelligent automation tools that enhance their 
              workflow, enabling them to focus on what matters most - creating impactful 
              stories that inform and engage their audience.
            </p>
          </motion.div>

          {/* Footer */}
          <div className="mt-24 pb-12 border-t border-gray-800">
            <div className="pt-8 text-center text-sm text-gray-400">
              <p>© {new Date().getFullYear()} AuroraPress. All rights reserved.</p>
              <p className="mt-2">Empowering journalists with intelligent automation</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
} 