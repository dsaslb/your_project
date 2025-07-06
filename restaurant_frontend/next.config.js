/** @type {import('next').NextConfig} */
const nextConfig = {
  // Next.js 15에서는 app 디렉토리가 기본으로 지원됨
  allowedDevOrigins: [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://192.168.45.44:3000",
    "http://192.168.45.44:3001"
  ]
}

module.exports = nextConfig; 