'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { IconArrowLeft } from '@tabler/icons-react';

export default function HowToUsePage() {
  const features = [
    {
      title: 'Quality Assurance & Compliance',
      description: 'Automated fact-checking, ethical compliance, and journalistic standards verification.',
      steps: [
        'Automated fact verification against trusted sources',
        'Ethical compliance checks for journalistic standards',
        'Plagiarism detection and source validation',
        'Citation format standardization'
      ]
    },
    {
      title: 'Trend Analysis',
      description: 'Stay ahead with real-time trend detection and analysis.',
      steps: [
        'View trending topics in your field',
        'Analyze engagement metrics',
        'Track topic evolution over time',
        'Get story angle recommendations'
      ]
    },
    {
      title: 'Publishing Workflow',
      description: 'Streamline your publishing process with automated tools.',
      steps: [
        'Write or import your article',
        'Run automated quality checks',
        'Schedule publication time',
        'Monitor post-publishing metrics'
      ]
    }
  ];

  const additionalFeatures = [
    {
      title: 'Visual Content Generation',
      description: 'Create and enhance visual content with AI assistance'
    },
    {
      title: 'SEO Optimization',
      description: 'Automated keyword analysis and metadata optimization'
    },
    {
      title: 'Multi-Platform Publishing',
      description: 'Seamless publishing to WordPress, social media, and other platforms'
    },
    {
      title: 'Analytics Dashboard',
      description: 'Comprehensive metrics and engagement tracking'
    },
    {
      title: 'Research Assistant',
      description: 'Agentic workflows for source verification and content research'
    },
    {
      title: 'Collaboration Tools',
      description: 'Real-time editing and team collaboration features'
    }
  ];

  return (
    <div className="min-h-screen bg-[#0F172A] text-white pt-24 px-4 sm:px-6 lg:px-8">
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
            AuroraPress Features
          </h1>
          <p className="text-xl text-gray-400 mb-12">
            Comprehensive tools and workflows designed for modern journalism
          </p>

          <div className="space-y-12">
            {features.map((feature, index) => (
              <motion.section
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-[#1E293B] rounded-xl p-8"
              >
                <h2 className="text-2xl font-bold mb-4 text-[#2DD4BF]">{feature.title}</h2>
                <p className="text-gray-300 mb-6">{feature.description}</p>
                <div className="bg-[#0F172A] rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4 text-white">Key Capabilities:</h3>
                  <ol className="space-y-4">
                    {feature.steps.map((step, stepIndex) => (
                      <li key={stepIndex} className="flex items-start">
                        <span className="flex items-center justify-center w-6 h-6 rounded-full bg-[#2DD4BF] text-[#0F172A] text-sm font-bold mr-3">
                          {stepIndex + 1}
                        </span>
                        <span className="text-gray-300">{step}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              </motion.section>
            ))}

            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="bg-[#1E293B] rounded-xl p-8"
            >
              <h2 className="text-2xl font-bold mb-6 text-[#2DD4BF]">Additional Features</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {additionalFeatures.map((feature, index) => (
                  <div key={feature.title} className="bg-[#0F172A] rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-2 text-white">{feature.title}</h3>
                    <p className="text-gray-300">{feature.description}</p>
                  </div>
                ))}
              </div>
            </motion.section>
          </div>

          <div className="mt-24 pb-12 border-t border-gray-800">
            <div className="pt-8 text-center text-sm text-gray-400">
              <p>© {new Date().getFullYear()} AuroraPress. All rights reserved.</p>
              <p className="mt-2">Empowering journalists with intelligent automation</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
} 