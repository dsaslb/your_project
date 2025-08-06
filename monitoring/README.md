# 📊 시스템 모니터링

퀀텀 비즈니스 관리 시스템의 실시간 모니터링 및 알림 모듈입니다. 시스템 성능, 애플리케이션 상태, 알림 관리 등의 기능을 제공합니다.

## 주요 기능

### 🔍 실시간 모니터링
- **시스템 메트릭**: CPU, 메모리, 디스크 사용률, 네트워크 트래픽
- **애플리케이션 메트릭**: API 응답 시간, 요청 수, 에러율, 활성 세션
- **자동 수집**: 설정 가능한 간격으로 메트릭 자동 수집
- **데이터 보존**: 설정 가능한 보존 기간으로 데이터 관리

### 🚨 알림 시스템
- **임계값 기반 알림**: CPU, 메모리, 디스크, 응답 시간 임계값 설정
- **다중 심각도**: 낮음, 보통, 높음, 치명적 레벨 지원
- **알림 상태 관리**: 활성, 승인됨, 해결됨 상태 추적
- **알림 규칙**: 사용자 정의 알림 규칙 생성 및 관리

### 📈 대시보드 및 분석
- **실시간 대시보드**: 현재 시스템 상태 및 통계 표시
- **메트릭 히스토리**: 과거 데이터 조회 및 트렌드 분석
- **성능 통계**: 1시간 평균, 에러율, 업타임 등 통계 제공
- **시각화**: 차트를 통한 메트릭 변화 추이 시각화

### ⚙️ 시스템 관리
- **모니터링 제어**: 시작/중지, 수동 메트릭 수집
- **설정 관리**: 수집 간격, 보존 기간, 알림 설정
- **데이터 정리**: 오래된 데이터 자동 정리
- **상태 모니터링**: 모니터링 시스템 자체 상태 확인

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r monitoring/requirements.txt
```

### 2. 환경 변수 설정
```bash
# .env 파일 생성
MONITORING_DATA_DIR=./monitoring/data
COLLECTION_INTERVAL=60
RETENTION_DAYS=30
ALERT_ENABLED=true
EMAIL_ENABLED=false
WEBHOOK_ENABLED=false
CPU_THRESHOLD=80.0
MEMORY_THRESHOLD=85.0
DISK_THRESHOLD=90.0
RESPONSE_TIME_THRESHOLD=5000.0
```

### 3. 모니터링 시스템 초기화
```python
from monitoring.monitoring_manager import MonitoringManager, MonitoringConfig

# 모니터링 설정
config = MonitoringConfig(
    data_dir="./monitoring/data",
    collection_interval=60,
    retention_days=30,
    alert_enabled=True,
    email_enabled=False,
    webhook_enabled=False,
    cpu_threshold=80.0,
    memory_threshold=85.0,
    disk_threshold=90.0,
    response_time_threshold=5000.0
)

