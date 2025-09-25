'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { 
  IconRobot, 
  IconTrendingUp, 
  IconNews, 
  IconBrain,
  IconChecks,
  IconChartBar 
} from '@tabler/icons-react';

export default function Home() {
  const features = [
    {
      icon: IconRobot,
      title: 'AI-Powered Automation',
      description: 'Reduce editorial workload with intelligent agentic workflows handling routine tasks'
    },
    {
      icon: IconTrendingUp,
      title: 'Real-time Trend Detection',
      description: 'Stay ahead with AI-driven analysis of breaking news and emerging stories'
    },
    {
      icon: IconNews,
      title: 'Automated Publishing',
      description: 'Seamlessly publish to WordPress, social media, and other platforms'
    },
    {
      icon: IconBrain,
      title: 'Smart Research Assistant',
      description: 'Agentic workflows help with fact-checking, citations, and content enhancement'
    },
    {
      icon: IconChecks,
      title: 'Quality Assurance',
      description: 'Automated compliance checks, fact verification, and style adaptation'
    },
    {
      icon: IconChartBar,
      title: 'Engagement Analytics',
      description: 'Track performance and optimize content with detailed analytics'
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5,
        ease: "easeOut"
      }
    }
  };

  return (
    <div className="min-h-screen bg-[#0F172A] text-white">
      {/* Navigation */}
      <nav className="fixed w-full z-50 bg-[#0F172A]/80 backdrop-blur-lg border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link href="/" className="text-2xl font-bold text-[#2DD4BF]">
                AuroraPress
              </Link>
            </div>
            <div className="flex items-center space-x-6">
              <Link href="/how-to-use" className="text-gray-300 hover:text-[#2DD4BF] transition-colors">
                Features
              </Link>
              <Link href="/guide" className="text-gray-300 hover:text-[#2DD4BF] transition-colors">
                Guide
              </Link>
              <Link href="/pricing" className="text-gray-300 hover:text-[#2DD4BF] transition-colors">
                Pricing
              </Link>
              <Link href="/contact" className="text-gray-300 hover:text-[#2DD4BF] transition-colors">
                Contact
              </Link>
              <Link 
                href="/auth/login"
                className="text-gray-300 hover:text-[#2DD4BF] transition-colors"
              >
                Login
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
        className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto"
      >
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-center"
        >
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-[#2DD4BF] to-blue-500 text-transparent bg-clip-text">
            AI-Powered Journalism Platform
          </h1>
          <p className="text-xl text-gray-400 mb-8 max-w-3xl mx-auto">
            Empower your journalism workflow with AI automation. From trend detection to publishing, 
            AuroraPress helps independent journalists compete with major newsrooms by automating tedious tasks.
          </p>
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Link
              href="/auth/signup"
              className="bg-[#2DD4BF] text-[#0F172A] px-8 py-4 rounded-lg text-lg font-semibold hover:bg-[#2DD4BF]/90 transition-colors inline-block"
            >
              Start Your Journey
            </Link>
          </motion.div>
        </motion.div>

        {/* Animated Feature Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="mt-24 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="bg-[#1E293B] p-6 rounded-xl hover:bg-[#1E293B]/80 transition-colors"
            >
              <div className="w-12 h-12 bg-[#2DD4BF]/10 rounded-lg flex items-center justify-center mb-4">
                <feature.icon className="w-6 h-6 text-[#2DD4BF]" />
              </div>
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-400">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Workflow Animation */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="mt-24 bg-[#1E293B] rounded-2xl p-8 relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-[#2DD4BF]/10 to-blue-500/10 opacity-50" />
          <div className="relative z-10">
            <h2 className="text-3xl font-bold mb-8 text-center">Intelligent Workflow</h2>
            <div className="flex justify-center items-center space-x-4">
              <motion.div
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.5, 1, 0.5]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
                className="flex flex-col items-center"
              >
                <div className="w-3 h-3 bg-[#2DD4BF] rounded-full mb-2" />
                <span className="text-sm text-gray-400">Research</span>
              </motion.div>
              <div className="w-8 h-0.5 bg-[#2DD4BF]/30" />
              <motion.div
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.5, 1, 0.5]
                }}
                transition={{
                  duration: 2,
                  delay: 0.4,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
                className="flex flex-col items-center"
              >
                <div className="w-3 h-3 bg-[#2DD4BF] rounded-full mb-2" />
                <span className="text-sm text-gray-400">Write</span>
              </motion.div>
              <div className="w-8 h-0.5 bg-[#2DD4BF]/30" />
              <motion.div
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.5, 1, 0.5]
                }}
                transition={{
                  duration: 2,
                  delay: 0.8,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
                className="flex flex-col items-center"
              >
                <div className="w-3 h-3 bg-[#2DD4BF] rounded-full mb-2" />
                <span className="text-sm text-gray-400">Publish</span>
              </motion.div>
            </div>
            <p className="text-center text-gray-400 mt-8">
              Streamline your journalism workflow with intelligent automation
            </p>
          </div>
        </motion.div>

        <div className="mt-24 pb-12 border-t border-gray-800">
          <div className="pt-8 text-center text-sm text-gray-400">
            <p>© {new Date().getFullYear()} AuroraPress. All rights reserved.</p>
            <p className="mt-2">Empowering journalists with intelligent automation</p>
          </div>
        </div>
      </motion.div>
    </div>
  );
} 