'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  NewspaperIcon,
  ChatBubbleBottomCenterTextIcon,
  ChartBarIcon,
  DocumentCheckIcon,
  MagnifyingGlassIcon,
  RocketLaunchIcon,
} from '@heroicons/react/24/outline';

const features = [
  {
    name: 'AI-Powered Trend Analysis',
    description: 'Automatically identify trending topics and emerging stories using advanced AI algorithms.',
    icon: ChartBarIcon,
  },
  {
    name: 'Automated Article Generation',
    description: 'Generate well-structured articles with AI while maintaining your unique writing style.',
    icon: NewspaperIcon,
  },
  {
    name: 'Smart Fact-Checking',
    description: 'Ensure accuracy with AI-driven fact verification and source validation.',
    icon: DocumentCheckIcon,
  },
  {
    name: 'SEO Optimization',
    description: 'Optimize content for search engines with AI-powered keyword and metadata suggestions.',
    icon: MagnifyingGlassIcon,
  },
  {
    name: 'Intelligent Publishing',
    description: 'Automate content distribution across multiple platforms with smart scheduling.',
    icon: RocketLaunchIcon,
  },
  {
    name: 'AI Assistant Chat',
    description: 'Get real-time writing suggestions and research assistance from your AI companion.',
    icon: ChatBubbleBottomCenterTextIcon,
  },
];

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5 }
};

export default function Features() {
  return (
    <section id="features" className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <motion.h2 
            className="text-3xl font-bold tracking-tight sm:text-4xl bg-gradient-to-r from-teal-400 to-blue-500 bg-clip-text text-transparent"
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            variants={fadeInUp}
          >
            Revolutionize Your Journalism Workflow
          </motion.h2>
          <motion.p 
            className="mt-6 text-lg leading-8 text-gray-300"
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            variants={fadeInUp}
          >
            Harness the power of AI to streamline your content creation process while maintaining journalistic integrity.
          </motion.p>
        </div>
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
            {features.map((feature, index) => (
              <motion.div 
                key={feature.name}
                className="flex flex-col"
                initial="initial"
                whileInView="animate"
                viewport={{ once: true }}
                variants={fadeInUp}
                transition={{ delay: index * 0.1 }}
              >
                <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-white">
                  <feature.icon className="h-5 w-5 flex-none text-teal-400" aria-hidden="true" />
                  {feature.name}
                </dt>
                <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-400">
                  <p className="flex-auto">{feature.description}</p>
                </dd>
              </motion.div>
            ))}
          </dl>
        </div>
      </div>
    </section>
  );
} 