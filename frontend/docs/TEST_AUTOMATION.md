# 🧪 테스트 자동화 시스템

## 개요

이 프로젝트는 포괄적인 테스트 자동화 시스템을 제공합니다. 단위 테스트, E2E 테스트, 성능 테스트, 보안 검사를 자동화하여 코드 품질을 보장합니다.

## 🚀 빠른 시작

### 기본 테스트 실행

```bash
# 단위 테스트만 실행
npm run test:unit

# 테스트 자동화 전체 실행
npm run test:automation

# E2E 테스트 포함 실행
npm run test:automation:e2e
```

### 개별 테스트 실행

```bash
# 단위 테스트 (감시 모드)
npm run test:unit:watch

# 커버리지 포함 단위 테스트
npm run test:unit:coverage

# E2E 테스트
npm run test:e2e

# E2E 테스트 (UI 모드)
npm run test:e2e:ui

# 성능 테스트만
npm run test:performance

# 보안 검사만
npm run test:security
```

## 📋 테스트 자동화 구성 요소

### 1. 단위 테스트 (Jest)

- **프레임워크**: Jest + React Testing Library
- **설정 파일**: `jest.config.js`
- **테스트 파일 위치**: `src/test/`, `src/__tests__/`
- **커버리지**: 자동 생성 (80% 이상 목표)

#### 테스트 작성 예시

```typescript
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { PerformanceTestUtils } from '@/test/utils/performance.test'

describe('Component', () => {
  it('렌더링 테스트', () => {
    render(<Component />)
    expect(screen.getByText('텍스트')).toBeInTheDocument()
  })

  it('성능 테스트', async () => {
    const result = await PerformanceTestUtils.measureRenderPerformance(
      <Component />,
      5
    )
    expect(result.avg).toHaveGoodPerformance(50)
  })
})
```

### 2. E2E 테스트 (Playwright)

- **프레임워크**: Playwright
- **설정 파일**: `playwright.config.ts`
- **테스트 파일 위치**: `tests/e2e/`
- **브라우저**: Chromium, Firefox, WebKit

#### E2E 테스트 작성 예시

```typescript
import { test, expect } from '@playwright/test'

test('사용자 로그인 플로우', async ({ page }) => {
  await page.goto('/login')
  await page.fill('[data-testid="username"]', 'admin')
  await page.fill('[data-testid="password"]', 'password')
  await page.click('[data-testid="login-button"]')
  
  await expect(page).toHaveURL('/dashboard')
  await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
})
```

### 3. 성능 테스트

- **빌드 시간 측정**
- **번들 크기 분석**
- **Core Web Vitals 모니터링**
- **메모리 사용량 체크**

### 4. 보안 검사

- **npm audit 실행**
- **의존성 취약점 검사**
- **보안 헤더 검증**

## 🔧 설정 파일

### Jest 설정 (`jest.config.js`)

```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.test.{js,jsx,ts,tsx}',
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
}

module.exports = createJestConfig(customJestConfig)
```

### MSW 설정 (API 모킹)

```typescript
// src/test/mocks/handlers.ts
import { rest } from 'msw'

export const handlers = [
  rest.get('/api/staff/list', (req, res, ctx) => {
    return res(
      ctx.json({
        success: true,
        data: mockStaffData,
      })
    )
  }),
]
```

## 📊 성능 테스트 유틸리티

### PerformanceTestUtils

```typescript
import { PerformanceTestUtils } from '@/test/utils/performance.test'

// 렌더링 성능 측정
const renderResult = await PerformanceTestUtils.measureRenderPerformance(
  <Component />,
  10
)

// 메모리 사용량 측정
const memoryUsage = PerformanceTestUtils.measureMemoryUsage()

// 네트워크 성능 측정
const networkResult = await PerformanceTestUtils.measureNetworkPerformance(
  () => apiCall(),
  5
)
```

## 🤖 CI/CD 통합

### GitHub Actions

`.github/workflows/test-automation.yml` 파일이 다음을 자동화합니다:

1. **코드 체크아웃**
2. **의존성 설치**
3. **린팅 및 타입 체크**
4. **단위 테스트 실행**
5. **커버리지 업로드**
6. **보안 감사**
7. **빌드 및 번들 분석**
8. **E2E 테스트 실행**
9. **성능 테스트 실행**

### 실행 트리거

- **Push**: main, develop 브랜치
- **Pull Request**: main, develop 브랜치
- **스케줄**: 매일 오전 6시

## 📈 테스트 리포트

### 자동 생성 리포트

테스트 자동화 실행 시 다음 리포트가 생성됩니다:

- **위치**: `test-reports/test-report-{timestamp}.json`
- **포함 내용**:
  - 테스트 결과 요약
  - 성능 메트릭
  - 커버리지 정보
  - 보안 검사 결과
  - 실행 시간 통계

### 리포트 예시

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "summary": {
    "totalTests": 5,
    "passedTests": 5,
    "failedTests": 0,
    "coverage": {
      "statements": 85.5,
      "branches": 78.2,
      "functions": 82.1,
      "lines": 84.3
    },
    "performance": {
      "buildTime": 45230
    }
  },
  "details": {
    "unitTests": { "success": true, "duration": 1250 },
    "coverage": { "success": true, "duration": 890 },
    "performance": { "success": true, "duration": 45670 },
    "security": { "success": true, "duration": 340 }
  }
}
```

## 🎯 모범 사례

### 1. 테스트 작성 가이드라인

- **설명적인 테스트 이름 사용**
- **AAA 패턴 준수** (Arrange, Act, Assert)
- **한 테스트에 한 가지 검증만**
- **테스트 격리 보장**

### 2. 성능 테스트 가이드라인

- **실제 사용 시나리오 기반**
- **임계값 설정 및 모니터링**
- **메모리 누수 검사**
- **네트워크 요청 최적화**

### 3. 보안 테스트 가이드라인

- **정기적인 의존성 업데이트**
- **보안 헤더 검증**
- **인증/인가 테스트**
- **입력 검증 테스트**

## 🛠️ 문제 해결

### 일반적인 문제

1. **테스트 타임아웃**
   ```bash
   # Jest 타임아웃 증가
   jest --testTimeout=10000
   ```

2. **메모리 부족**
   ```bash
   # Node.js 메모리 증가
   node --max-old-space-size=4096 scripts/test-automation.js
   ```

3. **MSW 설정 문제**
   ```bash
   # MSW 서버 재시작
   npm run test:unit -- --clearCache
   ```

### 디버깅 팁

- **개별 테스트 실행**: `npm run test:unit -- --testNamePattern="테스트명"`
- **상세 로그**: `npm run test:unit -- --verbose`
- **커버리지 상세보기**: `npm run test:unit:coverage -- --coverageReporters=text`

## 📚 추가 리소스

- [Jest 공식 문서](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Playwright 공식 문서](https://playwright.dev/docs/intro)
- [MSW 공식 문서](https://mswjs.io/docs/)

## 🤝 기여 가이드

새로운 테스트를 추가할 때:

1. **적절한 테스트 파일 위치 선택**
2. **설명적인 테스트 이름 작성**
3. **커버리지 목표 달성 확인**
4. **성능 테스트 포함 고려**
5. **문서 업데이트**

---

**마지막 업데이트**: 2024년 1월 15일 