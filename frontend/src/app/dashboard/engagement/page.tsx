'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { IconChartBar, IconUsers, IconMessageCircle } from '@tabler/icons-react';
import MainLayout from '@/components/layout/MainLayout';

export default function EngagementDashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/');
    }
  }, [status, router]);

  const features = [
    {
      icon: <IconChartBar className="w-12 h-12 text-[#2DD4BF]" />,
      title: "Engagement Metrics",
      description: "Track how readers interact with your articles over time"
    },
    {
      icon: <IconUsers className="w-12 h-12 text-[#2DD4BF]" />,
      title: "Audience Demographics",
      description: "Understand your reader base across different segments"
    },
    {
      icon: <IconMessageCircle className="w-12 h-12 text-[#2DD4BF]" />,
      title: "Reader Feedback",
      description: "Analyze comments and reactions to improve content"
    }
  ];

  return (
    <MainLayout>
      <div className="flex flex-col items-center justify-center min-h-[80vh] p-8 text-center">
        {/* Icon */}
        <div className="mb-6 bg-[#2DD4BF]/10 p-6 rounded-full">
          <IconChartBar className="w-16 h-16 text-[#2DD4BF]" />
        </div>

        {/* Title and Description */}
        <h1 className="text-3xl font-bold text-white mb-4">
          Audience Engagement Dashboard Coming Soon
        </h1>
        <p className="text-gray-400 mb-12 max-w-2xl">
          We're building powerful engagement tools to help you understand your audience better and create more impactful content.
        </p>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl w-full">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-[#1E293B] p-6 rounded-xl flex flex-col items-center text-center group hover:bg-gray-800/50 transition-colors"
            >
              <div className="bg-[#2DD4BF]/10 p-4 rounded-full mb-4 group-hover:bg-[#2DD4BF]/20 transition-colors">
                {feature.icon}
              </div>
              <h3 className="text-white font-semibold mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-400 text-sm">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Coming Soon Badge */}
        <div className="mt-12">
          <span className="px-4 py-2 bg-[#2DD4BF]/10 text-[#2DD4BF] rounded-full text-sm font-medium">
            Coming in Future Update
          </span>
        </div>
      </div>
    </MainLayout>
  );
} 