# 고도화된 플러그인 모니터링 시스템

## 개요

고도화된 플러그인 모니터링 시스템은 플러그인의 성능, 로그, 이벤트를 실시간으로 추적하고 분석하는 종합적인 모니터링 솔루션입니다. 실시간 그래프/차트, 상세 로그/이벤트 추적, 드릴다운 보기 기능을 제공합니다.

## 주요 기능

### 1. 실시간 메트릭 모니터링
- **CPU 사용률**: 플러그인별 CPU 사용량 추적
- **메모리 사용률**: 메모리 사용량 및 누수 감지
- **응답 시간**: API 응답 시간 및 성능 지표
- **에러율**: 오류 발생률 및 패턴 분석
- **처리량**: 요청 처리량 및 성능 측정
- **디스크/네트워크 I/O**: 시스템 리소스 사용량

### 2. 상세 로그 추적
- **로그 레벨별 분류**: Debug, Info, Warning, Error, Critical
- **컨텍스트 정보**: 로그 발생 시점의 상세 정보
- **스택 트레이스**: 에러 발생 시 상세 스택 정보
- **실시간 로그 스트리밍**: WebSocket을 통한 실시간 로그 전송

### 3. 이벤트 관리
- **이벤트 분류**: 시스템 이벤트, 사용자 이벤트, 오류 이벤트
- **심각도 레벨**: Low, Medium, High, Critical
- **이벤트 데이터**: 구조화된 이벤트 정보 저장
- **이벤트 알림**: 중요 이벤트 발생 시 실시간 알림

### 4. 성능 스냅샷
- **정기 스냅샷**: 주기적인 성능 상태 캡처
- **상세 메트릭**: 모든 성능 지표의 통합 스냅샷
- **트렌드 분석**: 시간별 성능 변화 추적
- **비교 분석**: 스냅샷 간 성능 비교

### 5. 분석 및 리포팅
- **트렌드 분석**: 시간별 메트릭 변화 추이
- **성능 분석**: 전체 시스템 성능 통계
- **드릴다운 보기**: 상세 데이터 탐색
- **실시간 대시보드**: 실시간 모니터링 UI

## 시스템 아키텍처

### 백엔드 구성요소

#### 1. AdvancedPluginMonitor 클래스
```python
class AdvancedPluginMonitor:
    - 메트릭 캐시 관리
    - 로그 및 이벤트 저장
    - 실시간 통계 계산
    - 데이터베이스 동기화
    - 알림 콜백 처리
```

#### 2. 데이터 모델
- **DetailedMetric**: 상세 메트릭 데이터
- **PluginLog**: 플러그인 로그 정보
- **PluginEvent**: 플러그인 이벤트 정보
- **PerformanceSnapshot**: 성능 스냅샷 데이터

#### 3. 데이터베이스 스키마
```sql
-- 메트릭 테이블
CREATE TABLE plugin_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    value REAL NOT NULL,
    timestamp DATETIME NOT NULL,
    metadata TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 로그 테이블
CREATE TABLE plugin_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    context TEXT,
    traceback TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 이벤트 테이블
CREATE TABLE plugin_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    description TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    severity TEXT NOT NULL,
    data TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 성능 스냅샷 테이블
CREATE TABLE performance_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    cpu_usage REAL NOT NULL,
    memory_usage REAL NOT NULL,
    response_time REAL NOT NULL,
    error_rate REAL NOT NULL,
    request_count INTEGER NOT NULL,
    throughput REAL NOT NULL,
    disk_io TEXT NOT NULL,
    network_io TEXT NOT NULL,
    custom_metrics TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 프론트엔드 구성요소

#### 1. AdvancedPluginMonitoring 컴포넌트
- **실시간 대시보드**: 플러그인 상태 및 메트릭 표시
- **탭 기반 인터페이스**: 개요, 메트릭, 로그, 이벤트, 스냅샷
- **필터링 기능**: 시간 범위, 메트릭 타입, 로그 레벨 필터
- **실시간 업데이트**: 30초마다 자동 데이터 새로고침

#### 2. 차트 및 시각화
- **실시간 그래프**: 메트릭 변화 추이 시각화
- **상태 표시**: 플러그인 활성/비활성 상태
- **알림 표시**: 중요 이벤트 및 에러 하이라이트
- **드릴다운 기능**: 상세 데이터 탐색

## API 엔드포인트

### 1. 시스템 상태
```
GET /api/advanced-monitoring/status
```
모니터링 시스템의 전체 상태 정보를 반환합니다.

### 2. 플러그인 관리
```
GET /api/advanced-monitoring/plugins
GET /api/advanced-monitoring/plugins/{plugin_id}/summary
```
플러그인 목록 및 개별 플러그인 요약 정보를 조회합니다.

### 3. 메트릭 관리
```
GET /api/advanced-monitoring/plugins/{plugin_id}/metrics
POST /api/advanced-monitoring/plugins/{plugin_id}/metrics
```
플러그인 메트릭을 조회하고 기록합니다.

### 4. 로그 관리
```
GET /api/advanced-monitoring/plugins/{plugin_id}/logs
POST /api/advanced-monitoring/plugins/{plugin_id}/logs
```
플러그인 로그를 조회하고 기록합니다.

### 5. 이벤트 관리
```
GET /api/advanced-monitoring/plugins/{plugin_id}/events
POST /api/advanced-monitoring/plugins/{plugin_id}/events
```
플러그인 이벤트를 조회하고 기록합니다.

### 6. 스냅샷 관리
```
GET /api/advanced-monitoring/plugins/{plugin_id}/snapshots
POST /api/advanced-monitoring/plugins/{plugin_id}/snapshots
```
성능 스냅샷을 조회하고 생성합니다.

### 7. 분석 기능
```
GET /api/advanced-monitoring/analytics/trends
GET /api/advanced-monitoring/analytics/performance
```
트렌드 분석 및 성능 통계를 제공합니다.

## 설치 및 설정

### 1. 백엔드 설정

#### 의존성 설치
```bash
pip install psutil sqlite3
```

#### 모니터링 시스템 초기화
```python
from core.backend.advanced_plugin_monitoring import advanced_plugin_monitor

