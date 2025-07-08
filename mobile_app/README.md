# Restaurant Manager Mobile App

레스토랑 관리 시스템의 React Native 모바일 앱입니다.

## 🚀 주요 기능

### 📱 핵심 기능
- **대시보드**: 실시간 통계 및 현황 모니터링
- **직원 관리**: 출근 체크, 근무 일정, 직원 정보 관리
- **주문 관리**: 주문 접수, 상태 추적, 완료 처리
- **재고 관리**: 재고 현황, 발주 관리, 알림
- **근무 일정**: 스케줄 관리, 교대 근무, 휴가 신청

### 🤖 고급 기능
- **AI 챗봇**: 자연어 기반 주문 및 문의 처리
- **음성 인식**: 음성 명령으로 빠른 작업 수행
- **이미지 분석**: QR 코드 스캔, 영수증 처리
- **실시간 번역**: 다국어 지원 및 자동 번역

### 🔔 알림 시스템
- **푸시 알림**: 실시간 알림 및 업데이트
- **오프라인 모드**: 네트워크 없이도 기본 기능 사용
- **동기화**: 온라인 복구 시 데이터 자동 동기화

## 📋 기술 스택

### Frontend
- **React Native**: 0.72.6
- **TypeScript**: 타입 안전성
- **React Navigation**: 네비게이션 관리
- **React Native Paper**: Material Design UI
- **React Native Elements**: 추가 UI 컴포넌트

### 상태 관리
- **Context API**: 전역 상태 관리
- **AsyncStorage**: 로컬 데이터 저장
- **React Query**: 서버 상태 관리 (예정)

### 네트워킹
- **Axios**: HTTP 클라이언트
- **NetInfo**: 네트워크 상태 모니터링
- **WebSocket**: 실시간 통신 (예정)

### 고급 기능
- **React Native Camera**: 카메라 및 QR 스캔
- **React Native Voice**: 음성 인식
- **React Native TTS**: 텍스트 음성 변환
- **React Native Image Picker**: 이미지 선택
- **React Native Push Notification**: 푸시 알림

## 🛠️ 설치 및 실행

### 필수 요구사항
- Node.js 16+
- React Native CLI
- Android Studio (Android 개발용)
- Xcode (iOS 개발용)

### 1. 의존성 설치
```bash
cd mobile_app
npm install
```

### 2. iOS 의존성 설치 (iOS 개발용)
```bash
cd ios
pod install
cd ..
```

### 3. 개발 서버 실행
```bash
# Metro 번들러 시작
npm start

# Android 실행
npm run android

# iOS 실행
npm run ios
```

### 4. 빌드
```bash
# Android 릴리즈 빌드
npm run build:android

# iOS 릴리즈 빌드
npm run build:ios
```

## 📁 프로젝트 구조

```
mobile_app/
├── src/
│   ├── components/          # 재사용 가능한 컴포넌트
│   ├── screens/            # 화면 컴포넌트
│   │   ├── auth/          # 인증 관련 화면
│   │   ├── main/          # 메인 기능 화면
│   │   ├── admin/         # 관리자 전용 화면
│   │   ├── advanced/      # 고급 기능 화면
│   │   └── common/        # 공통 화면
│   ├── navigation/        # 네비게이션 설정
│   ├── contexts/          # React Context
│   ├── services/          # API 서비스
│   ├── hooks/             # 커스텀 훅
│   ├── utils/             # 유틸리티 함수
│   ├── theme/             # 테마 설정
│   └── types/             # TypeScript 타입 정의
├── android/               # Android 네이티브 코드
├── ios/                   # iOS 네이티브 코드
└── assets/                # 이미지, 폰트 등 리소스
```

## 🔧 설정

### 환경 변수
`.env` 파일을 생성하여 다음 설정을 추가하세요:

```env
API_BASE_URL=http://192.168.45.44:5000
ENVIRONMENT=development
```

### API 서버 연결
`src/services/apiClient.ts`에서 API 서버 URL을 설정하세요:

```typescript
const API_BASE_URL = 'http://your-server-ip:5000';
```

## 📱 화면 구성

### 인증 화면
- **로그인**: 이메일/비밀번호 로그인
- **회원가입**: 신규 사용자 등록
- **비밀번호 찾기**: 비밀번호 재설정

### 메인 화면
- **대시보드**: 통계 및 빠른 액션
- **근무 일정**: 개인/팀 스케줄
- **출근 관리**: 출근/퇴근 체크
- **주문 관리**: 주문 현황 및 처리
- **알림**: 시스템 알림 및 메시지

### 관리자 화면
- **직원 관리**: 직원 정보 및 권한 관리
- **재고 관리**: 재고 현황 및 발주
- **보고서**: 매출, 출근, 재고 보고서
- **분석**: 데이터 분석 및 인사이트
- **설정**: 시스템 설정 및 관리

### 고급 기능 화면
- **AI 챗봇**: 자연어 대화 인터페이스
- **음성 인식**: 음성 명령 처리
- **이미지 분석**: QR 스캔 및 OCR
- **번역**: 다국어 번역 서비스

## 🔐 보안

### 인증
- JWT 토큰 기반 인증
- 토큰 자동 갱신
- 생체 인증 지원 (지문/얼굴 인식)

### 데이터 보호
- 민감 데이터 암호화
- 로컬 저장소 보안
- 네트워크 통신 암호화

### 권한 관리
- 역할 기반 접근 제어 (RBAC)
- 기능별 권한 설정
- 세션 관리

## 📊 성능 최적화

### 이미지 최적화
- 이미지 압축 및 리사이징
- 지연 로딩 (Lazy Loading)
- 캐싱 전략

### 네트워크 최적화
- 요청 캐싱
- 배치 처리
- 오프라인 지원

### 메모리 관리
- 컴포넌트 메모리 누수 방지
- 이미지 메모리 최적화
- 가비지 컬렉션 최적화

## 🧪 테스트

### 단위 테스트
```bash
npm test
```

### E2E 테스트
```bash
npm run test:e2e
```

### 린트 검사
```bash
npm run lint
```

## 📦 배포

### Android
1. `android/app/build.gradle`에서 버전 설정
2. `npm run build:android` 실행
3. APK 파일 생성

### iOS
1. `ios/RestaurantManager.xcodeproj`에서 버전 설정
2. `npm run build:ios` 실행
3. IPA 파일 생성

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해주세요.

---

**Restaurant Manager Mobile App** - 스마트한 레스토랑 관리의 새로운 경험 