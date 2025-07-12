# 플러그인 마이크로서비스 시스템

## 개요

플러그인 마이크로서비스 시스템은 플러그인을 독립적인 마이크로서비스로 분리하여 확장성, 격리성, 독립성을 확보하는 고도화된 아키텍처입니다. Docker 컨테이너 기반으로 각 플러그인을 독립적으로 실행하고 관리할 수 있습니다.

## 주요 기능

### 1. 마이크로서비스 격리
- **컨테이너 기반 격리**: 각 플러그인을 Docker 컨테이너로 격리
- **독립적 실행**: 플러그인 간 의존성 없이 독립적으로 실행
- **리소스 제한**: CPU, 메모리 등 리소스 사용량 제한 및 모니터링

### 2. 서비스 타입 지원
- **REST API**: HTTP 기반 REST API 서비스
- **WebSocket**: 실시간 통신을 위한 WebSocket 서비스
- **Background Worker**: 비동기 작업 처리 워커
- **Scheduler**: 정기적인 작업 스케줄링
- **Worker**: 일반적인 작업 처리 워커

### 3. 자동화된 관리
- **자동 배포**: 플러그인 코드를 자동으로 컨테이너화하여 배포
- **헬스 체크**: 서비스 상태 자동 모니터링
- **자동 재시작**: 장애 발생 시 자동 재시작
- **로드 밸런싱**: 여러 인스턴스 간 로드 분산

### 4. 네트워크 관리
- **격리된 네트워크**: 플러그인 전용 네트워크 구성
- **포트 관리**: 자동 포트 할당 및 관리
- **서비스 디스커버리**: 동적 서비스 발견 및 등록

## 시스템 아키텍처

### 백엔드 구성요소

#### 1. PluginMicroserviceManager (core/backend/plugin_microservice_manager.py)
```python
class PluginMicroserviceManager:
    """플러그인 마이크로서비스 관리 시스템"""
    
    def __init__(self, base_path: str = "plugins", docker_host: str = "unix://var/run/docker.sock"):
        self.base_path = Path(base_path)
        self.docker_host = docker_host
        self.docker_client = None
        self.services: Dict[str, ServiceInstance] = {}
        self.networks: Dict[str, Any] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.health_check_interval = 30
        self.port_manager = PortManager()
```

**주요 기능:**
- Docker 컨테이너 관리
- 서비스 라이프사이클 관리
- 네트워크 및 포트 관리
- 헬스 체크 및 모니터링

#### 2. ServiceConfig 데이터 클래스
```python
@dataclass
class ServiceConfig:
    name: str
    plugin_id: str
    service_type: ServiceType
    port: int
    host: str = "0.0.0.0"
    environment: Dict[str, str] = None
    volumes: List[str] = None
    networks: List[str] = None
    depends_on: List[str] = None
    health_check: Dict[str, Any] = None
    resource_limits: Dict[str, Any] = None
    restart_policy: str = "unless-stopped"
    version: str = "latest"
```

#### 3. ServiceInstance 데이터 클래스
```python
@dataclass
class ServiceInstance:
    id: str
    config: ServiceConfig
    status: ServiceStatus
    container_id: Optional[str]
    container_name: str
    port: int
    host_port: int
    start_time: Optional[datetime]
    last_health_check: Optional[datetime]
    health_status: ServiceStatus
    resource_usage: Dict[str, Any]
    logs: List[Dict[str, Any]]
    error_message: Optional[str]
```

#### 4. NetworkConfig 데이터 클래스
```python
@dataclass
class NetworkConfig:
    name: str
    driver: str = "bridge"
    subnet: str = "172.20.0.0/16"
    gateway: str = "172.20.0.1"
    enable_ipv6: bool = False
    internal: bool = False
    labels: Dict[str, str] = None
```

### 프론트엔드 구성요소

