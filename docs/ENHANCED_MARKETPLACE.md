# 고도화된 플러그인 마켓플레이스 시스템

## 개요

고도화된 플러그인 마켓플레이스는 플러그인 검색, 상세 정보 조회, 설치/삭제, 리뷰/평점, 통계/추천 기능을 제공하는 종합적인 플러그인 관리 시스템입니다.

## 주요 기능

### 1. 플러그인 검색 및 필터링
- **검색**: 이름, 설명, 태그 기반 검색
- **카테고리 필터**: 비즈니스, 분석, 보안 등 카테고리별 필터링
- **정렬**: 이름, 평점, 다운로드 수, 생성일, 가격순 정렬
- **페이지네이션**: 대량의 플러그인을 효율적으로 로드

### 2. 플러그인 상세 정보
- **기본 정보**: 이름, 버전, 개발자, 설명
- **통계**: 다운로드 수, 평점, 리뷰 수
- **기술 정보**: 크기, 의존성, 호환성, 라이선스
- **링크**: 홈페이지, 저장소 링크

### 3. 리뷰 및 평점 시스템
- **리뷰 작성**: 1-5점 평점과 텍스트 리뷰
- **리뷰 조회**: 플러그인별 리뷰 목록
- **평점 계산**: 자동 평균 평점 계산
- **도움됨 표시**: 리뷰의 유용성 평가

### 4. 다운로드 및 설치
- **다운로드 추적**: 사용자별 다운로드 이력
- **통계 업데이트**: 실시간 다운로드 통계
- **버전 관리**: 특정 버전 다운로드 지원

### 5. 추천 시스템
- **인기 플러그인**: 다운로드 수 기반 인기 순위
- **추천 플러그인**: 평점 기반 추천 (향후 협업 필터링 확장 예정)
- **카테고리별 추천**: 카테고리별 인기 플러그인

### 6. 통계 및 분석
- **전체 통계**: 총 플러그인 수, 다운로드 수, 평균 평점
- **카테고리별 통계**: 카테고리별 플러그인 분포
- **무료/유료 통계**: 무료/유료 플러그인 비율

## API 엔드포인트

### 플러그인 목록 조회
```
GET /api/enhanced-marketplace/plugins
```

**쿼리 파라미터:**
- `search`: 검색어
- `category`: 카테고리 필터
- `sort_by`: 정렬 기준 (name, rating, download_count, created_at, price)
- `sort_order`: 정렬 순서 (asc, desc)
- `limit`: 페이지 크기 (기본값: 50)
- `offset`: 페이지 오프셋 (기본값: 0)

**응답 예시:**
```json
{
  "success": true,
  "data": [
    {
      "id": "restaurant_management",
      "name": "레스토랑 관리 시스템",
      "description": "레스토랑의 주문, 재고, 직원 관리를 위한 종합 플러그인",
      "version": "2.1.0",
      "author": "PluginDev Team",
      "category": "business",
      "tags": ["restaurant", "order", "inventory", "staff"],
      "price": 0.0,
      "download_count": 1250,
      "rating": 4.5,
      "review_count": 89,
      "size": 2048576,
      "dependencies": ["core_management"],
      "compatibility": ["v2.0+", "v3.0+"],
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-20T14:45:00",
      "status": "active",
      "license": "MIT",
      "homepage": "https://example.com/restaurant-plugin",
      "repository": "https://github.com/example/restaurant-plugin"
    }
  ]
}
```

### 플러그인 상세 정보 조회
```
GET /api/enhanced-marketplace/plugins/{plugin_id}
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "id": "restaurant_management",
    "name": "레스토랑 관리 시스템",
    "description": "레스토랑의 주문, 재고, 직원 관리를 위한 종합 플러그인",
    "version": "2.1.0",
    "author": "PluginDev Team",
    "category": "business",
    "tags": ["restaurant", "order", "inventory", "staff"],
    "price": 0.0,
    "download_count": 1250,
    "rating": 4.5,
    "review_count": 89,
    "size": 2048576,
    "dependencies": ["core_management"],
    "compatibility": ["v2.0+", "v3.0+"],
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-20T14:45:00",
    "status": "active",
    "license": "MIT",
    "homepage": "https://example.com/restaurant-plugin",
    "repository": "https://github.com/example/restaurant-plugin",
    "download_stats": {
      "total_downloads": 1250,
      "daily_downloads": 15,
      "weekly_downloads": 89,
      "monthly_downloads": 342,
      "last_download": "2024-01-20T16:30:00"
    }
  }
}
```

### 플러그인 다운로드
```
POST /api/enhanced-marketplace/plugins/{plugin_id}/download
```

**요청 본문:**
```json
{
  "version": "latest"
}
```

