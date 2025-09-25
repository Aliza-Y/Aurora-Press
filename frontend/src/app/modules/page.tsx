'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

const modules = [
  {
    id: 1,
    name: 'User Authentication & Privacy',
    description: 'Secure access and data protection for journalists',
    features: [
      'Multi-factor authentication',
      'Role-based access control',
      'Data encryption',
      'Privacy compliance tools'
    ]
  },
  {
    id: 2,
    name: 'Data Collection & Analysis',
    description: 'AI-powered research and trend identification',
    features: [
      'Real-time data scraping',
      'Trend analysis',
      'Pattern recognition',
      'Automated research'
    ]
  },
  {
    id: 3,
    name: 'AI Content Generation',
    description: 'Automated drafting with journalistic integrity',
    features: [
      'Smart content suggestions',
      'Style adaptation',
      'Multi-language support',
      'Template customization'
    ]
  },
  {
    id: 4,
    name: 'Visual & Multimedia',
    description: 'Automated visual content creation and editing',
    features: [
      'Image generation',
      'Video editing',
      'Infographic creation',
      'Media optimization'
    ]
  },
  {
    id: 5,
    name: 'SEO Optimization',
    description: 'Smart content optimization for digital reach',
    features: [
      'Keyword analysis',
      'Meta tag optimization',
      'Content structure suggestions',
      'Performance tracking'
    ]
  },
  {
    id: 6,
    name: 'Quality & Compliance',
    description: 'Ethical standards and fact verification',
    features: [
      'Fact-checking automation',
      'Source verification',
      'Bias detection',
      'Compliance monitoring'
    ]
  },
  {
    id: 7,
    name: 'Publishing & Distribution',
    description: 'Multi-channel content distribution system',
    features: [
      'Multi-platform publishing',
      'Social media integration',
      'Schedule management',
      'Analytics tracking'
    ]
  },
  {
    id: 8,
    name: 'Audience Analytics',
    description: 'Real-time engagement tracking and insights',
    features: [
      'Engagement metrics',
      'Audience segmentation',
      'Behavior analysis',
      'Performance reporting'
    ]
  },
  {
    id: 9,
    name: 'Newspaper Generation',
    description: 'Automated digital newspaper formatting',
    features: [
      'Layout automation',
      'Content organization',
      'Style customization',
      'Digital publishing'
    ]
  },
  {
    id: 10,
    name: 'Journalist Assistant',
    description: 'Personalized AI support for content creation',
    features: [
      'Writing assistance',
      'Research support',
      'Editing suggestions',
      'Workflow automation'
    ]
  },
  {
    id: 11,
    name: 'Audio Processing',
    description: 'Automated transcription and audio analysis',
    features: [
      'Speech-to-text',
      'Audio editing',
      'Voice analysis',
      'Podcast tools'
    ]
  },
  {
    id: 12,
    name: 'Workflow Orchestration',
    description: 'End-to-end content workflow management',
    features: [
      'Task automation',
      'Team collaboration',
      'Progress tracking',
      'Resource management'
    ]
  },
  {
    id: 13,
    name: 'Payment Management',
    description: 'Secure payment processing and subscription handling',
    features: [
      'Subscription management',
      'Payment processing',
      'Invoice generation',
      'Revenue tracking'
    ]
  }
];

export default function ModulesPage() {
  const router = useRouter();

  const handleStartClick = () => {
    router.push('/?start=true');
  };

  return (
    <main className="min-h-screen bg-[#0D1117]">
      <Navbar onStartClick={handleStartClick} />
      
      <section className="pt-32 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h1 className="text-4xl sm:text-5xl font-bold mb-6">
            <span className="bg-gradient-to-r from-[#2DD4BF] to-[#3B82F6] bg-clip-text text-transparent">
              Our Modules
            </span>
          </h1>
          <p className="text-gray-300 text-lg max-w-2xl mx-auto">
            Explore our comprehensive suite of AI-powered modules designed to revolutionize your journalism workflow
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {modules.map((module, index) => (
            <motion.div
              key={module.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-gray-800/50 rounded-xl p-6 hover:bg-gray-800/70 transition-all duration-300 border border-gray-700/50 hover:border-[#2DD4BF]/30"
            >
              <h3 className="text-xl font-semibold text-white mb-3">{module.name}</h3>
              <p className="text-gray-300 mb-4">{module.description}</p>
              <ul className="space-y-2">
                {module.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-center text-gray-400">
                    <svg
                      className="h-5 w-5 flex-none text-[#2DD4BF] mr-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      </section>

      <Footer />
    </main>
  );
} 