#### 1. PluginMicroserviceDashboard (frontend/src/components/PluginMicroserviceDashboard.tsx)
- 서비스 목록 및 상태 모니터링
- 서비스 생성, 시작, 중지, 재시작, 삭제
- 실시간 로그 및 메트릭 확인
- 템플릿 기반 서비스 생성

#### 2. 플러그인 마이크로서비스 페이지 (frontend/src/app/plugin-microservice/page.tsx)
- 전체 마이크로서비스 시스템 접근점

## API 엔드포인트

### 서비스 관리 API

#### 1. 서비스 목록 조회
```http
GET /api/plugin-microservice/services?plugin_id=test_plugin&status=running
```

**응답 예시:**
```json
{
  "success": true,
  "data": [
    {
      "id": "test_service_123",
      "name": "테스트 서비스",
      "plugin_id": "test_plugin",
      "service_type": "rest_api",
      "status": "running",
      "health_status": "healthy",
      "port": 8080,
      "host_port": 8080,
      "start_time": "2024-01-01T00:00:00",
      "last_health_check": "2024-01-01T00:00:00",
      "resource_usage": {},
      "error_message": null
    }
  ],
  "message": "1개의 서비스를 찾았습니다."
}
```

#### 2. 서비스 생성
```http
POST /api/plugin-microservice/services
Content-Type: application/json

{
  "plugin_id": "test_plugin",
  "name": "테스트 서비스",
  "service_type": "rest_api",
  "port": 8080,
  "host": "0.0.0.0",
  "environment": {
    "NODE_ENV": "production",
    "LOG_LEVEL": "info"
  },
  "volumes": ["/host/path:/container/path"],
  "networks": ["plugin_network"],
  "depends_on": ["database"],
  "restart_policy": "unless-stopped",
  "version": "latest"
}
```

#### 3. 서비스 조회
```http
GET /api/plugin-microservice/services/{service_id}
```

#### 4. 서비스 시작
```http
POST /api/plugin-microservice/services/{service_id}/start
```

#### 5. 서비스 중지
```http
POST /api/plugin-microservice/services/{service_id}/stop
```

#### 6. 서비스 재시작
```http
POST /api/plugin-microservice/services/{service_id}/restart
```

#### 7. 서비스 삭제
```http
DELETE /api/plugin-microservice/services/{service_id}
```

### 서비스 모니터링 API

#### 1. 서비스 로그 조회
```http
GET /api/plugin-microservice/services/{service_id}/logs?lines=100
```

**응답 예시:**
```json
{
  "success": true,
  "data": [
    "2024-01-01T00:00:00 INFO: 서비스 시작",
    "2024-01-01T00:00:01 INFO: 헬스 체크 통과",
    "2024-01-01T00:00:02 INFO: 요청 처리 완료"
  ],
  "message": "3개의 로그 항목을 찾았습니다."
}
```

#### 2. 서비스 메트릭 조회
```http
GET /api/plugin-microservice/services/{service_id}/metrics
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "cpu_percent": 15.5,
    "memory_usage_mb": 256.0,
    "memory_limit_mb": 512.0,
    "memory_percent": 50.0,
    "network_rx_mb": 10.5,
    "network_tx_mb": 5.2,
    "timestamp": "2024-01-01T00:00:00"
  },
  "message": "서비스 메트릭을 성공적으로 조회했습니다."
}
```

#### 3. 서비스 스케일링
```http
POST /api/plugin-microservice/services/{service_id}/scale
Content-Type: application/json

{
  "replicas": 3
}
```

### 서비스 디스커버리 API

#### 1. 서비스 디스커버리 정보
```http
GET /api/plugin-microservice/discovery
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "services": [
      {
        "id": "test_service",
        "name": "테스트 서비스",
        "plugin_id": "test_plugin",
        "type": "rest_api",
        "status": "running",
        "health": "healthy",
        "endpoint": "http://localhost:8080",
        "port": 8080,
        "start_time": "2024-01-01T00:00:00"
      }
    ],
    "networks": [
      {
        "name": "plugin_network",
        "id": "network_123",
        "driver": "bridge",
        "scope": "local"
      }
    ],
    "total_services": 1,
    "healthy_services": 1,
    "unhealthy_services": 0
  },
  "message": "서비스 디스커버리 정보를 성공적으로 조회했습니다."
}
```

