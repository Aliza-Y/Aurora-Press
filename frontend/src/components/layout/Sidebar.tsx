'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  IconHome, 
  IconArticle, 
  IconChartBar, 
  IconUsers, 
  IconBookUpload,
  IconStar,
  IconTrendingUp
} from '@tabler/icons-react';

const Sidebar = () => {
  const pathname = usePathname();

  const links = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: <IconHome className="w-5 h-5" />
    },
    {
      name: 'Recommendations',
      href: '/dashboard/recommendations',
      icon: <IconStar className="w-5 h-5" />
    },
    {
      name: 'My Articles',
      href: '/dashboard/articles',
      icon: <IconArticle className="w-5 h-5" />
    },
    {
      name: 'Published Articles',
      href: '/dashboard/published',
      icon: <IconBookUpload className="w-5 h-5" />
    },
    {
      name: 'Trend Analysis',
      href: '/dashboard/trend-analysis',
      icon: <IconChartBar className="w-5 h-5" />
    },
    {
      name: 'Engagement',
      href: '/dashboard/engagement',
      icon: <IconUsers className="w-5 h-5" />
    }
  ];

  return (
    <aside className="w-64 bg-[#1E293B] h-screen fixed left-0 top-0 p-4">
      <div className="mb-8">
        <Link href="/dashboard" className="text-2xl font-bold text-[#2DD4BF]">
          AuroraPress
        </Link>
      </div>
      
      <nav className="space-y-2">
        {links.map((link) => {
          const isActive = pathname === link.href;
          
          return (
            <Link
              key={link.name}
              href={link.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-[#2DD4BF] text-white'
                  : 'text-gray-400 hover:bg-gray-800'
              }`}
            >
              {link.icon}
              <span>{link.name}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
};

export default Sidebar; 