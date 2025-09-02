/**
 * 모바일 앱 설정 파일
 * API URL 및 WebSocket URL 설정
 */
export default {
  expo: {
    name: "Your Program Mobile",
    slug: "your-program-mobile",
    version: "1.0.0",
    orientation: "portrait",
    icon: "./assets/icon.png",
    userInterfaceStyle: "light",
    splash: {
      image: "./assets/splash.png",
      resizeMode: "contain",
      backgroundColor: "#ffffff"
    },
    assetBundlePatterns: [
      "**/*"
    ],
    ios: {
      supportsTablet: true
    },
    android: {
      adaptiveIcon: {
        foregroundImage: "./assets/adaptive-icon.png",
        backgroundColor: "#FFFFFF"
      }
    },
    web: {
      favicon: "./assets/favicon.png"
    },
    extra: {
      // API 설정
      apiUrl: process.env.API_URL || "http://localhost:5000",
      wsUrl: process.env.WS_URL || "ws://localhost:5000",
      
      // 개발/프로덕션 환경 구분
      environment: process.env.NODE_ENV || "development",
      
      // 디버그 모드
      debug: process.env.DEBUG === "true" || false
    }
  }
};
