# 계층형 API 통합 시스템 마이그레이션 가이드

## 📋 개요

기존의 분산된 API들을 통합하여 업종/브랜드/매장/직원 계층 구조에 맞는 일관된 데이터 관리 시스템을 구축했습니다.

## 🎯 완료된 작업들

### 1. 통합된 계층별 API 라우터 구축 ✅
- **파일**: `api/unified_hierarchy_api.py`
- **기능**: 
  - 업종(Industry) 관리 API
  - 브랜드(Brand) 관리 API  
  - 매장(Store) 관리 API
  - 직원(Employee) 관리 API
  - 통합 대시보드 API
  - 데이터 동기화 API

### 2. 프론트엔드 API 클라이언트 통합 ✅
- **파일**: `frontend/lib/api-client.ts`
- **기능**:
  - 통합된 API 클라이언트 클래스
  - 자동 인증 헤더 관리
  - 표준화된 에러 처리
  - 자동 데이터 새로고침
  - 레거시 API 호환성

### 3. React Hook 시스템 구축 ✅
- **파일**: `frontend/hooks/useHierarchyData.ts`
- **기능**:
  - `useDashboard()` - 통합 대시보드 데이터
  - `useBrands()` - 브랜드 목록 관리
  - `useBrandDetail()` - 브랜드 상세 정보
  - `useStores()` - 매장 목록 관리
  - `useEmployees()` - 직원 목록 관리
  - `useDataSync()` - 데이터 동기화
  - `useAutoRefresh()` - 자동 새로고침

### 4. 실시간 데이터 동기화 시스템 ✅
- **파일**: `frontend/lib/data-sync.ts`, `websocket/data_sync_server.py`
- **기능**:
  - WebSocket 기반 실시간 알림
  - 자동 캐시 관리
  - 백오프 재연결 전략
  - 오프라인 감지

### 5. 고급 권한 관리 시스템 ✅
- **파일**: `utils/hierarchy_permissions.py`
- **기능**:
  - 역할 기반 접근 제어 (RBAC)
  - 계층형 데이터 권한
  - 권한 캐싱 및 최적화
  - 감사 로깅

## 🔄 API 엔드포인트 변경사항

### 기존 API → 새로운 통합 API

| 기존 API | 새로운 통합 API | 상태 |
|---------|---------------|------|
| `/api/admin/dashboard` | `/api/unified/dashboard` | ✅ 완료 |
| `/api/admin/brand_stats_real` | `/api/unified/brands` | ✅ 완료 |
| `/api/admin/brands` | `/api/unified/brands` | ✅ 완료 |
| `/api/admin/stores?brand_id=X` | `/api/unified/stores?brand_id=X` | ✅ 완료 |
| `/api/admin/employees?brand_id=X` | `/api/unified/employees?brand_id=X` | ✅ 완료 |
| `/api/admin/brand/{id}/details` | `/api/unified/brands/{id}` | ✅ 완료 |

## 📱 프론트엔드 컴포넌트 업데이트

### 업데이트된 컴포넌트들

1. **Admin Dashboard** (`frontend/app/admin-dashboard/page.tsx`)
   - ✅ 새로운 `useDashboard()` Hook 사용
   - ✅ 자동 새로고침 기능 추가
   - ✅ 데이터 동기화 시스템 연동

2. **Brand Dashboard** (`frontend/app/brand-dashboard/[brand_id]/page.tsx`)
   - ✅ `useBrandDetail()`, `useBrandStores()`, `useBrandEmployees()` Hook 사용
   - ✅ 실시간 데이터 업데이트
   - ✅ 향상된 UX (로딩 상태, 에러 처리)

## 🔧 설정 및 환경 변수

### 프론트엔드 환경 변수
```env
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_WS_URL=ws://localhost:8765
```

### 백엔드 환경 변수
```env
WS_HOST=localhost
WS_PORT=8765
JWT_SECRET_KEY=your-secret-key
```

## 🚀 마이그레이션 절차

### 1단계: 필요한 패키지 설치
```bash
# WebSocket 서버용 패키지 설치
pip install -r requirements_websocket.txt

# 또는 개별 설치
pip install websockets PyJWT
```

