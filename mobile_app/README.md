# 레스토랑 관리 모바일 앱

React Native와 Expo를 사용한 레스토랑 관리 모바일 애플리케이션입니다.

## 주요 기능

- 🔐 사용자 인증 (로그인/로그아웃)
- 📊 대시보드 (주문 현황, 재고 알림, 직원 출근)
- 👥 직원 관리
- 📦 재고 관리
- 🛒 주문 관리
- ⚙️ 설정

## 기술 스택

- **React Native** - 모바일 앱 개발
- **Expo** - 개발 도구 및 배포 플랫폼
- **TypeScript** - 타입 안전성
- **React Navigation** - 네비게이션
- **AsyncStorage** - 로컬 데이터 저장
- **Expo Notifications** - 푸시 알림
- **Axios** - HTTP 클라이언트

## 설치 및 실행

### 1. 의존성 설치

```bash
npm install
```

### 2. 개발 서버 실행

```bash
# Expo 개발 서버 시작
npm start

# 또는
expo start
```

### 3. 모바일 앱에서 실행

1. Expo Go 앱을 스마트폰에 설치
2. QR 코드를 스캔하여 앱 실행

### 4. 시뮬레이터에서 실행

```bash
# iOS 시뮬레이터
npm run ios

# Android 에뮬레이터
npm run android
```

## 프로젝트 구조

```
mobile_app/
├── src/
│   ├── contexts/          # React Context
│   │   ├── AuthContext.tsx
│   │   └── NetworkContext.tsx
│   ├── screens/           # 화면 컴포넌트
│   │   ├── DashboardScreen.tsx
│   │   ├── StaffScreen.tsx
│   │   ├── InventoryScreen.tsx
│   │   ├── OrdersScreen.tsx
│   │   ├── SettingsScreen.tsx
│   │   └── LoginScreen.tsx
│   ├── services/          # API 서비스
│   │   └── apiClient.ts
│   └── navigation/        # 네비게이션
├── assets/               # 이미지 및 아이콘
├── App.tsx              # 메인 앱 컴포넌트
├── package.json         # 의존성 관리
├── tsconfig.json        # TypeScript 설정
├── babel.config.js      # Babel 설정
└── app.json            # Expo 설정
```

## 환경 설정

### 백엔드 API 연결

`src/services/apiClient.ts` 파일에서 백엔드 API URL을 설정하세요:

```typescript
const API_BASE_URL = 'http://your-backend-url.com';
```

### 환경 변수

`.env` 파일을 생성하여 환경 변수를 설정할 수 있습니다:

```env
API_BASE_URL=http://localhost:5000
EXPO_PUBLIC_API_URL=http://localhost:5000
```

## 빌드 및 배포

### Android APK 빌드

```bash
expo build:android
```

### iOS IPA 빌드

```bash
expo build:ios
```

### 웹 빌드

```bash
expo build:web
```

## 개발 가이드

### 새로운 화면 추가

1. `src/screens/` 폴더에 새 화면 컴포넌트 생성
2. `App.tsx`의 네비게이션에 추가
3. 탭 아이콘 설정 (필요시)

### API 통신

`src/services/apiClient.ts`를 사용하여 백엔드와 통신:

```typescript
import { apiClient } from '../services/apiClient';

// GET 요청
const response = await apiClient.get('/api/endpoint');

// POST 요청
const response = await apiClient.post('/api/endpoint', data);
```

### 상태 관리

React Context를 사용하여 전역 상태 관리:

```typescript
import { useAuth } from '../contexts/AuthContext';
import { useNetwork } from '../contexts/NetworkContext';

const { user, login, logout } = useAuth();
const { isOnline } = useNetwork();
```

## 문제 해결

### 일반적인 오류

1. **모듈을 찾을 수 없음**: `npm install` 실행
2. **Metro 번들러 오류**: `expo start --clear` 실행
3. **타입 오류**: `tsconfig.json` 확인

### 디버깅

- React Native Debugger 사용
- Expo DevTools 활용
- 콘솔 로그 확인

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 