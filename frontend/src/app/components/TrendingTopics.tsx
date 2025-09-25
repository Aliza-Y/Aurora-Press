'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';

const categories = [
  { id: 'all', name: 'All' },
  { id: 'politics', name: 'Politics' },
  { id: 'technology', name: 'Technology' },
  { id: 'science', name: 'Science' },
  { id: 'business', name: 'Business' },
  { id: 'entertainment', name: 'Entertainment' },
  { id: 'sports', name: 'Sports' },
];

export default function TrendingTopics() {
  const [activeCategory, setActiveCategory] = useState('all');

  return (
    <section className="py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Trending Topics</h2>
          <p className="text-gray-400">Discover and approve trending topics for article generation</p>
        </div>

        {/* Category filters with improved visibility */}
        <div className="flex flex-wrap gap-3 mb-8">
          {categories.map((category) => (
            <motion.button
              key={category.id}
              onClick={() => setActiveCategory(category.id)}
              className={`
                px-4 py-2 rounded-full text-sm font-medium transition-all duration-200
                ${activeCategory === category.id
                  ? 'bg-aurora-primary text-white shadow-lg shadow-aurora-primary/20 border border-aurora-primary/50'
                  : 'bg-[#1e2a4a] text-white hover:bg-aurora-secondary/30 border border-aurora-secondary/30'
                }
              `}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {category.name}
            </motion.button>
          ))}
        </div>

        {/* Trend cards would go here */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Your trend cards content */}
        </div>
      </div>
    </section>
  );
} 