# 퀀텀 모바일 앱

퀀텀 비즈니스 관리 시스템의 모바일 애플리케이션입니다.

## 기능

### 📊 대시보드
- 실시간 통계 및 현황 확인
- 빠른 액션 버튼
- 최근 활동 내역

### 🏪 매장 관리
- 매장 목록 조회 및 관리
- 매장 상태 모니터링
- 매장별 통계 확인

### 📦 재고 관리
- 재고 현황 실시간 확인
- 재고 부족 알림
- 입출고 관리
- 카테고리별 필터링

### 🛒 주문 관리
- 실시간 주문 현황
- 주문 상태 추적
- 주문 처리 및 완료

### 📅 스케줄 관리
- 직원 스케줄 확인
- 근무 상태 모니터링
- 스케줄 생성 및 수정

### 🔔 알림 시스템
- 실시간 알림 수신
- 알림 타입별 분류
- 읽음/읽지 않음 상태 관리

### 👤 프로필 관리
- 사용자 정보 관리
- 앱 설정
- 보안 설정
- 지원 및 도움말

## 기술 스택

- **React Native** - 크로스 플랫폼 모바일 개발
- **Expo** - 개발 환경 및 빌드 도구
- **React Navigation** - 네비게이션 관리
- **TypeScript** - 타입 안전성
- **Ionicons** - 아이콘 라이브러리

## 설치 및 실행

### 필수 요구사항
- Node.js 18.0.0 이상
- npm 또는 yarn
- Expo CLI
- iOS Simulator (iOS 개발용)
- Android Studio (Android 개발용)

### 설치
```bash
# 의존성 설치
npm install

# Expo CLI 설치 (전역)
npm install -g @expo/cli
```

### 실행
```bash
# 개발 서버 시작
npm start

# iOS 시뮬레이터에서 실행
npm run ios

# Android 에뮬레이터에서 실행
npm run android

# 웹 브라우저에서 실행
npm run web
```

## 프로젝트 구조

```
mobile_app/
├── App.tsx                 # 메인 앱 컴포넌트
├── src/
│   └── screens/           # 화면 컴포넌트들
│       ├── DashboardScreen.tsx
│       ├── StoreManagementScreen.tsx
│       ├── InventoryScreen.tsx
│       ├── OrdersScreen.tsx
│       ├── ScheduleScreen.tsx
│       ├── NotificationsScreen.tsx
│       └── ProfileScreen.tsx
├── package.json
└── README.md
```

## 주요 컴포넌트

### DashboardScreen
- 통계 카드 (총 매장, 활성 주문, 재고 부족, 오늘 매출)
- 빠른 액션 버튼 (새 주문, 재고 확인, 스케줄, 알림)
- 최근 활동 내역

### StoreManagementScreen
- 매장 목록 및 검색
- 매장 상태 토글 (활성/비활성)
- 매장별 통계 (매출, 직원 수)
- 매장 관리 액션 (수정, 직원, 분석)

### InventoryScreen
- 재고 목록 및 검색
- 카테고리별 필터링
- 재고 상태 표시 (정상/부족/품절)
- 재고 바 시각화
- 입출고 관리

### OrdersScreen
- 주문 목록 및 상태 관리
- 주문별 상세 정보
- 주문 처리 액션 (완료, 취소)

### ScheduleScreen
- 직원 스케줄 목록
- 근무 상태 표시 (예정/근무중/완료/결근)
- 스케줄 관리

### NotificationsScreen
- 알림 목록 및 타입별 분류
- 읽음/읽지 않음 상태 관리
- 알림 전체 읽음 처리

### ProfileScreen
- 사용자 프로필 정보
- 앱 설정 (알림, 다크 모드, 언어, 시간대)
- 보안 설정 (비밀번호, 생체 인증, 2단계 인증)
- 지원 및 앱 정보

## API 연동

현재는 모의 데이터를 사용하고 있으며, 실제 백엔드 API와의 연동을 위해 다음 작업이 필요합니다:

1. API 클라이언트 설정
2. 인증 시스템 구현
3. 실시간 데이터 동기화
4. 오프라인 지원

## 빌드 및 배포

### Expo EAS Build
```bash
# EAS CLI 설치
npm install -g @expo/eas-cli

# 로그인
eas login

# 빌드 설정
eas build:configure

# Android 빌드
eas build --platform android

# iOS 빌드
eas build --platform ios
```

### 앱 스토어 배포
```bash
# Android Play Store
eas submit --platform android

# iOS App Store
eas submit --platform ios
```

## 개발 가이드라인

### 코드 스타일
- TypeScript 사용
- 함수형 컴포넌트 및 Hooks 사용
- 일관된 네이밍 컨벤션
- 적절한 주석 작성

### 상태 관리
- React Hooks (useState, useEffect) 사용
- 필요시 Context API 또는 Redux 도입 고려

### 성능 최적화
- FlatList 사용으로 대용량 데이터 처리
- 이미지 최적화
- 불필요한 리렌더링 방지

### 테스트
- Jest 및 React Native Testing Library 사용
- 컴포넌트 단위 테스트
- 통합 테스트

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해 주세요. 