### 템플릿 관리 API

#### 1. 서비스 템플릿 목록
```http
GET /api/plugin-microservice/templates
```

**응답 예시:**
```json
{
  "success": true,
  "data": [
    {
      "id": "rest_api_basic",
      "name": "기본 REST API 서비스",
      "description": "Flask 기반 기본 REST API 서비스",
      "service_type": "rest_api",
      "port": 8080,
      "template": {
        "name": "rest_api_service",
        "service_type": "rest_api",
        "port": 8080,
        "environment": {
          "FLASK_ENV": "production",
          "FLASK_DEBUG": "false"
        },
        "health_check": {
          "url": "http://localhost:8080/health",
          "interval": 30,
          "timeout": 10,
          "retries": 3
        },
        "resource_limits": {
          "memory": "512m",
          "cpu": "0.5"
        }
      }
    }
  ],
  "message": "1개의 서비스 템플릿을 찾았습니다."
}
```

#### 2. 템플릿으로 서비스 생성
```http
POST /api/plugin-microservice/templates/{template_id}/create
Content-Type: application/json

{
  "plugin_id": "test_plugin",
  "name": "템플릿 서비스"
}
```

### 관리 및 유지보수 API

#### 1. 리소스 정리
```http
POST /api/plugin-microservice/cleanup
Content-Type: application/json

{
  "days": 30
}
```

#### 2. 헬스 체크
```http
GET /api/plugin-microservice/health
```

## 서비스 템플릿

### 1. 기본 REST API 서비스 (rest_api_basic)
- **설명**: Flask 기반 기본 REST API 서비스
- **포트**: 8080
- **환경 변수**: FLASK_ENV, FLASK_DEBUG
- **헬스 체크**: /health 엔드포인트
- **리소스 제한**: 메모리 512MB, CPU 0.5

### 2. WebSocket 서비스 (websocket_service)
- **설명**: 실시간 통신을 위한 WebSocket 서비스
- **포트**: 8081
- **환경 변수**: WS_HOST, WS_PORT
- **헬스 체크**: /health 엔드포인트
- **리소스 제한**: 메모리 256MB, CPU 0.3

### 3. 백그라운드 워커 (background_worker)
- **설명**: 비동기 작업 처리를 위한 백그라운드 워커
- **포트**: 8082
- **환경 변수**: WORKER_POOL_SIZE, TASK_TIMEOUT
- **헬스 체크**: /health 엔드포인트
- **리소스 제한**: 메모리 1GB, CPU 1.0

### 4. 스케줄러 서비스 (scheduler_service)
- **설명**: 정기적인 작업 스케줄링을 위한 서비스
- **포트**: 8083
- **환경 변수**: SCHEDULER_INTERVAL, MAX_JOBS
- **헬스 체크**: /health 엔드포인트
- **리소스 제한**: 메모리 256MB, CPU 0.2

## 서비스 라이프사이클

### 1. 서비스 생성
```python
# 서비스 설정 생성
config = ServiceConfig(
    name="my_service",
    plugin_id="my_plugin",
    service_type=ServiceType.REST_API,
    port=8080,
    environment={"NODE_ENV": "production"},
    resource_limits={"memory": "512m", "cpu": "0.5"}
)

# 서비스 생성
service_id = await microservice_manager.create_service("my_plugin", config)
```

### 2. 서비스 시작
```python
# 서비스 시작
await microservice_manager._start_service(service)
```

### 3. 헬스 체크
```python
# 헬스 체크 실행
await microservice_manager._check_service_health(service)
```

