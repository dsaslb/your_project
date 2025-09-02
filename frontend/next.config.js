/** @type {import('next').NextConfig} */
const nextConfig = {
  // 실험적 기능 비활성화
  experimental: {
    optimizeCss: false,
  },

  // 이미지 최적화
  images: {
    domains: ['localhost', '192.168.45.44'],
  },

  // 웹팩 설정
  webpack: (config) => {
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });
    return config;
  },

  // 헤더 보안 설정
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; connect-src 'self' http://192.168.45.44:5000 http://localhost:5000 ws://localhost:5000 ws://192.168.45.44:5000; img-src 'self' data: https:; object-src 'none'; base-uri 'self'; form-action 'self';",
          },
        ],
      },
    ];
  },

  // 리다이렉트 설정
  async redirects() {
    return [
      {
        source: '/',
        destination: '/dashboard',
        permanent: false,
      },
    ];
  },
};

module.exports = nextConfig; 