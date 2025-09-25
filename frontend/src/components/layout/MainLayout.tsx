'use client';

import { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { signOut } from 'next-auth/react';
import { IconHome, IconArticle, IconChartBar, IconBulb, IconLogout } from '@tabler/icons-react';

interface MainLayoutProps {
  children: ReactNode;
}

const MainLayout = ({ children }: MainLayoutProps) => {
  const pathname = usePathname();
  
  const navigationItems = [
    { name: 'Dashboard', href: '/dashboard', icon: IconHome },
    { name: 'My Articles', href: '/dashboard/articles', icon: IconArticle },
    { name: 'Audience Engagement', href: '/dashboard/engagement', icon: IconChartBar },
    { name: 'Recommendations', href: '/dashboard/recommendations', icon: IconBulb },
  ];

  const handleSignOut = async () => {
    await signOut({ callbackUrl: '/' });
  };

  return (
    <div className="min-h-screen bg-[#0F172A] text-gray-100 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-[#1E293B] fixed h-full">
        <div className="p-6">
          <Link href="/dashboard" className="text-[#2DD4BF] text-2xl font-bold hover:opacity-90 transition-opacity">
            AuroraPress
          </Link>
          
          <nav className="mt-8 space-y-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-[#2DD4BF] text-white'
                      : 'text-gray-400 hover:bg-gray-800/50'
                  }`}
                >
                  <Icon size={20} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>
        
        <div className="absolute bottom-0 w-full p-6">
          <button 
            onClick={handleSignOut}
            className="flex items-center gap-3 px-4 py-3 w-full text-gray-400 hover:bg-gray-800/50 rounded-lg transition-colors"
          >
            <IconLogout size={20} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-64 bg-[#0F172A]">
        {children}
      </main>
    </div>
  );
};

export default MainLayout; 