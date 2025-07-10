# Your Program Frontend

Your Program 관리 시스템의 프론트엔드 애플리케이션입니다.

## 🚀 주요 기능

- **실시간 동기화**: WebSocket 기반 실시간 데이터 동기화
- **권한별 대시보드**: 사용자 역할에 따른 자동 메뉴 분기
- **오프라인 지원**: 네트워크 연결이 없어도 기본 기능 사용 가능
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 지원
- **PWA 지원**: Progressive Web App 기능
- **실시간 알림**: 브라우저 및 시스템 알림

## 🛠 기술 스택

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Testing**: Jest, React Testing Library, Playwright
- **Real-time**: WebSocket
- **PWA**: next-pwa

## 📋 요구사항

- Node.js 18.0.0 이상
- npm 9.0.0 이상
- Git

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone <repository-url>
cd your_program_frontend
```

### 2. 의존성 설치

```bash
npm install
```

### 3. 환경 변수 설정

```bash
cp .env.example .env.local
```

`.env.local` 파일을 편집하여 필요한 환경 변수를 설정하세요:

```env
NEXT_PUBLIC_API_URL=http://localhost:5001
NEXT_PUBLIC_WS_URL=ws://localhost:5001
NODE_ENV=development
```

### 4. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000)을 열어 애플리케이션을 확인하세요.

## 🧪 테스트

### 단위 테스트

```bash
# 모든 테스트 실행
npm test

# 테스트 감시 모드
npm run test:watch

# 커버리지 리포트와 함께 테스트
npm run test:coverage

# CI 환경용 테스트
npm run test:ci
```

### E2E 테스트

```bash
# E2E 테스트 실행
npm run test:e2e

# E2E 테스트 UI 모드
npm run test:e2e:ui
```

### 테스트 커버리지

테스트 커버리지는 다음 기준을 충족해야 합니다:
- **Branches**: 70% 이상
- **Functions**: 70% 이상
- **Lines**: 70% 이상
- **Statements**: 70% 이상

## 🏗 빌드

### 개발 빌드

```bash
npm run build
```

### 프로덕션 빌드

```bash
NODE_ENV=production npm run build
```

## 🚀 배포

### 자동 배포 스크립트 사용

```bash
# 개발 환경 배포
./scripts/deploy.sh dev

# 스테이징 환경 배포
./scripts/deploy.sh staging

# 프로덕션 환경 배포
./scripts/deploy.sh prod
```

### 수동 배포

1. **빌드**
   ```bash
   npm run build
   ```

2. **테스트**
   ```bash
   npm run test:ci
   ```

3. **배포**
   ```bash
   npm start
   ```

## 🧹 정리

### 자동 정리 스크립트 사용

```bash
# 모든 캐시 및 빌드 파일 정리
./scripts/cleanup.sh all

# 캐시만 정리
./scripts/cleanup.sh cache

# 빌드 파일만 정리
./scripts/cleanup.sh build

# 테스트 파일만 정리
./scripts/cleanup.sh test

# node_modules 정리
./scripts/cleanup.sh node_modules
```

### 수동 정리

```bash
# 캐시 정리
rm -rf .next .cache coverage

# node_modules 재설치
rm -rf node_modules package-lock.json
npm install
```

## 📁 프로젝트 구조

```
your_program_frontend/
├── src/
│   ├── app/                    # Next.js App Router 페이지
│   │   ├── dashboard/          # 대시보드 페이지
│   │   ├── orders/            # 주문 관리 페이지
│   │   ├── inventory/         # 재고 관리 페이지
│   │   └── layout.tsx         # 루트 레이아웃
│   ├── components/            # 재사용 가능한 컴포넌트
│   │   ├── ui/               # 기본 UI 컴포넌트
│   │   ├── Sidebar.tsx       # 사이드바 컴포넌트
│   │   └── RealTimeSync.tsx  # 실시간 동기화 컴포넌트
│   ├── store/                # Zustand 상태 관리
│   │   ├── useUserStore.ts   # 사용자 상태 관리
│   │   └── useOrderStore.ts  # 주문 상태 관리
│   ├── hooks/                # 커스텀 훅
│   ├── lib/                  # 유틸리티 라이브러리
│   └── utils/                # 유틸리티 함수
├── public/                   # 정적 파일
├── scripts/                  # 배포 및 유틸리티 스크립트
├── tests/                    # 테스트 파일
└── docs/                     # 문서
```

## 🔧 개발 가이드

### 컴포넌트 작성

```tsx
// components/Example.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'

