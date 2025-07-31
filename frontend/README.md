# 멀티테넌시 관리 시스템 프론트엔드

## 📋 프로젝트 개요

업종/브랜드/매장/직원의 계층적 구조를 관리하는 멀티테넌시 시스템의 프론트엔드입니다.

## 🏗️ 아키텍처

### 기술 스택
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Shadcn UI
- **State Management**: Zustand
- **HTTP Client**: Axios (API Client)
- **Icons**: Lucide React

### 프로젝트 구조
```
frontend/
├── app/                    # Next.js App Router
│   ├── dashboard/         # 메인 대시보드
│   ├── industry-management/  # 업종 관리
│   ├── brand-management/     # 브랜드 관리
│   ├── store-management/     # 매장 관리
│   └── employee-management/  # 직원 관리
├── src/
│   ├── components/        # 재사용 가능한 컴포넌트
│   ├── hooks/            # 커스텀 훅
│   ├── store/            # Zustand 스토어
│   └── lib/              # 유틸리티 및 설정
└── lib/                  # API 클라이언트
```

## 🚀 주요 기능

### 1. 계층별 관리 시스템
- **업종 관리**: 업종 CRUD, 통계, 검색
- **브랜드 관리**: 브랜드 CRUD, 업종별 필터링, 통계
- **매장 관리**: 매장 CRUD, 브랜드별 필터링, 상태 관리
- **직원 관리**: 직원 CRUD, 매장별 필터링, 근무 관리

### 2. 통합 대시보드
- **실시간 통계**: 업종/브랜드/매장/직원 현황
- **시스템 모니터링**: 백엔드 연결 상태, 오류 현황
- **빠른 액션**: 각 관리 페이지로의 빠른 이동
- **데이터 분석**: 계층별 분포 및 시스템 상태 시각화

### 3. 고급 기능
- **전역 에러 처리**: ErrorBoundary + useErrorHandler
- **데이터 캐싱**: useDataCache로 성능 최적화
- **로딩 상태 관리**: useLoadingState로 일관된 UX
- **접근성 지원**: 고대비, 큰 글씨, 모션 감소 옵션

## 🔧 API 연동

### 백엔드 엔드포인트
| 데이터 유형 | GET (조회) | POST (생성) | PUT (수정) | DELETE (삭제) |
|------------|------------|-------------|------------|---------------|
| 업종 | `/api/admin/industries` | `/api/admin/industries` | `/api/admin/industries/{id}` | `/api/admin/industries/{id}` |
| 브랜드 | `/api/admin/brands` | `/api/admin/brands` | `/api/admin/brands/{id}` | `/api/admin/brands/{id}` |
| 매장 | `/api/admin/branches` | `/api/admin/branches` | `/api/admin/branches/{id}` | `/api/admin/branches/{id}` |
| 직원 | `/api/admin/employees` | `/api/admin/employees` | `/api/admin/employees/{id}` | `/api/admin/employees/{id}` |

### API 클라이언트 특징
- **자동 인증**: 토큰 관리 및 자동 갱신
- **에러 처리**: 표준화된 에러 응답 및 전역 처리
- **데이터 동기화**: 변경 시 자동 캐시 무효화
- **타입 안전성**: TypeScript 인터페이스로 완전한 타입 지원

## 🎨 UI/UX 특징

### 디자인 시스템
- **다크 테마**: 슬레이트 기반의 모던한 다크 테마
- **그라데이션**: 사이버펑크 스타일의 네온 그라데이션
- **반응형**: 모바일부터 데스크톱까지 완전 반응형
- **접근성**: WCAG 가이드라인 준수

### 컴포넌트 라이브러리
- **Shadcn UI**: 일관된 디자인 시스템
- **커스텀 컴포넌트**: 프로젝트 특화 컴포넌트
- **로딩 상태**: 다양한 로딩 스피너 및 스켈레톤
- **에러 처리**: 사용자 친화적인 에러 메시지

## 🔐 권한 관리

### 역할별 접근 제어
- **super_admin**: 모든 기능 접근 가능
- **brand_manager**: 브랜드 및 하위 관리
- **store_manager**: 매장 및 직원 관리
- **employee**: 제한된 기능만 접근

