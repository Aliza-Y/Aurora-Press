'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { IconArrowLeft } from '@tabler/icons-react';

export default function PricingPage() {
  const plans = [
    {
      name: 'Basic',
      price: '$19',
      features: [
        'Smart Research Assistant',
        'Basic Trend Detection',
        'Manual Publishing',
        'Email Support'
      ]
    },
    {
      name: 'Professional',
      price: '$49',
      features: [
        'All Basic features',
        'Advanced Trend Analysis',
        'Automated Publishing',
        'Priority Support',
        'Quality Assurance Tools'
      ]
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      features: [
        'All Professional features',
        'Custom Workflows',
        'API Access',
        'Dedicated Support',
        'Custom Integrations'
      ]
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
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-[#2DD4BF] to-blue-500 text-transparent bg-clip-text">
            Choose Your Plan
          </h1>
          <p className="text-gray-400">
            Select the perfect plan for your journalism needs
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-[#1E293B] rounded-xl p-6 flex flex-col"
            >
              <h2 className="text-2xl font-bold mb-2">{plan.name}</h2>
              <div className="text-3xl font-bold text-[#2DD4BF] mb-6">{plan.price}</div>
              <ul className="space-y-3 mb-8 flex-grow">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center text-gray-300">
                    <svg className="w-5 h-5 text-[#2DD4BF] mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>
              <Link
                href="/auth/signup"
                className="block w-full py-2 px-4 bg-[#2DD4BF] text-[#0F172A] rounded-lg text-center font-semibold hover:bg-[#2DD4BF]/90 transition-colors"
              >
                Get Started
              </Link>
            </motion.div>
          ))}
        </div>

        <div className="mt-24 pb-12 border-t border-gray-800">
          <div className="pt-8 text-center text-sm text-gray-400">
            <p>© {new Date().getFullYear()} AuroraPress. All rights reserved.</p>
            <p className="mt-2">Empowering journalists with intelligent automation</p>
          </div>
        </div>
      </div>
    </div>
  );
} 