'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { CheckIcon } from '@heroicons/react/24/outline';

const tiers = [
  {
    name: 'Starter',
    id: 'tier-starter',
    price: '$29',
    description: 'Perfect for individual content creators and bloggers.',
    features: [
      'Up to 10 articles per month',
      'Basic trend analysis',
      'Standard AI templates',
      'Email support',
      'Basic analytics',
    ],
    gradient: 'from-teal-400 to-blue-500',
  },
  {
    name: 'Professional',
    id: 'tier-professional',
    price: '$79',
    description: 'Ideal for professional writers and small publications.',
    features: [
      'Up to 50 articles per month',
      'Advanced trend analysis',
      'Custom AI templates',
      'Priority support',
      'Advanced analytics',
      'API access',
      'Team collaboration',
    ],
    gradient: 'from-blue-500 to-purple-500',
    featured: true,
  },
  {
    name: 'Enterprise',
    id: 'tier-enterprise',
    price: '$199',
    description: 'For large publications and media organizations.',
    features: [
      'Unlimited articles',
      'Real-time trend analysis',
      'Custom AI model training',
      '24/7 dedicated support',
      'Enterprise analytics',
      'Full API access',
      'Advanced team management',
      'Custom integrations',
    ],
    gradient: 'from-purple-500 to-pink-500',
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
  },
};

export default function Pricing() {
  return (
    <section id="pricing" className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <motion.div
          className="mx-auto max-w-2xl text-center"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={containerVariants}
        >
          <motion.h2
            className="text-3xl font-bold tracking-tight sm:text-4xl bg-gradient-to-r from-aurora-primary to-aurora-highlight bg-clip-text text-transparent"
            variants={itemVariants}
          >
            Choose Your Plan
          </motion.h2>
          <motion.p
            className="mt-6 text-lg leading-8 text-gray-300"
            variants={itemVariants}
          >
            Select the perfect plan for your content creation needs
          </motion.p>
        </motion.div>

        <motion.div
          className="mx-auto mt-16 grid max-w-lg grid-cols-1 gap-8 lg:max-w-none lg:grid-cols-3"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={containerVariants}
        >
          {tiers.map((tier) => (
            <motion.div
              key={tier.id}
              className={`relative flex flex-col justify-between rounded-3xl bg-aurora-card ring-1 ring-gray-700/80 ${
                tier.featured ? 'lg:z-10 lg:scale-105' : ''
              }`}
              variants={itemVariants}
              whileHover={{ scale: tier.featured ? 1.02 : 1.05 }}
            >
              {/* Gradient border */}
              <div
                className="absolute inset-0 rounded-3xl bg-gradient-to-r opacity-10"
                style={{
                  backgroundImage: `linear-gradient(to right, ${tier.gradient})`,
                }}
              />

              <div className="p-8 sm:p-10">
                <h3
                  className="text-lg font-semibold leading-8 bg-gradient-to-r bg-clip-text text-transparent"
                  style={{
                    backgroundImage: `linear-gradient(to right, ${tier.gradient})`,
                  }}
                >
                  {tier.name}
                </h3>
                <p className="mt-4 text-sm leading-6 text-gray-300">{tier.description}</p>
                <p className="mt-6 flex items-baseline gap-x-1">
                  <span className="text-4xl font-bold tracking-tight text-white">{tier.price}</span>
                  <span className="text-sm font-semibold leading-6 text-gray-300">/month</span>
                </p>
                <ul role="list" className="mt-8 space-y-3 text-sm leading-6 text-gray-300">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex gap-x-3">
                      <CheckIcon
                        className={`h-6 w-5 flex-none`}
                        style={{
                          backgroundImage: `linear-gradient(to right, ${tier.gradient})`,
                          WebkitBackgroundClip: 'text',
                          WebkitTextFillColor: 'transparent',
                        }}
                        aria-hidden="true"
                      />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="flex flex-col p-6">
                <motion.a
                  href="#"
                  className={`rounded-full px-4 py-2.5 text-center text-sm font-semibold leading-6 text-white shadow-sm bg-gradient-to-r ${tier.gradient}`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Get Started
                </motion.a>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
} 