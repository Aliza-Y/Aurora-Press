/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    serverActions: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/approve_trend/:path*',
        destination: 'http://localhost:5000/approve_trend/:path*',
      },
    ];
  },
  images: {
    domains: ['localhost'],
  },
  typescript: {
    ignoreBuildErrors: true,
  }
};

export default nextConfig; 