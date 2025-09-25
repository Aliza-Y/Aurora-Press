'use client';

import MainLayout from '@/components/layout/MainLayout';
import { IconArticle } from '@tabler/icons-react';

export default function PublishedArticles() {
  return (
    <MainLayout>
      <div className="flex flex-col items-center justify-center min-h-[60vh] p-8">
        <IconArticle className="w-16 h-16 text-gray-400 mb-4" />
        <h2 className="text-2xl font-semibold text-gray-700 mb-2">No Published Articles Yet</h2>
        <p className="text-gray-500 text-center max-w-md">
          When you publish your articles, they will appear here. Start by generating articles from trending topics in the dashboard.
        </p>
      </div>
    </MainLayout>
  );
} 