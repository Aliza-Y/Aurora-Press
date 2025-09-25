'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

type StepNumber = 1 | 2;

type FormData = {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
};

export default function SignUp() {
  const router = useRouter();
  const [step, setStep] = useState<StepNumber>(1);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(''); // Clear error when user types
  };

  const validateStep1 = () => {
    if (!formData.firstName.trim()) {
      setError('Please enter your first name');
      return false;
    }
    if (!formData.lastName.trim()) {
      setError('Please enter your last name');
      return false;
    }
    if (!formData.email.trim()) {
      setError('Please enter your email address');
      return false;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }
    return true;
  };

  const validateStep2 = () => {
    if (!formData.password) {
      setError('Please enter a password');
      return false;
    }
    if (!formData.confirmPassword) {
      setError('Please confirm your password');
      return false;
    }
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    
    // Check password requirements
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    if (!passwordRegex.test(formData.password)) {
      setError(`Password must contain:
        • At least 8 characters
        • One uppercase letter (A-Z)
        • One lowercase letter (a-z)
        • One number (0-9)
        • One special character (@$!%*?&)`);
      return false;
    }
    return true;
  };

  const handleNextStep = () => {
    if (step === 1 && validateStep1()) {
      setStep(2);
    }
  };

  const handlePrevStep = () => {
    if (step > 1) {
      setStep(1);
      setError('');
    }
  };

  const handleSubmit = async () => {
    if (!validateStep2()) return;

    try {
      setLoading(true);
      setError('');

      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          firstName: formData.firstName,
          lastName: formData.lastName,
          email: formData.email,
          password: formData.password,
          confirmPassword: formData.confirmPassword
        }),
      });

      // Log response details for debugging
      console.log('Response status:', response.status);
      const contentType = response.headers.get('content-type');
      console.log('Content-Type:', contentType);

      // Handle non-JSON responses
      if (!contentType?.includes('application/json')) {
        const text = await response.text();
        console.error('Non-JSON response:', text);
        throw new Error('Server returned invalid response format');
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || 'Registration failed');
      }

      // Redirect to success page
      router.push('/auth/signup/success');
    } catch (err: any) {
      console.error('Registration error:', err);
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0D1117] p-4 relative overflow-hidden">
      {/* Back arrow */}
      <Link
        href="/auth"
        className="absolute top-8 left-8 text-gray-400 hover:text-[#2DD4BF] transition-colors z-10 flex items-center gap-2 group"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={2}
          stroke="currentColor"
          className="w-5 h-5 group-hover:-translate-x-1 transition-transform"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"
          />
        </svg>
        <span>Back to Login</span>
      </Link>

      {/* Background effects */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-[#2DD4BF]/10 via-[#3B82F6]/5 to-[#2DD4BF]/10" />
        <div className="absolute inset-0 bg-grid-pattern opacity-10" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl z-10"
      >
        {/* Progress bar */}
        <div className="mb-8 px-4">
          <div className="flex justify-between mb-2">
            {[1, 2].map((stepNumber) => (
              <motion.div
                key={stepNumber}
                className={`flex items-center ${step >= stepNumber ? 'text-[#2DD4BF]' : 'text-gray-500'}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: stepNumber * 0.2 }}
              >
                <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 
                  ${step > stepNumber ? 'bg-[#2DD4BF] border-[#2DD4BF]' : 
                    step === stepNumber ? 'border-[#2DD4BF]' : 'border-gray-500'}`}
                >
                  {step > stepNumber ? (
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <span className={`text-lg ${step === stepNumber ? 'text-[#2DD4BF]' : ''}`}>{stepNumber}</span>
                  )}
                </div>
                {stepNumber < 2 && (
                  <div className={`w-full h-1 mx-4 rounded-full transition-colors duration-300 ${step > stepNumber ? 'bg-[#2DD4BF]' : 'bg-gray-700'}`} />
                )}
              </motion.div>
            ))}
          </div>
        </div>

        <motion.div
          className="relative backdrop-blur-xl bg-[#1A1F2B]/90 rounded-2xl p-8 shadow-2xl border border-[#2DD4BF]/10"
          style={{
            boxShadow: '0 0 40px rgba(45, 212, 191, 0.1)',
          }}
          whileHover={{ scale: 1.01 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-[#2DD4BF]/20 via-[#3B82F6]/10 to-[#2DD4BF]/20 animate-gradient-xy" />

          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="relative"
            >
              <motion.h2
                className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#2DD4BF] to-[#3B82F6] mb-3 text-center"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                {step === 1 ? 'Personal Information' : 'Security Setup'}
              </motion.h2>
              
              <motion.p
                className="text-gray-400 text-center mb-10 text-lg"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
              >
                {step === 1 ? "Let's get to know you better" : 'Secure your AuroraPress account'}
              </motion.p>

              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-500 text-center"
                >
                  {error}
                </motion.div>
              )}

              {step === 1 ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="block text-gray-300 text-sm font-medium">First Name</label>
                      <motion.div
                        whileHover={{ scale: 1.01 }}
                        whileTap={{ scale: 0.99 }}
                      >
                        <input
                          type="text"
                          name="firstName"
                          value={formData.firstName}
                          onChange={handleInputChange}
                          className="w-full px-4 py-3 rounded-lg bg-[#0D1117]/80 border border-gray-700 text-white focus:outline-none focus:border-[#2DD4BF] focus:ring-1 focus:ring-[#2DD4BF] transition-all placeholder-gray-500"
                          placeholder="Enter first name"
                        />
                      </motion.div>
                    </div>
                    <div className="space-y-2">
                      <label className="block text-gray-300 text-sm font-medium">Last Name</label>
                      <motion.div
                        whileHover={{ scale: 1.01 }}
                        whileTap={{ scale: 0.99 }}
                      >
                        <input
                          type="text"
                          name="lastName"
                          value={formData.lastName}
                          onChange={handleInputChange}
                          className="w-full px-4 py-3 rounded-lg bg-[#0D1117]/80 border border-gray-700 text-white focus:outline-none focus:border-[#2DD4BF] focus:ring-1 focus:ring-[#2DD4BF] transition-all placeholder-gray-500"
                          placeholder="Enter last name"
                        />
                      </motion.div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="block text-gray-300 text-sm font-medium">Email Address</label>
                    <motion.div
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                    >
                      <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 rounded-lg bg-[#0D1117]/80 border border-gray-700 text-white focus:outline-none focus:border-[#2DD4BF] focus:ring-1 focus:ring-[#2DD4BF] transition-all placeholder-gray-500"
                        placeholder="Enter your email"
                      />
                    </motion.div>
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="space-y-2">
                    <label className="block text-gray-300 text-sm font-medium">Password</label>
                    <motion.div
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                    >
                      <input
                        type="password"
                        name="password"
                        value={formData.password}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 rounded-lg bg-[#0D1117]/80 border border-gray-700 text-white focus:outline-none focus:border-[#2DD4BF] focus:ring-1 focus:ring-[#2DD4BF] transition-all placeholder-gray-500"
                        placeholder="Create a strong password"
                      />
                    </motion.div>
                  </div>
                  <div className="space-y-2">
                    <label className="block text-gray-300 text-sm font-medium">Confirm Password</label>
                    <motion.div
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                    >
                      <input
                        type="password"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 rounded-lg bg-[#0D1117]/80 border border-gray-700 text-white focus:outline-none focus:border-[#2DD4BF] focus:ring-1 focus:ring-[#2DD4BF] transition-all placeholder-gray-500"
                        placeholder="Confirm your password"
                      />
                    </motion.div>
                  </div>
                </div>
              )}

              <div className="flex justify-between mt-10">
                {step > 1 && (
                  <motion.button
                    onClick={handlePrevStep}
                    className="px-8 py-3 rounded-lg border-2 border-[#2DD4BF] text-[#2DD4BF] hover:bg-[#2DD4BF]/10 transition-all duration-300 font-medium"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    disabled={loading}
                  >
                    Back
                  </motion.button>
                )}
                <motion.button
                  onClick={step === 1 ? handleNextStep : handleSubmit}
                  className={`px-8 py-3 rounded-lg font-medium ${
                    step === 2
                      ? 'bg-gradient-to-r from-[#2DD4BF] to-[#3B82F6] hover:opacity-90'
                      : 'bg-[#2DD4BF] hover:bg-[#2DD4BF]/90'
                  } text-white transition-all duration-300 ml-auto`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  disabled={loading}
                >
                  {loading ? (
                    <span className="flex items-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </span>
                  ) : (
                    step === 2 ? 'Create Account' : 'Next'
                  )}
                </motion.button>
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Login link */}
          <motion.div
            className="mt-6 text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <p className="text-gray-400">
              Already have an account?{' '}
              <Link href="/auth" className="text-[#2DD4BF] hover:text-[#2DD4BF]/80 transition-colors font-medium">
                Sign in
              </Link>
            </p>
          </motion.div>
        </motion.div>
      </motion.div>
    </div>
  );
} 