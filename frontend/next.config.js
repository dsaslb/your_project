/** @type {import('next').NextConfig} */
const nextConfig = {
  // Turbopack 설정 (안정화됨)
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
  
  // CORS 및 개발 환경 설정 - 더 포괄적으로
  allowedDevOrigins: [
    'http://192.168.45.44:3000',
    'http://192.168.45.44:3001',
    'http://localhost:3000',
    'http://localhost:3001',
    'ws://192.168.45.44:3000',
    'ws://192.168.45.44:3001',
    'ws://localhost:3000',
    'ws://localhost:3001',
    'wss://192.168.45.44:3000',
    'wss://192.168.45.44:3001',
    'wss://localhost:3000',
    'wss://localhost:3001',
  ],

  // Turbopack 사용으로 webpack 설정 제거

  // 개발 서버 설정 (deprecated 옵션 제거)

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
          // 여러 Origin 지원: 개발 시 Access-Control-Allow-Origin을 요청 Origin으로 동적 처리 권장(실제 배포는 Nginx 등에서 처리)
          { key: 'Access-Control-Allow-Origin', value: '*', },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization, X-Requested-With, Accept' },
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
        ],
      },
      // 정적 리소스에 대한 특별한 헤더
      {
        source: '/_next/(.*)',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: FRONTEND_ORIGINS[0] },
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

const FRONTEND_ORIGINS = [
  'http://localhost:3000',
  'http://localhost:3001',
  'http://192.168.45.44:3000',
  'http://192.168.45.44:3001',
];
const BACKEND_API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

module.exports = {
  ...nextConfig,
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
      {
        source: '/(.*)',
        headers: [
          // 여러 Origin 지원: 개발 시 Access-Control-Allow-Origin을 요청 Origin으로 동적 처리 권장(실제 배포는 Nginx 등에서 처리)
          { key: 'Access-Control-Allow-Origin', value: '*', },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization, X-Requested-With, Accept' },
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
        ],
      },
      {
        source: '/_next/(.*)',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: FRONTEND_ORIGINS[0] },
          { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' },
        ],
      },
      {
        source: '/__nextjs_font/:all*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: FRONTEND_ORIGINS[0] },
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
}; 