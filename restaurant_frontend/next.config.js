/** @type {import('next').NextConfig} */
const nextConfig = {
  // 이미지 도메인 설정
  images: {
    domains: ['localhost', '192.168.45.44'],
  },
  
  // 개발 서버 허용 오리진 설정
  allowedDevOrigins: [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001", 
    "http://192.168.45.44:3000",
    "http://192.168.45.44:3001"
  ],
  
  // 개발 서버 설정
  experimental: {
    // 실험적 기능 비활성화
  },
  
  // WebSocket HMR 설정
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
      }
    }
    return config
  },
};

module.exports = nextConfig; 