### 4. 서비스 중지
```python
# 서비스 중지
success = await microservice_manager.stop_service(service_id)
```

### 5. 서비스 삭제
```python
# 서비스 삭제
success = await microservice_manager.delete_service(service_id)
```

## 네트워크 구성

### 1. 기본 네트워크
- **이름**: plugin_network
- **드라이버**: bridge
- **서브넷**: 172.20.0.0/16
- **게이트웨이**: 172.20.0.1

### 2. 격리된 네트워크
- **이름**: plugin_isolated
- **드라이버**: bridge
- **내부 네트워크**: true
- **외부 접근 제한**: 활성화

### 3. 네트워크 생성
```python
network_config = NetworkConfig(
    name="custom_network",
    driver="bridge",
    subnet="172.21.0.0/16",
    gateway="172.21.0.1",
    enable_ipv6=True
)

success = microservice_manager._create_network(network_config)
```

## 포트 관리

### 1. 자동 포트 할당
```python
# 포트 할당
port = port_manager.allocate_port()

# 포트 해제
port_manager.release_port(port)

# 포트 사용 여부 확인
is_used = port_manager.is_port_allocated(port)
```

### 2. 포트 범위
- **시작 포트**: 8000
- **종료 포트**: 9000
- **사용 가능한 포트**: 1000개

## 리소스 모니터링

### 1. CPU 사용률
```python
# CPU 사용률 조회
metrics = await microservice_manager.get_service_metrics(service_id)
cpu_percent = metrics["cpu_percent"]
```

### 2. 메모리 사용량
```python
# 메모리 사용량 조회
memory_usage_mb = metrics["memory_usage_mb"]
memory_limit_mb = metrics["memory_limit_mb"]
memory_percent = metrics["memory_percent"]
```

### 3. 네트워크 통계
```python
# 네트워크 통계 조회
network_rx_mb = metrics["network_rx_mb"]
network_tx_mb = metrics["network_tx_mb"]
```

## 헬스 체크 시스템

### 1. 헬스 체크 설정
```python
health_check = {
    "url": "http://localhost:8080/health",
    "interval": 30,  # 초
    "timeout": 10,   # 초
    "retries": 3
}
```

### 2. 헬스 체크 실행
```python
async def _check_service_health(self, service: ServiceInstance):
    try:
        health_url = service.config.health_check["url"]
        async with aiohttp.ClientSession() as session:
            async with session.get(health_url, timeout=service.config.health_check["timeout"]) as response:
                if response.status == 200:
                    service.health_status = ServiceStatus.HEALTHY
                else:
                    service.health_status = ServiceStatus.UNHEALTHY
    except Exception as e:
        service.health_status = ServiceStatus.UNHEALTHY
        service.error_message = str(e)
```

### 3. 자동 모니터링
```python
def _start_health_monitoring(self):
    def health_monitor():
        while True:
            try:
                asyncio.run(self._check_all_services_health())
                time.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"헬스 체크 모니터링 오류: {e}")
                time.sleep(10)
    
    monitor_thread = threading.Thread(target=health_monitor, daemon=True)
    monitor_thread.start()
```

## 사용 예시

### 1. 기본 서비스 생성
```python
from core.backend.plugin_microservice_manager import (
    PluginMicroserviceManager, ServiceConfig, ServiceType
)

# 마이크로서비스 매니저 초기화
manager = PluginMicroserviceManager()

# 서비스 설정
config = ServiceConfig(
    name="my_rest_api",
    plugin_id="my_plugin",
    service_type=ServiceType.REST_API,
    port=8080,
    environment={"NODE_ENV": "production"},
    resource_limits={"memory": "512m", "cpu": "0.5"}
)

# 서비스 생성
service_id = await manager.create_service("my_plugin", config)
print(f"서비스 생성 완료: {service_id}")
```

