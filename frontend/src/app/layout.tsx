import React from 'react';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import ClientProviders from '@/components/providers/ClientProviders';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'AuroraPress - AI-Powered Digital Journalism',
  description: 'Revolutionizing digital journalism with AI-powered automation for independent journalists and small media teams.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gradient-to-br from-gray-900 to-gray-800 text-white min-h-screen`}>
        <ClientProviders>{children}</ClientProviders>
      </body>
    </html>
  );
} 