interface ExampleProps {
  title: string
  onAction?: () => void
}

export default function Example({ title, onAction }: ExampleProps) {
  const [count, setCount] = useState(0)

  return (
    <div className="p-4 border rounded-lg">
      <h2 className="text-xl font-bold">{title}</h2>
      <p>Count: {count}</p>
      <Button onClick={() => setCount(count + 1)}>
        Increment
      </Button>
    </div>
  )
}
```

### Store 작성

```tsx
// store/useExampleStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ExampleState {
  data: any[]
  isLoading: boolean
  fetchData: () => Promise<void>
}

export const useExampleStore = create<ExampleState>()(
  persist(
    (set, get) => ({
      data: [],
      isLoading: false,
      fetchData: async () => {
        set({ isLoading: true })
        try {
          const response = await fetch('/api/data')
          const data = await response.json()
          set({ data, isLoading: false })
        } catch (error) {
          set({ isLoading: false })
        }
      },
    }),
    {
      name: 'example-store',
    }
  )
)
```

### 테스트 작성

```tsx
// __tests__/components/Example.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import Example from '@/components/Example'

describe('Example Component', () => {
  it('renders correctly', () => {
    render(<Example title="Test Title" />)
    expect(screen.getByText('Test Title')).toBeInTheDocument()
  })

  it('increments count when button is clicked', () => {
    render(<Example title="Test" />)
    const button = screen.getByText('Increment')
    fireEvent.click(button)
    expect(screen.getByText('Count: 1')).toBeInTheDocument()
  })
})
```

## 🔐 권한 시스템

### 사용자 역할

- **super_admin**: 최고 관리자 (모든 기능 접근)
- **brand_manager**: 브랜드 관리자 (브랜드별 관리)
- **store_manager**: 매장 관리자 (매장별 관리)
- **employee**: 직원 (제한된 기능)

### 권한 체크

```tsx
import useUserStore from '@/store/useUserStore'

function MyComponent() {
  const { hasRole } = useUserStore()
  
  if (hasRole('super_admin')) {
    return <AdminPanel />
  }
  
  if (hasRole(['store_manager', 'employee'])) {
    return <UserPanel />
  }
  
  return <AccessDenied />
}
```

## 🔄 실시간 동기화

### WebSocket 연결

```tsx
import { useOrderStore } from '@/store/useOrderStore'

function OrderList() {
  const { orders, connectWebSocket } = useOrderStore()
  
  useEffect(() => {
    connectWebSocket()
  }, [])
  
  return (
    <div>
      {orders.map(order => (
        <OrderItem key={order.id} order={order} />
      ))}
    </div>
  )
}
```

### 오프라인 지원

```tsx
import { offlineStorage } from '@/utils/offlineStorage'

// 오프라인 데이터 저장
await offlineStorage.saveOfflineData('orders', 'create', orderData)

// 온라인 복구 시 동기화
await offlineStorage.syncOfflineData()
```

## 🐛 문제 해결

### 일반적인 문제

1. **빌드 실패**
   ```bash
   npm run cleanup:all
   npm install
   npm run build
   ```

2. **테스트 실패**
   ```bash
   npm run test:coverage
   # 커버리지 리포트 확인 후 테스트 수정
   ```

3. **실시간 동기화 문제**
   ```bash
   # WebSocket 연결 상태 확인
   # 브라우저 개발자 도구에서 네트워크 탭 확인
   ```

### 로그 확인

```bash
# 개발 서버 로그
npm run dev

# 빌드 로그
npm run build

# 테스트 로그
npm run test:coverage
```

## 📚 추가 문서

- [API 문서](./docs/API.md)
- [컴포넌트 가이드](./docs/COMPONENTS.md)
- [테스트 가이드](./docs/TESTING.md)
- [배포 가이드](./docs/DEPLOYMENT.md)

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 지원

문제가 있거나 질문이 있으시면 다음 방법으로 연락하세요:

- [Issues](../../issues) - 버그 리포트 및 기능 요청
- [Discussions](../../discussions) - 일반적인 질문 및 토론
- Email: support@yourprogram.com

---

**Your Program Frontend** - 효율적인 관리 시스템을 위한 현대적인 웹 애플리케이션
