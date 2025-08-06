# API 게이트웨이 시스템

API 게이트웨이는 모든 API 요청의 진입점 역할을 하며, 라우팅, 인증, 속도 제한, 로깅, 모니터링 등의 기능을 제공합니다.

## 주요 기능

### 1. API 라우팅 및 프록시
- 다양한 서비스로의 요청 라우팅
- 동적 라우트 설정 및 관리
- 요청/응답 프록시 처리

### 2. 인증 및 보안
- JWT 토큰 기반 인증
- 라우트별 인증 요구사항 설정
- API 키 관리 (선택사항)

### 3. 속도 제한 (Rate Limiting)
- IP 기반 속도 제한
- 사용자 기반 속도 제한
- API 키 기반 속도 제한
- 라우트별 개별 속도 제한 설정

### 4. 모니터링 및 메트릭
- 실시간 API 메트릭 수집
- 응답 시간 모니터링
- 상태 코드 분포 분석
- 상위 라우트 통계

### 5. 캐싱
- 응답 캐싱 (선택사항)
- 캐시 TTL 설정
- 캐시 정리 기능

### 6. 로깅
- 요청/응답 로깅
- 에러 로깅
- 성능 로깅

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 설정
```bash
# .env 파일 생성
GATEWAY_DATA_DIR=data/gateway
JWT_SECRET=your-secret-key-change-in-production
RATE_LIMIT_WINDOW=3600
RATE_LIMIT_MAX_REQUESTS=1000
ENABLE_RATE_LIMITING=true
ENABLE_LOGGING=true
```

### 3. 데이터 디렉토리 생성
```bash
mkdir -p data/gateway
```

## 사용법

### 1. 게이트웨이 관리자 초기화
```python
from gateway.gateway_manager import GatewayManager, GatewayConfig

config = GatewayConfig(
    data_dir="data/gateway",
    jwt_secret="your-secret-key",
    rate_limit_window=3600,
    rate_limit_max_requests=1000,
    enable_rate_limiting=True,
    enable_logging=True
)

gateway_manager = GatewayManager(config)
```

### 2. API 라우트 생성
```python
route_id = gateway_manager.create_route(
    name="사용자 API",
    path="/api/users",
    method="GET",
    target_url="http://localhost:5001/api/users",
    service_name="user-service",
    requires_auth=True
)
```

### 3. 요청 라우팅
```python
response, status_code = gateway_manager.route_request(request)
```

## API 엔드포인트

### 게이트웨이 관리 API

#### 1. 상태 확인
```
GET /api/gateway/health
```

#### 2. 통계 조회
```
GET /api/gateway/stats
```

#### 3. 라우트 관리
```
GET /api/gateway/routes          # 라우트 목록 조회
POST /api/gateway/routes         # 새 라우트 생성
PUT /api/gateway/routes/{id}     # 라우트 수정
DELETE /api/gateway/routes/{id}  # 라우트 삭제
```

#### 4. 메트릭 조회
```
GET /api/gateway/metrics              # 메트릭 목록 조회
GET /api/gateway/metrics/summary      # 메트릭 요약 조회
```

#### 5. 설정 관리
```
GET /api/gateway/config       # 설정 조회
PUT /api/gateway/config       # 설정 수정
```

#### 6. 시스템 관리
```
POST /api/gateway/cache/clear        # 캐시 정리
POST /api/gateway/rate-limit/clear   # 속도 제한 데이터 정리
```

### 프록시 API
```
GET /api/gateway/proxy/{path}     # GET 요청 프록시
POST /api/gateway/proxy/{path}    # POST 요청 프록시
PUT /api/gateway/proxy/{path}     # PUT 요청 프록시
DELETE /api/gateway/proxy/{path}  # DELETE 요청 프록시
PATCH /api/gateway/proxy/{path}   # PATCH 요청 프록시
```

## 설정 옵션

