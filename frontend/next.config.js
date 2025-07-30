/** @type {import('next').NextConfig} */
const nextConfig = {
  // 성능 최적화 설정
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
  },
  
  // 이미지 최적화
  images: {
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
  
  // 번들 분석
  webpack: (config, { dev, isServer }) => {
    // 프로덕션 빌드에서만 번들 분석
    if (!dev && !isServer) {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: false,
          reportFilename: '../bundle-analysis.html',
        })
      );
    }
    
    // 트리 쉐이킹 최적화
    config.optimization = {
      ...config.optimization,
      usedExports: true,
      sideEffects: false,
    };
    
    return config;
  },
  
  // 압축 설정
  compress: true,
  
  // 캐싱 설정
  generateEtags: true,
  
  // 보안 헤더
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ];
  },
  

  
  // 환경 변수
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  
  // 타입스크립트 설정
  typescript: {
    ignoreBuildErrors: false,
  },
  
  // ESLint 설정
  eslint: {
    ignoreDuringBuilds: false,
  },
  
  // 리다이렉트 설정
  async redirects() {
    return [
      {
        source: '/',
        destination: '/dashboard',
        permanent: false,  // 개발용이므로 임시 리다이렉트
      },
    ];
  },
};

module.exports = nextConfig; 