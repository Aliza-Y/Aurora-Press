'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  DocumentTextIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline';

const steps = [
  {
    id: 1,
    name: 'Input Content',
    description: 'Start by providing your raw content or topic ideas.',
    icon: DocumentTextIcon,
  },
  {
    id: 2,
    name: 'AI Processing',
    description: 'Our AI analyzes and enhances your content in real-time.',
    icon: ArrowPathIcon,
  },
  {
    id: 3,
    name: 'Review & Publish',
    description: 'Review the enhanced content and publish with confidence.',
    icon: CheckCircleIcon,
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
  hidden: { x: -20, opacity: 0 },
  visible: {
    x: 0,
    opacity: 1,
  },
};

export default function GuideSection() {
  return (
    <section id="guide" className="py-24 sm:py-32 relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-aurora-background via-aurora-background/50 to-aurora-background" />

      <div className="relative mx-auto max-w-7xl px-6 lg:px-8">
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
            Get Started in Minutes
          </motion.h2>
          <motion.p
            className="mt-6 text-lg leading-8 text-gray-300"
            variants={itemVariants}
          >
            Follow our simple guide to transform your content creation process
          </motion.p>
        </motion.div>

        <motion.div
          className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={containerVariants}
        >
          <div className="grid grid-cols-1 gap-y-12 lg:grid-cols-3 lg:gap-x-8">
            {steps.map((step, index) => (
              <motion.div
                key={step.id}
                className="relative"
                variants={itemVariants}
              >
                <div className="flex flex-col items-center">
                  {/* Step number with gradient border */}
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-r from-aurora-primary to-aurora-highlight p-[2px]">
                    <div className="flex h-full w-full items-center justify-center rounded-full bg-aurora-background">
                      <span className="text-lg font-semibold text-white">{step.id}</span>
                    </div>
                  </div>

                  {/* Step content */}
                  <div className="mt-6 text-center">
                    <h3 className="text-lg font-semibold text-white">{step.name}</h3>
                    <p className="mt-2 text-sm text-gray-400">{step.description}</p>
                  </div>

                  {/* Icon */}
                  <div className="mt-4">
                    <step.icon className="h-6 w-6 text-aurora-primary" aria-hidden="true" />
                  </div>

                  {/* Connector line */}
                  {index < steps.length - 1 && (
                    <div className="absolute top-6 left-full hidden lg:block">
                      <ArrowRightIcon className="h-6 w-6 text-aurora-primary mx-4" aria-hidden="true" />
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Call to action */}
        <motion.div
          className="mt-16 flex justify-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.6 }}
        >
          <motion.a
            href="#"
            className="group inline-flex items-center gap-x-2 rounded-full bg-gradient-to-r from-aurora-primary to-aurora-highlight px-6 py-3 text-base font-semibold text-white shadow-lg hover:shadow-aurora-primary/20"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Start Your Journey
            <ArrowRightIcon 
              className="h-5 w-5 transition-transform group-hover:translate-x-1" 
              aria-hidden="true" 
            />
          </motion.a>
        </motion.div>
      </div>
    </section>
  );
} 