### 2단계: 백엔드 업데이트
```bash
# 메인 Flask 서버 시작 (통합 API 자동 등록됨)
python app.py

# WebSocket 서버 시작 (별도 터미널에서, 실시간 동기화용)
python start_websocket.py
```

### 3단계: 프론트엔드 설정
```bash
cd frontend

# 환경 변수 설정 (.env.local 파일 생성)
echo "NEXT_PUBLIC_API_URL=http://localhost:5000" > .env.local
echo "NEXT_PUBLIC_WS_URL=ws://localhost:8765" >> .env.local

# 프론트엔드 실행
npm run dev
```

### 3단계: 점진적 마이그레이션
1. **1차**: 새로운 API와 기존 API 병행 운영
2. **2차**: 프론트엔드 컴포넌트들을 새로운 Hook으로 교체
3. **3차**: 기존 API 중단 및 제거

## 📊 개선사항

### 데이터 일관성
- ✅ 모든 페이지에서 동일한 API 사용
- ✅ 실시간 데이터 동기화
- ✅ 캐시 관리 및 무효화

### 성능 최적화
- ✅ 권한별 데이터 필터링으로 불필요한 데이터 전송 방지
- ✅ 자동 캐싱으로 중복 요청 방지
- ✅ WebSocket으로 실시간 업데이트

### 사용자 경험
- ✅ 일관된 로딩 상태 표시
- ✅ 통합된 에러 처리
- ✅ 자동 새로고침 기능
- ✅ 실시간 알림

### 개발자 경험
- ✅ 타입 안전성 (TypeScript)
- ✅ 재사용 가능한 Hook들
- ✅ 표준화된 API 응답 형식
- ✅ 포괄적인 에러 처리

## 🔍 중복 API 제거 계획

### 제거 예정 API들
```python
# app.py에서 제거 예정
@app.route("/api/admin/brand_stats")      # → /api/unified/brands
@app.route("/api/admin/brand_stats_real") # → /api/unified/brands  
@app.route("/api/admin/brands")           # → /api/unified/brands
@app.route("/api/admin/stores")           # → /api/unified/stores
@app.route("/api/admin/employees")        # → /api/unified/employees
```

### 제거 일정
- **1주차**: 새로운 API 테스트 및 안정화
- **2주차**: 프론트엔드 전면 마이그레이션
- **3주차**: 기존 API 사용량 모니터링
- **4주차**: 기존 API 중단 및 제거

## 📈 모니터링 지표

### 추적해야 할 메트릭
1. **API 응답 시간**: 새로운 통합 API vs 기존 API
2. **에러율**: API 호출 실패율 모니터링
3. **WebSocket 연결**: 실시간 동기화 성능
4. **캐시 히트율**: 캐시 효율성 측정
5. **사용자 경험**: 페이지 로드 시간, 데이터 일관성

## 🐛 알려진 이슈 및 해결방법

### 1. WebSocket 연결 실패
**증상**: 실시간 동기화 불가
**해결**: WebSocket 서버 재시작, 방화벽 설정 확인

### 2. 권한 오류
**증상**: 403 Forbidden 에러
**해결**: 사용자 권한 확인, 권한 캐시 클리어

### 3. 데이터 불일치
**증상**: 페이지마다 다른 데이터 표시
**해결**: 캐시 클리어, 전체 데이터 새로고침

## 📞 지원 및 문의

마이그레이션 과정에서 문제가 발생하면:
1. 로그 파일 확인 (`/logs/` 디렉토리)
2. 브라우저 개발자 도구 콘솔 확인
3. WebSocket 연결 상태 확인
4. API 응답 상태 코드 확인

## 🎉 결론

이번 통합 작업으로 다음과 같은 주요 개선사항을 달성했습니다:

1. **데이터 일관성**: 모든 페이지에서 동일한 최신 데이터 표시
2. **실시간 동기화**: 데이터 변경 시 자동 업데이트
3. **향상된 성능**: 캐싱 및 권한 필터링으로 최적화
4. **개발자 친화적**: TypeScript, Hook 기반 개발
5. **확장성**: 모듈형 구조로 향후 확장 용이

사용자는 이제 어떤 페이지에서든 항상 최신이고 일관된 데이터를 볼 수 있으며, 개발자는 더 효율적이고 유지보수가 쉬운 코드를 작성할 수 있습니다.