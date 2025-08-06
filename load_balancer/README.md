# 로드 밸런서 시스템

로드 밸런서는 여러 서버에 트래픽을 분산시켜 시스템의 성능과 가용성을 향상시키는 핵심 컴포넌트입니다.

## 주요 기능

### 1. 서버 그룹 관리
- 서버 그룹 생성 및 관리
- 그룹별 로드 밸런싱 알고리즘 설정
- 서버 추가/제거 및 상태 관리

### 2. 로드 밸런싱 알고리즘
- **라운드 로빈 (Round Robin)**: 순차적으로 서버에 요청 분산
- **가중치 라운드 로빈 (Weighted Round Robin)**: 서버 가중치에 따른 분산
- **최소 연결 (Least Connections)**: 연결 수가 가장 적은 서버 선택
- **IP 해시 (IP Hash)**: 클라이언트 IP 기반 서버 선택

### 3. 헬스 체크 및 장애 감지
- 자동 헬스 체크 (설정 가능한 간격)
- 서버 상태 모니터링 (정상/비정상/점검/오프라인)
- 연속 실패 시 자동 서버 제외
- 복구 시 자동 서버 재포함

### 4. 세션 고정 (Sticky Sessions)
- 클라이언트 세션 유지
- 설정 가능한 세션 타임아웃
- 세션 매핑 관리

### 5. 실시간 모니터링
- 서버별 연결 수 추적
- 응답 시간 모니터링
- 요청/응답 메트릭 수집
- 그룹별 통계 분석

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 설정
```bash
# .env 파일 생성
LOAD_BALANCER_DATA_DIR=data/load_balancer
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=5
MAX_FAILURES=3
ENABLE_STICKY_SESSIONS=true
SESSION_TIMEOUT=1800
```

### 3. 데이터 디렉토리 생성
```bash
mkdir -p data/load_balancer
```

## 사용법

### 1. 로드 밸런서 관리자 초기화
```python
from load_balancer.load_balancer_manager import LoadBalancerManager, LoadBalancerConfig

config = LoadBalancerConfig(
    data_dir="data/load_balancer",
    health_check_interval=30,
    health_check_timeout=5,
    max_failures=3,
    enable_sticky_sessions=True,
    session_timeout=1800
)

load_balancer_manager = LoadBalancerManager(config)
```

### 2. 서버 그룹 생성
```python
group_id = load_balancer_manager.create_server_group(
    name="웹 서버 그룹",
    algorithm=LoadBalancingAlgorithm.ROUND_ROBIN
)
```

### 3. 서버 추가
```python
server_id = load_balancer_manager.add_server_to_group(
    group_id=group_id,
    name="웹 서버 1",
    host="localhost",
    port=5001,
    protocol="http",
    weight=100,
    health_check_url="/health"
)
```

### 4. 서버 선택
```python
selected_server = load_balancer_manager.select_server(
    group_id=group_id,
    client_ip="192.168.1.100",
    session_id="session123"
)
```

## API 엔드포인트

### 로드 밸런서 관리 API

#### 1. 상태 확인
```
GET /api/load-balancer/health
```

#### 2. 통계 조회
```
GET /api/load-balancer/stats
```

#### 3. 서버 그룹 관리
```
GET /api/load-balancer/groups              # 그룹 목록 조회
POST /api/load-balancer/groups             # 새 그룹 생성
PUT /api/load-balancer/groups/{id}         # 그룹 수정
DELETE /api/load-balancer/groups/{id}      # 그룹 삭제
```

#### 4. 서버 관리
```
POST /api/load-balancer/groups/{id}/servers    # 그룹에 서버 추가
PUT /api/load-balancer/servers/{id}            # 서버 정보 수정
DELETE /api/load-balancer/servers/{id}         # 서버 삭제
```

#### 5. 헬스 체크
```
GET /api/load-balancer/servers/{id}/health     # 헬스 체크 결과 조회
POST /api/load-balancer/servers/{id}/health    # 수동 헬스 체크 수행
```

#### 6. 메트릭 조회
```
GET /api/load-balancer/metrics                 # 메트릭 목록 조회
```

#### 7. 서버 선택
```
POST /api/load-balancer/select-server/{group_id}   # 로드 밸런싱 서버 선택
```

#### 8. 설정 관리
```
GET /api/load-balancer/config       # 설정 조회
PUT /api/load-balancer/config       # 설정 수정
```

#### 9. 시스템 관리
```
POST /api/load-balancer/sessions/clear        # 세션 매핑 정리
POST /api/load-balancer/connections/clear     # 연결 수 카운터 정리
```

## 설정 옵션

### LoadBalancerConfig

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| data_dir | str | - | 데이터 저장 디렉토리 |
| health_check_interval | int | 30 | 헬스 체크 간격 (초) |
| health_check_timeout | int | 5 | 헬스 체크 타임아웃 (초) |
| max_failures | int | 3 | 최대 연속 실패 횟수 |
| enable_sticky_sessions | bool | True | 세션 고정 활성화 |
| session_timeout | int | 1800 | 세션 타임아웃 (초) |

### Server

| 필드 | 타입 | 설명 |
|------|------|------|
| server_id | str | 서버 고유 ID |
| name | str | 서버 이름 |
| host | str | 서버 호스트 |
| port | int | 서버 포트 |
| protocol | str | 프로토콜 (http/https/tcp) |
| weight | int | 서버 가중치 |
| max_connections | int | 최대 연결 수 |
| is_active | bool | 활성화 여부 |
| status | ServerStatus | 서버 상태 |
| health_check_url | str | 헬스 체크 URL |
| created_at | datetime | 생성 시간 |
| updated_at | datetime | 수정 시간 |