# 모니터링 관리자 초기화
monitoring_manager = MonitoringManager(config)
```

## API 엔드포인트

### 시스템 상태 확인
- `GET /api/monitoring/health` - 모니터링 시스템 상태 확인

### 통계 조회
- `GET /api/monitoring/stats/system` - 시스템 통계 조회
- `GET /api/monitoring/stats/application` - 애플리케이션 통계 조회
- `GET /api/monitoring/metrics/history` - 메트릭 히스토리 조회

### 알림 관리
- `GET /api/monitoring/alerts` - 알림 목록 조회
- `POST /api/monitoring/alerts/{alert_id}/acknowledge` - 알림 승인

### 알림 규칙 관리
- `GET /api/monitoring/rules` - 알림 규칙 목록 조회
- `POST /api/monitoring/rules` - 알림 규칙 생성
- `PUT /api/monitoring/rules/{rule_id}` - 알림 규칙 수정
- `DELETE /api/monitoring/rules/{rule_id}` - 알림 규칙 삭제

### 모니터링 제어
- `GET /api/monitoring/control/status` - 모니터링 상태 조회
- `POST /api/monitoring/control/start` - 모니터링 시작
- `POST /api/monitoring/control/stop` - 모니터링 중지
- `POST /api/monitoring/metrics/collect` - 수동 메트릭 수집
- `POST /api/monitoring/cleanup` - 오래된 데이터 정리

## 사용 예시

### 시스템 통계 조회
```javascript
const response = await fetch('/api/monitoring/stats/system');
const stats = await response.json();
console.log(`CPU 사용률: ${stats.data.current_cpu}%`);
console.log(`메모리 사용률: ${stats.data.current_memory}%`);
```

### 알림 규칙 생성
```javascript
const response = await fetch('/api/monitoring/rules', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'CPU 사용률 높음',
    metric_type: 'system',
    metric_name: 'cpu_percent',
    operator: '>',
    threshold: 85,
    duration: 300,
    severity: 'high'
  })
});
```

### 모니터링 시작
```javascript
const response = await fetch('/api/monitoring/control/start', {
  method: 'POST'
});
```

### 메트릭 히스토리 조회
```javascript
const response = await fetch('/api/monitoring/metrics/history?metric=cpu_percent&hours=24');
const history = await response.json();
console.log(`24시간 CPU 사용률 데이터: ${history.data.history.length}개 포인트`);
```

## 모니터링 기능 상세

### 시스템 메트릭
- **CPU 사용률**: 전체 CPU 사용률 및 코어별 사용률
- **메모리 사용률**: RAM 사용률, 가상 메모리, 스왑 사용률
- **디스크 사용률**: 각 파티션별 사용률 및 I/O 통계
- **네트워크 트래픽**: 송수신 바이트, 패킷 수, 연결 수
- **시스템 업타임**: 부팅 후 경과 시간, 로드 평균

### 애플리케이션 메트릭
- **API 응답 시간**: 엔드포인트별 평균 응답 시간
- **요청 통계**: 총 요청 수, 성공/실패 요청 수
- **에러율**: HTTP 상태 코드별 에러 비율
- **세션 관리**: 활성 세션 수, 데이터베이스 연결 수
- **성능 지표**: 처리량, 대기 시간, 큐 길이

### 알림 규칙
- **메트릭 유형**: 시스템, 애플리케이션, 사용자 정의
- **연산자**: >, >=, <, <=, ==, !=
- **임계값**: 숫자 기반 임계값 설정
- **지속 시간**: 알림 발생 전 지속 시간 (초)
- **심각도**: 낮음, 보통, 높음, 치명적

### 알림 상태
- **활성 (active)**: 임계값을 초과하여 알림 발생
- **승인됨 (acknowledged)**: 관리자가 알림을 확인
- **해결됨 (resolved)**: 조건이 정상으로 복구됨

## 프론트엔드 통합

### 모니터링 페이지 접근
```
http://localhost:3000/monitoring
```

### 주요 기능
- **실시간 대시보드**: 시스템 및 애플리케이션 통계 표시
- **알림 관리**: 알림 목록, 승인, 상세 정보 조회
- **규칙 관리**: 알림 규칙 생성, 수정, 삭제, 활성화/비활성화
- **메트릭 히스토리**: 차트를 통한 메트릭 변화 추이
- **모니터링 제어**: 시작/중지, 수동 수집, 설정 관리

## 모니터링 및 알림

### 권장 임계값
- **CPU 사용률**: 80% (높음), 90% (치명적)
- **메모리 사용률**: 85% (높음), 95% (치명적)
- **디스크 사용률**: 90% (높음), 95% (치명적)
- **API 응답 시간**: 5초 (보통), 10초 (높음)

### 알림 조건
- 임계값 초과 시 즉시 알림
- 지속 시간 동안 조건 유지 시 알림
- 조건 정상화 시 자동 해결
- 중복 알림 방지

### 성능 최적화
- 수집 간격 조정 (기본 60초)
- 데이터 보존 기간 설정 (기본 30일)
- 메모리 사용량 모니터링
- 데이터베이스 정리 스케줄링

## 개발 가이드라인

### 새로운 메트릭 추가
1. `MonitoringManager` 클래스에 메트릭 수집 메서드 추가
2. 데이터베이스 스키마 업데이트
3. API 엔드포인트 구현
4. 프론트엔드 컴포넌트 개발

### 알림 규칙 추가
```python
rule_id = monitoring_manager.create_alert_rule(
    name="사용자 정의 알림",
    metric_type="system",
    metric_name="custom_metric",
    operator=">",
    threshold=100,
    duration=60,
    severity="medium"
)
```

### 메트릭 수집 확장
```python
def collect_custom_metrics(self):
    """사용자 정의 메트릭 수집"""
    # 메트릭 수집 로직
    custom_value = self._get_custom_metric()
    
    # 메트릭 저장
    self._save_custom_metrics(custom_value)
    
    # 히스토리 업데이트
    self._update_metric_history('custom_metric', custom_value)
```

## 문제 해결

### 일반적인 문제
1. **메트릭 수집 실패**: 권한 확인, psutil 설치 확인
2. **알림 미발생**: 임계값 설정, 규칙 활성화 상태 확인
3. **성능 저하**: 수집 간격 조정, 데이터 정리 실행
4. **API 오류**: 엔드포인트 가용성, 네트워크 연결 확인

### 로그 확인
```bash
# 모니터링 로그
tail -f logs/monitoring.log

# 시스템 로그
tail -f logs/system.log
```

### 성능 최적화
- 수집 간격을 시스템 부하에 맞게 조정
- 불필요한 메트릭 비활성화
- 데이터 보존 기간 단축
- 데이터베이스 인덱스 최적화

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 