### 2. 서비스 상태 확인
```python
# 서비스 조회
service = await manager.get_service(service_id)
print(f"서비스 상태: {service.status}")
print(f"헬스 상태: {service.health_status}")

# 서비스 목록 조회
services = await manager.list_services(plugin_id="my_plugin")
for service in services:
    print(f"{service['name']}: {service['status']}")
```

### 3. 서비스 제어
```python
# 서비스 시작
await manager.restart_service(service_id)

# 서비스 중지
await manager.stop_service(service_id)

# 서비스 삭제
await manager.delete_service(service_id)
```

### 4. 모니터링
```python
# 서비스 로그 조회
logs = await manager.get_service_logs(service_id, lines=100)
for log in logs:
    print(log)

# 서비스 메트릭 조회
metrics = await manager.get_service_metrics(service_id)
print(f"CPU 사용률: {metrics['cpu_percent']}%")
print(f"메모리 사용률: {metrics['memory_percent']}%")
```

### 5. 서비스 디스커버리
```python
# 디스커버리 정보 조회
discovery = await manager.get_service_discovery_info()
print(f"총 서비스: {discovery['total_services']}")
print(f"정상 서비스: {discovery['healthy_services']}")
print(f"비정상 서비스: {discovery['unhealthy_services']}")

# 서비스 엔드포인트 확인
for service in discovery['services']:
    print(f"{service['name']}: {service['endpoint']}")
```

## 프론트엔드 사용법

### 1. 대시보드 접근
```
http://localhost:3000/plugin-microservice
```

### 2. 서비스 관리
- **서비스 목록**: 등록된 모든 서비스 확인
- **서비스 생성**: 새 서비스 정의 및 등록
- **서비스 제어**: 시작, 중지, 재시작, 삭제
- **상태 모니터링**: 실시간 상태 및 헬스 체크 확인

### 3. 템플릿 사용
- **템플릿 선택**: 미리 정의된 템플릿 중 선택
- **빠른 생성**: 템플릿을 사용한 빠른 서비스 생성
- **커스터마이징**: 템플릿 기반 설정 수정

### 4. 모니터링 및 로그
- **실시간 로그**: 서비스 실행 로그 실시간 확인
- **메트릭 대시보드**: CPU, 메모리, 네트워크 사용량 확인
- **헬스 상태**: 서비스 상태 및 오류 정보 확인

## 설정 및 환경 변수

### 1. Docker 설정
```bash
# Docker 데몬 시작
sudo systemctl start docker

# Docker 권한 설정
sudo usermod -aG docker $USER

# Docker 네트워크 확인
docker network ls
```

### 2. 환경 변수
```bash
# Docker 호스트 설정
export DOCKER_HOST="unix://var/run/docker.sock"

# 플러그인 경로 설정
export PLUGIN_BASE_PATH="/path/to/plugins"

# 포트 범위 설정
export PORT_START=8000
export PORT_END=9000
```

### 3. 리소스 제한
```python
# 메모리 제한
resource_limits = {
    "memory": "512m",  # 512MB
    "cpu": "0.5"       # CPU 50%
}

# 네트워크 제한
network_config = {
    "bandwidth": "100m",  # 100MB/s
    "connections": 1000   # 최대 연결 수
}
```

## 보안 고려사항

### 1. 컨테이너 보안
- **권한 제한**: 최소 권한 원칙 적용
- **네트워크 격리**: 불필요한 네트워크 접근 차단
- **리소스 제한**: CPU, 메모리 사용량 제한

### 2. 이미지 보안
- **베이스 이미지**: 신뢰할 수 있는 베이스 이미지 사용
- **보안 스캔**: 컨테이너 이미지 보안 취약점 검사
- **업데이트**: 정기적인 보안 업데이트

### 3. 네트워크 보안
- **방화벽**: 필요한 포트만 개방
- **SSL/TLS**: HTTPS 통신 강제
- **인증**: API 인증 및 권한 확인

## 성능 최적화

