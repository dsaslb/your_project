/** @type {import('next').NextConfig} */
const nextConfig = {
  // App 디렉토리 경로 명시적 지정
  // experimental: {
  //   appDir: true,
  // },
  // App Router 경로 설정
  distDir: '.next',
  images: {
    domains: ['localhost', '192.168.45.44'],
  },
  // PWA 설정 (일시적으로 제거)
  // async headers() {
  //   return [
  //     {
  //       source: '/(.*)',
  //       headers: [
  //         {
  //           key: 'X-Frame-Options',
  //           value: 'DENY',
  //         },
  //         {
  //           key: 'X-Content-Type-Options',
  //           value: 'nosniff',
  //         },
  //         {
  //           key: 'Referrer-Policy',
  //           value: 'origin-when-cross-origin',
  //         },
  //       ],
  //     },
  //   ];
  // },
  // 모바일 최적화 (일시적으로 제거)
  // async rewrites() {
  //   return [
  //     {
  //       source: '/api/:path*',
  //       destination: 'http://192.168.45.44:5000/api/:path*',
  //     },
  //   ];
  // },
  allowedDevOrigins: [
    "http://localhost:3000",
    "http://192.168.45.44:3000"
  ],
};

module.exports = nextConfig; 