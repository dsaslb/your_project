import { ExpoConfig } from "expo/config";

const API_URL = process.env.API_URL ?? "http://192.168.45.44:5000"; // 개발 중엔 PC의 로컬 IP
const WS_URL = process.env.WS_URL ?? "ws://192.168.45.44:5000"; // WebSocket URL

const config: ExpoConfig = {
  name: "StaffApp",
  slug: "staff-app",
  scheme: "staffapp",
  version: "1.0.0",
  orientation: "portrait",
  icon: "./assets/icon.png",
  userInterfaceStyle: "light",
  newArchEnabled: true,
  splash: { 
    image: "./assets/splash-icon.png", 
    resizeMode: "contain", 
    backgroundColor: "#ffffff" 
  },
  ios: { 
    supportsTablet: true,
    bundleIdentifier: "com.yourcompany.staffapp" 
  },
  android: {
    package: "com.yourcompany.staffapp",
    adaptiveIcon: {
      foregroundImage: "./assets/adaptive-icon.png",
      backgroundColor: "#ffffff"
    },
    edgeToEdgeEnabled: true,
    permissions: [
      "ACCESS_FINE_LOCATION", 
      "ACCESS_COARSE_LOCATION", 
      "INTERNET", 
      "POST_NOTIFICATIONS",
      "CAMERA"
    ],
  },
  web: {
    favicon: "./assets/favicon.png"
  },
  extra: {
    apiUrl: API_URL,
    wsUrl: WS_URL,
    eas: { 
      projectId: "mobile-app-test" 
    }
  },
  plugins: [
    "expo-router",
    "expo-secure-store",
    "expo-sqlite"
  ]
};

export default config;