**응답 예시:**
```json
{
  "success": true,
  "message": "플러그인이 다운로드되었습니다."
}
```

### 리뷰 목록 조회
```
GET /api/enhanced-marketplace/plugins/{plugin_id}/reviews
```

**쿼리 파라미터:**
- `limit`: 페이지 크기 (기본값: 20)
- `offset`: 페이지 오프셋 (기본값: 0)

**응답 예시:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "plugin_id": "restaurant_management",
      "user_id": "user123",
      "rating": 5,
      "title": "훌륭한 플러그인입니다!",
      "content": "레스토랑 관리에 정말 유용합니다. 직관적인 인터페이스와 다양한 기능이 인상적입니다.",
      "created_at": "2024-01-18T12:30:00",
      "helpful_count": 3,
      "reported": false
    }
  ]
}
```

### 리뷰 작성
```
POST /api/enhanced-marketplace/plugins/{plugin_id}/reviews
```

**요청 본문:**
```json
{
  "rating": 5,
  "title": "훌륭한 플러그인입니다!",
  "content": "레스토랑 관리에 정말 유용합니다. 직관적인 인터페이스와 다양한 기능이 인상적입니다."
}
```

**응답 예시:**
```json
{
  "success": true,
  "message": "리뷰가 추가되었습니다."
}
```

### 카테고리 목록 조회
```
GET /api/enhanced-marketplace/categories
```

**응답 예시:**
```json
{
  "success": true,
  "data": ["business", "analytics", "security", "integration", "ai"]
}
```

### 인기 플러그인 조회
```
GET /api/enhanced-marketplace/popular
```

**쿼리 파라미터:**
- `limit`: 조회할 플러그인 수 (기본값: 10)

**응답 예시:**
```json
{
  "success": true,
  "data": [
    {
      "id": "security_monitor",
      "name": "보안 모니터링 시스템",
      "description": "시스템 보안 상태를 실시간으로 모니터링하고 알림",
      "version": "1.5.1",
      "author": "Security Labs",
      "category": "security",
      "tags": ["security", "monitoring", "alerts", "compliance"],
      "price": 0.0,
      "download_count": 2100,
      "rating": 4.3,
      "review_count": 234,
      "size": 1536000,
      "status": "active",
      "license": "GPL"
    }
  ]
}
```

### 추천 플러그인 조회
```
GET /api/enhanced-marketplace/recommended
```

**쿼리 파라미터:**
- `limit`: 조회할 플러그인 수 (기본값: 10)

**응답 예시:**
```json
{
  "success": true,
  "data": [
    {
      "id": "analytics_dashboard",
      "name": "고급 분석 대시보드",
      "description": "실시간 데이터 분석 및 시각화를 위한 고급 대시보드",
      "version": "1.8.2",
      "author": "Analytics Pro",
      "category": "analytics",
      "tags": ["dashboard", "analytics", "visualization", "reports"],
      "price": 29.99,
      "download_count": 890,
      "rating": 4.8,
      "review_count": 156,
      "size": 5120000,
      "status": "active",
      "license": "Commercial"
    }
  ]
}
```

### 마켓플레이스 통계 조회
```
GET /api/enhanced-marketplace/stats
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "total_plugins": 5,
    "total_downloads": 5152,
    "average_rating": 4.56,
    "free_plugins": 3,
    "paid_plugins": 2,
    "categories": {
      "business": 1,
      "analytics": 1,
      "security": 1,
      "integration": 1,
      "ai": 1
    }
  }
}
```

## 프론트엔드 사용법

### 컴포넌트 사용
```tsx
import EnhancedMarketplace from '@/components/EnhancedMarketplace';

function MarketplacePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <EnhancedMarketplace />
    </div>
  );
}
```

### 주요 기능
1. **검색 및 필터링**: 상단 검색바와 필터 옵션
2. **플러그인 카드**: 각 플러그인의 기본 정보 표시
3. **상세 정보**: 플러그인 카드 클릭 시 상세 정보 다이얼로그
4. **리뷰 시스템**: 상세 정보에서 리뷰 작성 및 조회
5. **다운로드**: 플러그인 다운로드 기능
6. **통계 대시보드**: 상단 통계 카드로 전체 현황 파악

## 데이터베이스 스키마

### plugins 테이블
```sql
CREATE TABLE plugins (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    version TEXT NOT NULL,
    author TEXT NOT NULL,
    category TEXT NOT NULL,
    tags TEXT,
    price REAL DEFAULT 0.0,
    download_count INTEGER DEFAULT 0,
    rating REAL DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,
    size INTEGER DEFAULT 0,
    dependencies TEXT,
    compatibility TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active',
    license TEXT DEFAULT 'MIT',
    homepage TEXT,
    repository TEXT
);
```

### reviews 테이블
```sql
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    rating INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    helpful_count INTEGER DEFAULT 0,
    reported BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (plugin_id) REFERENCES plugins (id)
);
```

### download_stats 테이블
```sql
CREATE TABLE download_stats (
    plugin_id TEXT PRIMARY KEY,
    total_downloads INTEGER DEFAULT 0,
    daily_downloads INTEGER DEFAULT 0,
    weekly_downloads INTEGER DEFAULT 0,
    monthly_downloads INTEGER DEFAULT 0,
    last_download DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plugin_id) REFERENCES plugins (id)
);
```

### download_history 테이블
```sql
CREATE TABLE download_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT NOT NULL,
    user_id TEXT,
    downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    version TEXT,
    FOREIGN KEY (plugin_id) REFERENCES plugins (id)
);
```

## 테스트

### 테스트 실행
```bash
# 전체 테스트 실행
python tests/test_enhanced_marketplace.py