### ServerGroup

| 필드 | 타입 | 설명 |
|------|------|------|
| group_id | str | 그룹 고유 ID |
| name | str | 그룹 이름 |
| algorithm | LoadBalancingAlgorithm | 로드 밸런싱 알고리즘 |
| servers | List[Server] | 서버 목록 |
| is_active | bool | 활성화 여부 |
| created_at | datetime | 생성 시간 |
| updated_at | datetime | 수정 시간 |

## 데이터베이스 스키마

### server_groups 테이블
```sql
CREATE TABLE server_groups (
    group_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    algorithm TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### servers 테이블
```sql
CREATE TABLE servers (
    server_id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL,
    name TEXT NOT NULL,
    host TEXT NOT NULL,
    port INTEGER NOT NULL,
    protocol TEXT NOT NULL DEFAULT 'http',
    weight INTEGER NOT NULL DEFAULT 100,
    max_connections INTEGER NOT NULL DEFAULT 1000,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'healthy',
    health_check_url TEXT NOT NULL DEFAULT '/health',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES server_groups (group_id)
);
```

### load_balancer_metrics 테이블
```sql
CREATE TABLE load_balancer_metrics (
    metric_id TEXT PRIMARY KEY,
    server_id TEXT NOT NULL,
    group_id TEXT NOT NULL,
    request_count INTEGER NOT NULL,
    response_time REAL NOT NULL,
    status_code INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (server_id) REFERENCES servers (server_id),
    FOREIGN KEY (group_id) REFERENCES server_groups (group_id)
);
```

### health_check_results 테이블
```sql
CREATE TABLE health_check_results (
    server_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    response_time REAL NOT NULL,
    status_code INTEGER NOT NULL,
    last_check TEXT NOT NULL,
    consecutive_failures INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (server_id) REFERENCES servers (server_id)
);
```

## 로드 밸런싱 알고리즘

### 1. 라운드 로빈 (Round Robin)
- 요청을 순차적으로 각 서버에 분산
- 가장 간단하고 공정한 분산 방식
- 서버 성능 차이를 고려하지 않음

### 2. 가중치 라운드 로빈 (Weighted Round Robin)
- 서버 가중치에 따라 요청 분산
- 성능이 좋은 서버에 더 많은 요청 할당
- 가중치 비율로 분산 비율 조정

### 3. 최소 연결 (Least Connections)
- 현재 연결 수가 가장 적은 서버 선택
- 서버 부하를 실시간으로 고려
- 동적 부하 분산에 효과적

### 4. IP 해시 (IP Hash)
- 클라이언트 IP 주소를 해시하여 서버 선택
- 같은 클라이언트는 항상 같은 서버로 라우팅
- 세션 유지에 유리

## 모니터링 및 알림

### 1. 성능 모니터링
- 서버별 응답 시간 추적
- 연결 수 모니터링
- 처리량 측정

### 2. 상태 모니터링
- 서버 헬스 체크 결과
- 장애 서버 감지
- 복구 상태 추적

### 3. 알림 설정
- 서버 장애 시 알림
- 응답 시간 임계값 초과 시 알림
- 연결 수 임계값 초과 시 알림

## 확장 기능

### 1. SSL 터미네이션
- HTTPS 요청 처리
- SSL 인증서 관리
- 보안 연결 지원

### 2. 자동 스케일링
- 부하에 따른 서버 자동 추가/제거
- 클라우드 환경 연동
- 동적 리소스 관리

### 3. 고급 알고리즘
- 응답 시간 기반 선택
- 지리적 위치 기반 라우팅
- 사용자 정의 알고리즘

### 4. 백업 서버
- 장애 시 백업 서버 활성화
- 자동 페일오버
- 고가용성 보장

## 개발 가이드

### 1. 새로운 알고리즘 추가
1. `LoadBalancingAlgorithm` enum에 추가
2. `LoadBalancerManager`에 선택 메서드 구현
3. API 엔드포인트 업데이트
4. 프론트엔드 UI 업데이트

### 2. 테스트 작성
```python
def test_server_selection():
    config = LoadBalancerConfig(data_dir="test_data")
    manager = LoadBalancerManager(config)
    
    group_id = manager.create_server_group("Test Group", LoadBalancingAlgorithm.ROUND_ROBIN)
    server_id = manager.add_server_to_group(group_id, "Test Server", "localhost", 5001)
    
    selected_server = manager.select_server(group_id)
    assert selected_server.server_id == server_id
```

### 3. 헬스 체크 커스터마이징
```python
def custom_health_check(server):
    # 사용자 정의 헬스 체크 로직
    try:
        response = requests.get(f"{server.protocol}://{server.host}:{server.port}/custom-health")
        return response.status_code == 200
    except:
        return False
```

## 문제 해결

### 1. 일반적인 문제

#### 서버가 선택되지 않음
- 서버가 활성화되어 있는지 확인
- 서버 상태가 정상인지 확인
- 그룹이 활성화되어 있는지 확인

#### 헬스 체크 실패
- 헬스 체크 URL이 올바른지 확인
- 서버가 응답하는지 확인
- 네트워크 연결 상태 확인

#### 세션 고정이 작동하지 않음
- 세션 고정이 활성화되어 있는지 확인
- 세션 ID가 올바르게 전달되는지 확인
- 세션 타임아웃 설정 확인

### 2. 성능 최적화
- 헬스 체크 간격 조정
- 메트릭 수집 최적화
- 데이터베이스 인덱스 최적화
- 불필요한 로깅 비활성화

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 