# 모니터링 시작
advanced_plugin_monitor.start_monitoring()

# 알림 콜백 등록
def alert_callback(event):
    print(f"알림: {event.description}")
    
advanced_plugin_monitor.add_alert_callback(alert_callback)
```

#### API 블루프린트 등록
```python
from api.advanced_monitoring_api import advanced_monitoring_bp
app.register_blueprint(advanced_monitoring_bp)
```

### 2. 프론트엔드 설정

#### 컴포넌트 사용
```tsx
import AdvancedPluginMonitoring from '@/components/AdvancedPluginMonitoring';

export default function MonitoringPage() {
  return (
    <div className="container mx-auto py-6">
      <AdvancedPluginMonitoring />
    </div>
  );
}
```

#### 라우팅 설정
```tsx
// app/advanced-monitoring/page.tsx
import AdvancedPluginMonitoring from '@/components/AdvancedPluginMonitoring';

export default function AdvancedMonitoringPage() {
  return (
    <div className="container mx-auto py-6">
      <AdvancedPluginMonitoring />
    </div>
  );
}
```

## 사용법

### 1. 메트릭 기록
```python
from core.backend.advanced_plugin_monitoring import advanced_plugin_monitor, MetricType

# CPU 사용률 기록
advanced_plugin_monitor.record_metric(
    plugin_id="my_plugin",
    metric_type=MetricType.CPU_USAGE,
    value=45.2,
    metadata={"source": "custom_monitor"}
)

# 응답 시간 기록
advanced_plugin_monitor.record_metric(
    plugin_id="my_plugin",
    metric_type=MetricType.RESPONSE_TIME,
    value=125.5,
    metadata={"endpoint": "/api/data"}
)
```

### 2. 로그 기록
```python
from core.backend.advanced_plugin_monitoring import advanced_plugin_monitor, LogLevel

# 정보 로그
advanced_plugin_monitor.record_log(
    plugin_id="my_plugin",
    level=LogLevel.INFO,
    message="플러그인이 성공적으로 시작되었습니다.",
    context={"version": "1.0.0"}
)

# 에러 로그
advanced_plugin_monitor.record_log(
    plugin_id="my_plugin",
    level=LogLevel.ERROR,
    message="데이터베이스 연결 실패",
    context={"db_host": "localhost"},
    traceback="Traceback (most recent call last):..."
)
```

### 3. 이벤트 기록
```python
from core.backend.advanced_plugin_monitoring import advanced_plugin_monitor

# 시스템 이벤트
advanced_plugin_monitor.record_event(
    plugin_id="my_plugin",
    event_type="startup",
    description="플러그인 시작",
    severity="info",
    data={"version": "1.0.0", "config": {...}}
)

# 오류 이벤트
advanced_plugin_monitor.record_event(
    plugin_id="my_plugin",
    event_type="error",
    description="치명적인 오류 발생",
    severity="critical",
    data={"error_code": "E001", "details": {...}}
)
```

### 4. 성능 스냅샷 생성
```python
from core.backend.advanced_plugin_monitoring import advanced_plugin_monitor

# 스냅샷 데이터 준비
snapshot_data = {
    'cpu_usage': 45.2,
    'memory_usage': 67.8,
    'response_time': 125.5,
    'error_rate': 0.02,
    'request_count': 1500,
    'throughput': 25.3,
    'disk_io': {'read_bytes': 1024000, 'write_bytes': 512000},
    'network_io': {'rx_bytes': 2048000, 'tx_bytes': 1024000},
    'custom_metrics': {'custom_metric_1': 42.5}
}

