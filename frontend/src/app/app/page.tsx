'use client';

import React from 'react';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function AppPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to home page since /app is not a valid route
    router.replace('/');
  }, [router]);

  return (
    <div className="min-h-screen bg-aurora-background flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-aurora-primary mb-4">Redirecting...</h1>
        <p className="text-gray-400">Taking you to the homepage</p>
      </div>
    </div>
  );
} 