### GatewayConfig

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| data_dir | str | - | 데이터 저장 디렉토리 |
| jwt_secret | str | "your-secret-key" | JWT 토큰 서명 키 |
| rate_limit_window | int | 3600 | 속도 제한 시간 윈도우 (초) |
| rate_limit_max_requests | int | 1000 | 최대 요청 수 |
| enable_rate_limiting | bool | True | 속도 제한 활성화 |
| enable_logging | bool | True | 로깅 활성화 |

### APIRoute

| 필드 | 타입 | 설명 |
|------|------|------|
| route_id | str | 라우트 고유 ID |
| name | str | 라우트 이름 |
| path | str | API 경로 |
| method | str | HTTP 메서드 |
| target_url | str | 대상 서비스 URL |
| service_name | str | 서비스 이름 |
| is_active | bool | 활성화 여부 |
| requires_auth | bool | 인증 필요 여부 |
| created_at | datetime | 생성 시간 |

## 데이터베이스 스키마

### api_routes 테이블
```sql
CREATE TABLE api_routes (
    route_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    method TEXT NOT NULL,
    target_url TEXT NOT NULL,
    service_name TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    requires_auth BOOLEAN NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);
```

### api_metrics 테이블
```sql
CREATE TABLE api_metrics (
    metric_id TEXT PRIMARY KEY,
    route_id TEXT NOT NULL,
    method TEXT NOT NULL,
    path TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    response_time REAL NOT NULL,
    ip_address TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
```

## 모니터링 및 알림

### 1. 성능 모니터링
- 응답 시간 추적
- 처리량 모니터링
- 에러율 추적

### 2. 보안 모니터링
- 인증 실패 추적
- 속도 제한 위반 감지
- 의심스러운 요청 패턴 감지

### 3. 알림 설정
- 응답 시간 임계값 초과 시 알림
- 에러율 임계값 초과 시 알림
- 속도 제한 위반 시 알림

## 확장 기능

### 1. Redis 통합
- 분산 캐싱
- 분산 속도 제한
- 세션 저장소

### 2. 로드 밸런싱
- 라운드 로빈 로드 밸런싱
- 가중치 기반 로드 밸런싱
- 헬스 체크 기반 로드 밸런싱

### 3. API 버전 관리
- URL 기반 버전 관리
- 헤더 기반 버전 관리
- 버전별 라우팅

### 4. 문서 자동 생성
- OpenAPI 3.0 스펙 생성
- Swagger UI 통합
- API 문서 자동 업데이트

## 개발 가이드

### 1. 새로운 기능 추가
1. `GatewayManager` 클래스에 메서드 추가
2. 데이터베이스 스키마 업데이트
3. API 엔드포인트 추가
4. 프론트엔드 UI 업데이트

### 2. 테스트 작성
```python
def test_route_creation():
    config = GatewayConfig(data_dir="test_data")
    manager = GatewayManager(config)
    
    route_id = manager.create_route(
        name="Test Route",
        path="/api/test",
        method="GET",
        target_url="http://localhost:5001/api/test",
        service_name="test-service"
    )
    
    assert route_id in manager.routes
```

### 3. 로깅 설정
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gateway.log'),
        logging.StreamHandler()
    ]
)
```

## 문제 해결

### 1. 일반적인 문제

#### 라우트를 찾을 수 없음
- 라우트가 활성화되어 있는지 확인
- 경로 패턴이 올바른지 확인
- HTTP 메서드가 일치하는지 확인

#### 인증 실패
- JWT 토큰이 유효한지 확인
- 토큰이 만료되지 않았는지 확인
- 라우트에 인증이 필요한지 확인

#### 속도 제한 초과
- 속도 제한 설정 확인
- 요청 빈도 확인
- 속도 제한 데이터 정리

### 2. 성능 최적화
- 캐싱 활성화
- 데이터베이스 인덱스 최적화
- 로깅 레벨 조정
- 불필요한 메트릭 수집 비활성화

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 