# 특정 URL로 테스트
python tests/test_enhanced_marketplace.py --url http://localhost:5000

# 결과를 JSON 파일로 저장
python tests/test_enhanced_marketplace.py --output test_results.json
```

### 테스트 항목
1. **마켓플레이스 통계**: 전체 통계 조회 테스트
2. **카테고리 목록**: 카테고리 목록 조회 테스트
3. **플러그인 목록**: 플러그인 목록 조회 및 검색/정렬 테스트
4. **플러그인 상세**: 플러그인 상세 정보 조회 테스트
5. **플러그인 리뷰**: 리뷰 목록 조회 테스트
6. **인기 플러그인**: 인기 플러그인 조회 테스트
7. **추천 플러그인**: 추천 플러그인 조회 테스트
8. **플러그인 다운로드**: 다운로드 기능 테스트

## 샘플 플러그인

시스템에는 다음과 같은 샘플 플러그인들이 포함되어 있습니다:

1. **레스토랑 관리 시스템** (business)
   - 무료 플러그인
   - 주문, 재고, 직원 관리 기능
   - 1,250+ 다운로드, 4.5점 평점

2. **고급 분석 대시보드** (analytics)
   - 유료 플러그인 ($29.99)
   - 실시간 데이터 분석 및 시각화
   - 890+ 다운로드, 4.8점 평점

3. **보안 모니터링 시스템** (security)
   - 무료 플러그인
   - 실시간 보안 모니터링 및 알림
   - 2,100+ 다운로드, 4.3점 평점

4. **모바일 앱 동기화** (integration)
   - 유료 플러그인 ($49.99)
   - 모바일 앱과 웹 시스템 동기화
   - 567+ 다운로드, 4.6점 평점

5. **AI 챗봇 시스템** (ai)
   - 유료 플러그인 ($99.99)
   - 인공지능 기반 고객 지원 챗봇
   - 345+ 다운로드, 4.7점 평점

## 향후 개선 계획

1. **고급 검색**: Elasticsearch 기반 풀텍스트 검색
2. **협업 필터링**: 사용자 기반 추천 시스템
3. **플러그인 버전 관리**: 자동 업데이트 알림
4. **결제 시스템**: 유료 플러그인 구매 기능
5. **플러그인 개발자 포털**: 개발자 전용 관리 인터페이스
6. **플러그인 검증**: 자동 테스트 및 보안 검사
7. **다국어 지원**: 국제화 및 현지화
8. **모바일 앱**: React Native 기반 모바일 앱

## 문제 해결

### 일반적인 문제

1. **API 응답이 느린 경우**
   - 데이터베이스 인덱스 확인
   - 캐싱 설정 검토
   - 쿼리 최적화

2. **리뷰가 표시되지 않는 경우**
   - 데이터베이스 연결 확인
   - 플러그인 ID 유효성 검사
   - 권한 설정 확인

3. **다운로드가 실패하는 경우**
   - 사용자 인증 상태 확인
   - 플러그인 파일 존재 여부 확인
   - 디스크 공간 확인

### 로그 확인
```bash
# 애플리케이션 로그 확인
tail -f logs/app.log

# 마켓플레이스 관련 로그 필터링
grep "enhanced_marketplace" logs/app.log
```

### 데이터베이스 확인
```bash
# SQLite 데이터베이스 접속
sqlite3 marketplace.db

# 테이블 구조 확인
.schema plugins
.schema reviews
.schema download_stats

# 샘플 데이터 확인
SELECT * FROM plugins LIMIT 5;
SELECT * FROM reviews LIMIT 5;
```

## 라이선스

이 시스템은 MIT 라이선스 하에 배포됩니다. 자세한 내용은 LICENSE 파일을 참조하세요. 