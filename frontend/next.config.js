/** @type {import('next').NextConfig} */

const FRONTEND_ORIGINS = [
  'http://localhost:3000',
  'http://localhost:3001',
  'http://192.168.45.44:3000',
  'http://192.168.45.44:3001',
];

const BACKEND_API = process.env.NEXT_PUBLIC_API_URL || 'http://192.168.45.44:5000';

const nextConfig = {
  // Turbopack 설정
  turbopack: {
    rules: {
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
    },
  },
  
  images: {
    domains: ['localhost', '192.168.45.44'],
  },
  
  // 정적 파일 설정
  assetPrefix: process.env.NODE_ENV === 'production' ? undefined : '',

  async headers() {
    return [
      {
        source: '/manifest.json',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      // 모든 경로에 CORS 헤더 추가
      {
        source: '/(.*)',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization, X-Requested-With, Accept' },
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
        ],
      },
      // Next.js 내부 리소스에 대한 특별한 헤더
      {
        source: '/_next/(.*)',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' },
        ],
      },
      {
        source: '/__nextjs_font/:all*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type' },
        ],
      },
      {
        source: '/_next/static/:all*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' },
        ],
      },
    ];
  },

  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${BACKEND_API}/api/:path*`,
      },
    ];
  },

  webpack: (config) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
    };
    return config;
  },
};

module.exports = nextConfig; 