# 스냅샷 생성
advanced_plugin_monitor.create_snapshot("my_plugin", snapshot_data)
```

## 테스트

### 테스트 스크립트 실행
```bash
python scripts/test_advanced_monitoring.py
```

### 테스트 항목
1. **모니터링 상태 테스트**: 시스템 상태 조회
2. **플러그인 목록 테스트**: 등록된 플러그인 조회
3. **데이터 기록 테스트**: 메트릭, 로그, 이벤트 기록
4. **데이터 조회 테스트**: 저장된 데이터 조회
5. **분석 기능 테스트**: 트렌드 및 성능 분석
6. **실시간 시뮬레이션**: 실시간 데이터 생성 테스트

## 성능 최적화

### 1. 메모리 관리
- **캐시 크기 제한**: 메트릭 10,000개, 로그 5,000개, 이벤트 2,000개
- **자동 정리**: 30일 이상 된 데이터 자동 삭제
- **배치 처리**: 데이터베이스 동기화를 배치로 처리

### 2. 데이터베이스 최적화
- **인덱스 생성**: 플러그인 ID 및 타임스탬프 인덱스
- **파티셔닝**: 시간별 테이블 파티셔닝 고려
- **커넥션 풀링**: 데이터베이스 연결 풀 관리

### 3. 네트워크 최적화
- **압축 전송**: 대용량 데이터 압축 전송
- **캐싱**: 자주 조회되는 데이터 캐싱
- **배치 API**: 여러 데이터를 한 번에 전송

## 모니터링 및 알림

### 1. 시스템 모니터링
- **메모리 사용량**: 캐시 메모리 사용량 모니터링
- **데이터베이스 성능**: 쿼리 성능 및 연결 상태
- **API 응답 시간**: 엔드포인트별 응답 시간 추적

### 2. 알림 설정
```python
def custom_alert_callback(event):
    if event.severity == 'critical':
        # 이메일 알림
        send_email_alert(event)
    elif event.severity == 'high':
        # 슬랙 알림
        send_slack_alert(event)

advanced_plugin_monitor.add_alert_callback(custom_alert_callback)
```

## 문제 해결

### 1. 일반적인 문제

#### 메트릭이 기록되지 않는 경우
- 모니터링 시스템이 시작되었는지 확인
- 플러그인 ID가 올바른지 확인
- 메트릭 타입이 유효한지 확인

#### 로그가 표시되지 않는 경우
- 로그 레벨 필터 확인
- 시간 범위 설정 확인
- 데이터베이스 연결 상태 확인

#### 성능 문제
- 캐시 크기 조정
- 데이터베이스 인덱스 확인
- 배치 처리 간격 조정

### 2. 로그 분석
```bash
# 모니터링 시스템 로그 확인
tail -f logs/app.log | grep "advanced_monitoring"

# 데이터베이스 크기 확인
ls -lh advanced_monitoring.db
```

### 3. 디버깅
```python
# 디버그 모드 활성화
import logging
logging.getLogger('core.backend.advanced_plugin_monitoring').setLevel(logging.DEBUG)

# 캐시 상태 확인
print(f"메트릭 캐시 크기: {len(advanced_plugin_monitor.metrics_cache)}")
print(f"로그 캐시 크기: {len(advanced_plugin_monitor.logs_cache)}")
```

## 향후 개발 계획

### 1. 단기 계획 (1-2개월)
- **차트 라이브러리 통합**: Chart.js 또는 D3.js 통합
- **실시간 WebSocket**: 실시간 데이터 스트리밍
- **알림 시스템 연동**: 기존 알림 시스템과 통합

### 2. 중기 계획 (3-6개월)
- **머신러닝 통합**: 이상 감지 및 예측 분석
- **대시보드 커스터마이징**: 사용자 정의 대시보드
- **API 성능 모니터링**: API 엔드포인트별 상세 모니터링

### 3. 장기 계획 (6개월 이상)
- **분산 모니터링**: 여러 서버 간 모니터링 통합
- **AI 기반 분석**: 자동 성능 최적화 제안
- **모바일 앱**: 모니터링 모바일 앱 개발

## 결론

고도화된 플러그인 모니터링 시스템은 플러그인의 성능과 안정성을 실시간으로 추적하고 분석할 수 있는 강력한 도구입니다. 실시간 그래프/차트, 상세 로그/이벤트 추적, 드릴다운 보기 기능을 통해 플러그인 시스템의 전반적인 상태를 한눈에 파악할 수 있습니다.

이 시스템을 통해 플러그인 개발자와 시스템 관리자는 더욱 효율적으로 플러그인을 모니터링하고 관리할 수 있으며, 문제 발생 시 빠른 대응이 가능합니다. 