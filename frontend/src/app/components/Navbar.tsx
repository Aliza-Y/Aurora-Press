'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';
import Link from 'next/link';
import { useSession, signOut } from 'next-auth/react';
import { usePathname } from 'next/navigation';

const navigation = [
  { name: 'Features', href: '/#features' },
  { name: 'Guide', href: '/#guide' },
  { name: 'Pricing', href: '/#pricing' },
];

export default function Navbar() {
  const { data: session, status } = useSession();
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const pathname = usePathname();
  const isHomePage = pathname === '/';

  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 10;
      if (isScrolled !== scrolled) {
        setScrolled(isScrolled);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [scrolled]);

  const handleSignOut = async () => {
    await signOut({ callbackUrl: '/' });
  };

  return (
    <motion.header
      className={`fixed w-full z-50 transition-colors duration-300 ${
        scrolled || !isHomePage ? 'bg-aurora-background/80 backdrop-blur-md' : 'bg-transparent'
      }`}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <nav className="mx-auto flex max-w-7xl items-center justify-between p-6 lg:px-8" aria-label="Global">
        <div className="flex lg:flex-1">
          <Link href="/" className="-m-1.5 p-1.5">
            <span className="sr-only">AuroraPress</span>
            <motion.span 
              className="text-2xl font-bold bg-gradient-to-r from-aurora-primary to-aurora-highlight bg-clip-text text-transparent"
              whileHover={{ scale: 1.05 }}
            >
              AuroraPress
            </motion.span>
          </Link>
        </div>
        <div className="flex lg:hidden">
          <button
            type="button"
            className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-gray-400"
            onClick={() => setIsOpen(true)}
          >
            <span className="sr-only">Open main menu</span>
            <Bars3Icon className="h-6 w-6" aria-hidden="true" />
          </button>
        </div>
        <div className="hidden lg:flex lg:gap-x-12">
          {isHomePage && navigation.map((item) => (
            <motion.a
              key={item.name}
              href={item.href}
              className="text-sm font-semibold leading-6 text-gray-300 hover:text-aurora-primary transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {item.name}
            </motion.a>
          ))}
          {!isHomePage && (
            <Link href="/" className="text-sm font-semibold leading-6 text-gray-300 hover:text-aurora-primary transition-colors">
              Home
            </Link>
          )}
          {session?.user && (
            <Link href="/dashboard" className="text-sm font-semibold leading-6 text-gray-300 hover:text-aurora-primary transition-colors">
              Dashboard
            </Link>
          )}
        </div>
        <div className="hidden lg:flex lg:flex-1 lg:justify-end lg:gap-x-4">
          {status === 'authenticated' ? (
            <>
              <motion.button
                onClick={handleSignOut}
                className="text-sm font-semibold leading-6 text-gray-300 hover:text-aurora-primary transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Sign Out
              </motion.button>
              <Link href="/dashboard">
                <motion.span
                  className="rounded-full bg-gradient-to-r from-aurora-primary to-aurora-highlight px-4 py-2 text-sm font-semibold text-white shadow-lg hover:shadow-aurora-primary/20"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Dashboard
                </motion.span>
              </Link>
            </>
          ) : (
            <>
              <Link href="/auth">
                <motion.span
                  className="text-sm font-semibold leading-6 text-gray-300 hover:text-aurora-primary transition-colors"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Sign In
                </motion.span>
              </Link>
              <Link href="/auth/signup">
                <motion.span
                  className="rounded-full bg-gradient-to-r from-aurora-primary to-aurora-highlight px-4 py-2 text-sm font-semibold text-white shadow-lg hover:shadow-aurora-primary/20"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Get Started
                </motion.span>
              </Link>
            </>
          )}
        </div>
      </nav>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="lg:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="fixed inset-0 z-50">
              <motion.div
                className="fixed inset-y-0 right-0 z-50 w-full overflow-y-auto bg-aurora-background px-6 py-6 sm:max-w-sm sm:ring-1 sm:ring-gray-900/10"
                initial={{ x: "100%" }}
                animate={{ x: 0 }}
                exit={{ x: "100%" }}
                transition={{ type: "spring", damping: 25, stiffness: 200 }}
              >
                <div className="flex items-center justify-between">
                  <Link href="/" className="-m-1.5 p-1.5">
                    <span className="sr-only">AuroraPress</span>
                    <span className="text-2xl font-bold bg-gradient-to-r from-aurora-primary to-aurora-highlight bg-clip-text text-transparent">
                      AuroraPress
                    </span>
                  </Link>
                  <button
                    type="button"
                    className="-m-2.5 rounded-md p-2.5 text-gray-400"
                    onClick={() => setIsOpen(false)}
                  >
                    <span className="sr-only">Close menu</span>
                    <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                  </button>
                </div>
                <div className="mt-6 flow-root">
                  <div className="-my-6 divide-y divide-gray-500/10">
                    <div className="space-y-2 py-6">
                      {isHomePage && navigation.map((item) => (
                        <motion.a
                          key={item.name}
                          href={item.href}
                          className="-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-gray-300 hover:bg-aurora-card"
                          whileHover={{ x: 10 }}
                          onClick={() => setIsOpen(false)}
                        >
                          {item.name}
                        </motion.a>
                      ))}
                      {!isHomePage && (
                        <Link href="/" className="-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-gray-300 hover:bg-aurora-card">
                          Home
                        </Link>
                      )}
                      {session?.user && (
                        <Link href="/dashboard" className="-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-gray-300 hover:bg-aurora-card">
                          Dashboard
                        </Link>
                      )}
                    </div>
                    <div className="py-6">
                      {status === 'authenticated' ? (
                        <>
                          <motion.button
                            onClick={handleSignOut}
                            className="-mx-3 block w-full rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-gray-300 hover:bg-aurora-card"
                            whileHover={{ x: 10 }}
                          >
                            Sign Out
                          </motion.button>
                          <Link href="/dashboard" onClick={() => setIsOpen(false)}>
                            <motion.span
                              className="-mx-3 mt-3 block rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-white bg-gradient-to-r from-aurora-primary to-aurora-highlight"
                              whileHover={{ x: 10 }}
                            >
                              Dashboard
                            </motion.span>
                          </Link>
                        </>
                      ) : (
                        <>
                          <Link href="/auth" onClick={() => setIsOpen(false)}>
                            <motion.span
                              className="-mx-3 block rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-gray-300 hover:bg-aurora-card"
                              whileHover={{ x: 10 }}
                            >
                              Sign In
                            </motion.span>
                          </Link>
                          <Link href="/auth/signup" onClick={() => setIsOpen(false)}>
                            <motion.span
                              className="-mx-3 mt-3 block rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-white bg-gradient-to-r from-aurora-primary to-aurora-highlight"
                              whileHover={{ x: 10 }}
                            >
                              Get Started
                            </motion.span>
                          </Link>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
} 