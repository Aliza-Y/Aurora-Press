import { ReactNode } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();
  
  return (
    <div className="min-h-screen bg-aurora-background">
      {/* Sidebar */}
      <div className="fixed left-0 top-0 h-full w-64 bg-aurora-card border-r border-aurora-secondary">
        <div className="p-6">
          <Link href="/" className="flex items-center space-x-2">
            <div className="text-2xl font-bold text-aurora-primary">AuroraPress</div>
          </Link>
        </div>
        <nav className="mt-6">
          <Link 
            href="/" 
            className={`flex items-center px-6 py-3 hover:bg-aurora-secondary ${
              router.pathname === '/' ? 'text-aurora-primary' : 'text-aurora-text-secondary'
            }`}
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            Dashboard
          </Link>
          <Link 
            href="/my-articles" 
            className={`flex items-center px-6 py-3 hover:bg-aurora-secondary ${
              router.pathname === '/my-articles' ? 'text-aurora-primary' : 'text-aurora-text-secondary'
            }`}
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9.5a2 2 0 00-2-2h-2" />
            </svg>
            My Articles
          </Link>
          <Link 
            href="/recommendations" 
            className={`flex items-center px-6 py-3 hover:bg-aurora-secondary ${
              router.pathname === '/recommendations' ? 'text-aurora-primary' : 'text-aurora-text-secondary'
            }`}
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Recommendations
          </Link>
          <Link 
            href="/trend-analysis" 
            className={`flex items-center px-6 py-3 hover:bg-aurora-secondary ${
              router.pathname === '/trend-analysis' ? 'text-aurora-primary' : 'text-aurora-text-secondary'
            }`}
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
            Trend Analysis
          </Link>
        </nav>

        <div className="absolute bottom-0 w-full p-4 border-t border-aurora-secondary">
          <button className="flex items-center w-full px-6 py-3 text-aurora-text-secondary hover:bg-aurora-secondary rounded-lg transition-colors">
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Sign Out
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64">
        <main className="p-4">
          {children}
        </main>
      </div>
    </div>
  );
} 