### 1. 리소스 최적화
- **메모리 사용량**: 적절한 메모리 제한 설정
- **CPU 사용률**: CPU 사용량 모니터링 및 조정
- **디스크 I/O**: 볼륨 마운트 최적화

### 2. 네트워크 최적화
- **포트 재사용**: 효율적인 포트 관리
- **로드 밸런싱**: 여러 인스턴스 간 부하 분산
- **캐싱**: 자주 사용되는 데이터 캐싱

### 3. 모니터링 최적화
- **헬스 체크 간격**: 적절한 헬스 체크 주기 설정
- **로그 관리**: 로그 파일 크기 및 보관 기간 관리
- **메트릭 수집**: 효율적인 메트릭 수집 및 저장

## 문제 해결

### 1. 일반적인 문제

#### 서비스 시작 실패
```bash
# Docker 상태 확인
docker ps -a

# 컨테이너 로그 확인
docker logs <container_id>

# 네트워크 확인
docker network ls
```

#### 포트 충돌
```python
# 포트 사용 여부 확인
is_used = port_manager.is_port_allocated(port)

# 다른 포트 할당
new_port = port_manager.allocate_port()
```

#### 메모리 부족
```python
# 리소스 제한 조정
resource_limits = {
    "memory": "1g",  # 메모리 증가
    "cpu": "1.0"     # CPU 증가
}
```

### 2. 디버깅 방법

#### 로그 분석
```python
# 상세 로그 확인
logs = await manager.get_service_logs(service_id, lines=200)
for log in logs:
    if "ERROR" in log:
        print(f"오류: {log}")
```

#### 메트릭 분석
```python
# 리소스 사용량 확인
metrics = await manager.get_service_metrics(service_id)
if metrics["cpu_percent"] > 80:
    print("CPU 사용률이 높습니다")
if metrics["memory_percent"] > 90:
    print("메모리 사용률이 높습니다")
```

### 3. 성능 문제 해결

#### 높은 CPU 사용률
- 리소스 제한 증가
- 불필요한 프로세스 제거
- 코드 최적화

#### 높은 메모리 사용률
- 메모리 제한 증가
- 메모리 누수 확인
- 가비지 컬렉션 최적화

#### 네트워크 지연
- 네트워크 대역폭 확인
- 로드 밸런서 설정
- 캐싱 전략 적용

## 확장 및 커스터마이징

### 1. 새로운 서비스 타입 추가
```python
class CustomServiceType(ServiceType):
    CUSTOM_SERVICE = "custom_service"

async def _execute_custom_service(self, service: ServiceInstance):
    """커스텀 서비스 실행 로직"""
    # 커스텀 로직 구현
    pass
```

### 2. 커스텀 헬스 체크
```python
async def custom_health_check(self, service: ServiceInstance):
    """커스텀 헬스 체크 로직"""
    try:
        # 커스텀 헬스 체크 구현
        response = await custom_check_logic(service)
        return response.status == 200
    except Exception as e:
        return False
```

### 3. 외부 모니터링 시스템 연동
```python
async def integrate_with_monitoring(self, service: ServiceInstance):
    """외부 모니터링 시스템 연동"""
    # Prometheus, Grafana 등과 연동
    metrics = await self.get_service_metrics(service.id)
    await external_monitoring.send_metrics(metrics)
```

## 결론

플러그인 마이크로서비스 시스템은 플러그인을 독립적인 마이크로서비스로 분리하여 확장성, 격리성, 독립성을 확보합니다. Docker 컨테이너 기반의 격리된 환경에서 각 플러그인이 독립적으로 실행되며, 자동화된 관리 시스템을 통해 효율적인 운영이 가능합니다.

이 시스템을 통해 플러그인 개발자는 복잡한 인프라 관리에 신경 쓰지 않고 핵심 기능 개발에 집중할 수 있으며, 운영자는 안정적이고 확장 가능한 플러그인 아키텍처를 구축할 수 있습니다. 