### 동적 메뉴 구성
- 권한에 따른 사이드바 메뉴 자동 구성
- 실시간 권한 변경 감지
- 계층별 데이터 필터링

## 📱 반응형 디자인

### 브레이크포인트
- **모바일**: 320px ~ 768px
- **태블릿**: 768px ~ 1024px
- **데스크톱**: 1024px 이상

### 컴포넌트별 최적화
- **DashboardContainer**: 7xl 최대 너비
- **CardContainer**: 4xl 최대 너비
- **FormContainer**: 2xl 최대 너비
- **ModalContainer**: lg 최대 너비

## 🚀 성능 최적화

### 데이터 캐싱
- **TTL**: 5분 기본 캐시 시간
- **Stale While Revalidate**: 30초 동안 캐시된 데이터 표시
- **자동 새로고침**: 1분마다 백그라운드 업데이트

### 코드 최적화
- **React.memo**: 불필요한 리렌더링 방지
- **useCallback/useMemo**: 메모이제이션으로 성능 향상
- **동적 임포트**: 코드 스플리팅으로 초기 로딩 최적화

## 🛠️ 개발 환경 설정

### 필수 요구사항
- Node.js 18+ 
- npm 또는 yarn

### 설치 및 실행
```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 빌드
npm run build

# 프로덕션 서버 실행
npm start
```

### 환경 변수
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=멀티테넌시 관리 시스템
```

## 📊 상태 관리

### Zustand 스토어
- **useUserStore**: 사용자 인증 및 권한 관리
- **useAuthStore**: 인증 토큰 관리
- **useOrderStore**: 주문 데이터 관리
- **uiStore**: UI 상태 관리

### 커스텀 훅
- **useOptimizedData**: 데이터 캐싱 및 최적화
- **useLoadingState**: 로딩 상태 관리
- **useErrorHandler**: 에러 처리
- **useDataCache**: 클라이언트 사이드 캐싱

## 🔧 개발 가이드

### 컴포넌트 작성 규칙
1. **TypeScript**: 모든 컴포넌트는 TypeScript로 작성
2. **Props 인터페이스**: 명시적인 Props 타입 정의
3. **에러 경계**: ErrorBoundary로 감싸기
4. **접근성**: ARIA 라벨 및 키보드 네비게이션 지원

### API 호출 패턴
```typescript
// 최적화된 데이터 훅 사용
const { data, isLoading, error, refreshData } = useOptimizedData({
  key: 'unique-cache-key',
  fetchFunction: () => apiClient.getData(),
  ttl: 5 * 60 * 1000,
  autoRefresh: true
});
```

### 에러 처리
```typescript
// 전역 에러 핸들러 사용
const { handleError } = useErrorHandler();

try {
  await apiCall();
} catch (error) {
  handleError(error);
}
```

## 🧪 테스트

### 테스트 환경
- **Jest**: 단위 테스트
- **React Testing Library**: 컴포넌트 테스트
- **MSW**: API 모킹

### 테스트 실행
```bash
# 전체 테스트 실행
npm test

# 커버리지 포함
npm run test:coverage

# 감시 모드
npm run test:watch
```

## 📈 배포

### 빌드 최적화
- **Next.js 최적화**: 자동 코드 스플리팅
- **이미지 최적화**: Next.js Image 컴포넌트
- **번들 분석**: webpack-bundle-analyzer

### 배포 환경
- **Vercel**: 권장 배포 플랫폼
- **Docker**: 컨테이너화 지원
- **CI/CD**: GitHub Actions 자동화

## 🤝 기여 가이드

### 코드 스타일
- **ESLint**: 코드 품질 검사
- **Prettier**: 코드 포맷팅
- **Husky**: Git 훅으로 자동 검사

### 커밋 메시지
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 업데이트
style: 코드 스타일 변경
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 빌드 프로세스 변경
```

## 📞 지원

### 이슈 리포트
- GitHub Issues를 통한 버그 리포트
- 기능 요청 및 개선 제안

### 문서
- [API 문서](./docs/api.md)
- [컴포넌트 문서](./docs/components.md)
- [배포 가이드](./docs/deployment.md)

---

**개발팀**: 멀티테넌시 관리 시스템 개발팀  
**최종 업데이트**: 2024년 7월  
**버전**: 1.0.0
