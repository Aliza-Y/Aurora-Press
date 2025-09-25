'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, useAnimation } from 'framer-motion';

const processSteps = [
  {
    id: 'input',
    title: 'Content Input',
    description: 'Raw content analysis in progress',
    color: '#2DD4BF'
  },
  {
    id: 'process',
    title: 'AI Processing',
    description: 'Neural network enhancement',
    color: '#3B82F6'
  },
  {
    id: 'optimize',
    title: 'Smart Optimization',
    description: 'Advanced content refinement',
    color: '#8B5CF6'
  },
  {
    id: 'output',
    title: 'Final Output',
    description: 'Publishing-ready content',
    color: '#EC4899'
  }
];

export default function ArticleEvolution() {
  const [activeStep, setActiveStep] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const controls = useAnimation();

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % processSteps.length);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    controls.start({
      background: [
        `radial-gradient(circle at center, ${processSteps[activeStep].color}22 0%, transparent 70%)`,
        `radial-gradient(circle at center, ${processSteps[activeStep].color}44 0%, transparent 70%)`,
        `radial-gradient(circle at center, ${processSteps[activeStep].color}22 0%, transparent 70%)`
      ],
      transition: {
        duration: 2,
        ease: "easeInOut",
        repeat: Infinity
      }
    });
  }, [activeStep, controls]);

  return (
    <div className="relative w-full max-w-4xl mx-auto h-[500px] rounded-xl overflow-hidden bg-[#0D1117] border border-gray-800">
      <motion.div
        ref={containerRef}
        className="absolute inset-0"
        animate={controls}
      />

      {/* Rest of the component implementation */}
      {/* Hexagonal Grid Background */}
      <div className="absolute inset-0 opacity-20">
        {Array.from({ length: 20 }).map((_, i) => (
          <div
            key={`hex-${i}`}
            className="absolute w-20 h-20 border border-gray-700"
            style={{
              clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              transform: 'translate(-50%, -50%)',
            }}
          />
        ))}
      </div>

      {/* Content Transformation */}
      <div className="relative h-full flex items-center justify-center">
        <motion.div
          key={activeStep}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 1.2 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          {/* Step Title */}
          <motion.h3
            className="text-3xl font-bold mb-4"
            style={{ color: processSteps[activeStep].color }}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            {processSteps[activeStep].title}
          </motion.h3>

          {/* Dynamic Content Visualization */}
          <div className="relative w-96 h-48 mx-auto mb-6">
            {/* Content Lines */}
            {Array.from({ length: 6 }).map((_, i) => (
              <motion.div
                key={`line-${i}`}
                className="h-3 rounded-full my-3"
                style={{
                  backgroundColor: `${processSteps[activeStep].color}22`,
                  width: `${Math.random() * 40 + 60}%`,
                  marginLeft: `${Math.random() * 20}%`
                }}
                initial={{ scaleX: 0, opacity: 0 }}
                animate={{ scaleX: 1, opacity: 1 }}
                transition={{ delay: i * 0.1 }}
              />
            ))}

            {/* Processing Effects */}
            <motion.div
              className="absolute inset-0"
              animate={{
                background: [
                  `linear-gradient(90deg, transparent, ${processSteps[activeStep].color}44, transparent)`,
                  `linear-gradient(90deg, transparent, ${processSteps[activeStep].color}00, transparent)`
                ],
                x: ['-100%', '200%']
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "linear"
              }}
            />
          </div>

          {/* Processing Status */}
          <motion.div
            className="text-lg text-gray-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            {processSteps[activeStep].description}
          </motion.div>

          {/* Progress Indicator */}
          <div className="flex justify-center mt-8 space-x-2">
            {processSteps.map((_, index) => (
              <motion.div
                key={`indicator-${index}`}
                className="w-2 h-2 rounded-full"
                style={{
                  backgroundColor: index === activeStep ? processSteps[activeStep].color : '#1F2937'
                }}
                animate={{
                  scale: index === activeStep ? [1, 1.2, 1] : 1
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
            ))}
          </div>
        </motion.div>
      </div>

      {/* Energy Flow Lines */}
      <div className="absolute inset-0 pointer-events-none">
        {Array.from({ length: 8 }).map((_, i) => (
          <motion.div
            key={`flow-${i}`}
            className="absolute h-px"
            style={{
              background: `linear-gradient(90deg, transparent, ${processSteps[activeStep].color}, transparent)`,
              top: `${Math.random() * 100}%`,
              left: 0,
              right: 0,
            }}
            animate={{
              opacity: [0, 1, 0],
              scaleX: [0, 1, 0],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: i * 0.3,
              ease: "linear"
            }}
          />
        ))}
      </div>
    </div>
  );
} 