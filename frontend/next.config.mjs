/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // ✅ Disable Webpack persistent cache to prevent OOM errors
  webpack: (config, { isServer }) => {
    config.cache = false;
    return config;
  },
  // (Optional) Turn off source maps in production to reduce build size
  productionBrowserSourceMaps: false,
  async rewrites() {
    return [
      {
        source: '/api/trends/:path*',
        destination: 'http://localhost:8000/api/trends/:path*',
      },
      {
        source: '/api/articles/:path*',
        destination: 'http://localhost:8000/api/articles/:path*',
      },
      {
        source: '/api/categories',
        destination: 'http://localhost:8000/api/categories',
      },
      {
        source: '/api/recommended-topics',
        destination: 'http://localhost:8000/api/recommended-topics',
      },
      {
        source: '/m9/:path*',
        destination: 'http://localhost:8000/m9/:path*',
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