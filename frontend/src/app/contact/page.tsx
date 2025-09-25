'use client';

import React from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { FaLinkedin, FaEnvelope, FaPhone, FaArrowLeft } from 'react-icons/fa';

const teamMembers = [
  {
    name: 'Aliza Yousaf',
    phone: '03094484977',
    email: 'Yousaffaliza@gmail.com',
    linkedin: 'https://www.linkedin.com/in/aliza-yousaf-307910259/',
    role: 'Team Lead',
    gradientFrom: '#2DD4BF',
    gradientTo: '#3B82F6'
  },
  {
    name: 'Muhammad Haris Awan',
    phone: '+92 300 2126000',
    email: 'harisawan015@gmail.com',
    linkedin: 'http://linkedin.com/in/haris-awan-1b46a6259',
    role: 'Full Stack Developer',
    gradientFrom: '#3B82F6',
    gradientTo: '#8B5CF6'
  },
  {
    name: 'Fatima Zafar',
    phone: '03001811965',
    email: 'syedafati4.5@gmail.com',
    linkedin: 'https://www.linkedin.com/in/fatimaai/',
    role: 'AI Specialist',
    gradientFrom: '#8B5CF6',
    gradientTo: '#EC4899'
  }
];

const ContactCard = ({ member, index }: { member: typeof teamMembers[0], index: number }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.2 }}
      className="relative group"
    >
      <div className="absolute inset-0 bg-gradient-to-r from-[#2DD4BF]/20 to-[#3B82F6]/20 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300 opacity-0 group-hover:opacity-100" />
      
      <div className="relative backdrop-blur-xl bg-[#1A1F2B]/90 rounded-2xl p-8 border border-[#2DD4BF]/10 shadow-xl hover:shadow-2xl transition-all duration-300">
        <div 
          className="absolute inset-0 rounded-2xl opacity-10"
          style={{
            background: `linear-gradient(135deg, ${member.gradientFrom}20, transparent 50%, ${member.gradientTo}20)`
          }}
        />
        
        <div className="relative z-10">
          <motion.h3 
            className="text-2xl font-bold mb-2"
            style={{
              background: `linear-gradient(to right, ${member.gradientFrom}, ${member.gradientTo})`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
          >
            {member.name}
          </motion.h3>
          <p className="text-gray-400 mb-4 text-sm">{member.role}</p>
          
          <div className="space-y-4">
            <motion.a
              href={`tel:${member.phone}`}
              className="flex items-center space-x-3 text-gray-300 hover:text-[#2DD4BF] transition-colors group"
              whileHover={{ x: 5 }}
            >
              <FaPhone className="w-4 h-4" />
              <span>{member.phone}</span>
            </motion.a>
            
            <motion.a
              href={`mailto:${member.email}`}
              className="flex items-center space-x-3 text-gray-300 hover:text-[#2DD4BF] transition-colors group"
              whileHover={{ x: 5 }}
            >
              <FaEnvelope className="w-4 h-4" />
              <span>{member.email}</span>
            </motion.a>
            
            <motion.a
              href={member.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-3 text-gray-300 hover:text-[#2DD4BF] transition-colors group"
              whileHover={{ x: 5 }}
            >
              <FaLinkedin className="w-4 h-4" />
              <span>LinkedIn Profile</span>
            </motion.a>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default function Contact() {
  return (
    <main className="min-h-screen bg-[#0D1117]">
      <div className="relative pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        {/* Back to Home Button */}
        <div className="max-w-7xl mx-auto relative">
          <Link 
            href="/"
            className="absolute -left-4 -top-12 flex items-center text-gray-400 hover:text-[#2DD4BF] transition-colors group"
          >
            <FaArrowLeft className="w-5 h-5 mr-2 transform group-hover:-translate-x-1 transition-transform" />
            <span>Back to Home</span>
          </Link>
        </div>

        {/* Background Effects */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-[#2DD4BF]/5 via-transparent to-transparent" />
          <div className="absolute inset-0 bg-grid-pattern opacity-10" />
        </div>
        
        <div className="max-w-7xl mx-auto relative">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-16"
          >
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="bg-gradient-to-r from-[#2DD4BF] to-[#3B82F6] bg-clip-text text-transparent">
                Meet Our Team
              </span>
            </h1>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Get in touch with our talented team members who are dedicated to revolutionizing journalism through AI innovation.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {teamMembers.map((member, index) => (
              <ContactCard key={member.name} member={member} index={index} />
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="mt-16 text-center"
          >
            <p className="text-gray-400">
              Want to learn more about AuroraPress?{' '}
              <Link href="/about" className="text-[#2DD4BF] hover:text-[#2DD4BF]/80 transition-colors">
                Visit our About page
              </Link>
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