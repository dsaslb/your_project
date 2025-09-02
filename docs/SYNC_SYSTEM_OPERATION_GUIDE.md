# 동기화 시스템 운영 가이드

## 📋 개요

이 문서는 구현된 동기화 시스템의 운영 방법과 모니터링, 문제 해결 방법을 설명합니다.

## 🏗️ 시스템 아키텍처

### 핵심 컴포넌트

1. **배치 동기화 API** (`/api/mobile/sync/batch`)
   - 멱등성 키를 통한 중복 처리 방지
   - 항목별 결과 반환 (ok/dup/error)
   - 충돌 해결 규칙 적용

2. **Outbox 패턴** (`OutboxEvent` 모델)
   - 안정적인 이벤트 전송 보장
   - 재시도 메커니즘
   - 이벤트 유실 방지

3. **관측성 시스템**
   - `/healthz`, `/readyz`, `/metrics` 엔드포인트
   - Prometheus 메트릭 수집
   - Grafana 대시보드

## 🚀 배포 방법

### 1. Docker Compose를 사용한 배포

```bash
# 동기화 시스템 배포
docker-compose -f docker-compose.sync.yml up -d

# 서비스 상태 확인
docker-compose -f docker-compose.sync.yml ps

# 로그 확인
docker-compose -f docker-compose.sync.yml logs -f app
```

### 2. 수동 배포

```bash
# 1. 데이터베이스 테이블 생성
python reset_sync_tables.py

# 2. 서버 시작
python start_server.py

# 3. Outbox 워커 시작 (별도 터미널)
python workers/outbox_worker.py
```

## 📊 모니터링

### 1. 헬스체크 엔드포인트

```bash
# 기본 헬스체크
curl http://localhost:5000/healthz

# 준비 상태 확인
curl http://localhost:5000/readyz

# 메트릭 조회
curl http://localhost:5000/metrics
```

### 2. Prometheus 메트릭

- **Outbox 메트릭**: `outbox_events_total`, `outbox_events_pending`
- **동기화 메트릭**: `sync_audit_total`, `sync_processing_time_ms`
- **시스템 메트릭**: `process_cpu_seconds_total`, `process_resident_memory_bytes`

### 3. Grafana 대시보드

- URL: http://localhost:3000
- 기본 계정: admin/admin123
- 대시보드: "동기화 시스템 대시보드"

## 🔧 운영 작업

### 1. 동기화 테이블 관리

```bash
# 테이블 상태 확인
python -c "
from app import app
from extensions import db
from models_sync import IdempotencyKey, SyncAudit, OutboxEvent

with app.app_context():
    print(f'IdempotencyKey: {IdempotencyKey.query.count()}개')
    print(f'SyncAudit: {SyncAudit.query.count()}개')
    print(f'OutboxEvent: {OutboxEvent.query.count()}개')
"

# 오래된 데이터 정리
python -c "
from app import app
from utils.outbox import cleanup_delivered_events

with app.app_context():
    cleaned = cleanup_delivered_events(days=7)
    print(f'정리된 이벤트: {cleaned}개')
"
```

### 2. Outbox 워커 관리

```bash
# 워커 상태 확인
ps aux | grep outbox_worker

# 워커 재시작
pkill -f outbox_worker
python workers/outbox_worker.py &

# 워커 설정 변경
export OUTBOX_INTERVAL=0.5  # 0.5초 간격
export OUTBOX_BATCH_SIZE=50  # 50개씩 처리
```

### 3. 충돌 해결 규칙 관리

```python
# 출퇴근 시간 윈도우 확인
from utils.conflict_resolution import validate_schedule_window

# 현재 시간이 출근 시간인지 확인
is_checkin_time = validate_schedule_window(1, 'in')
print(f"출근 시간: {is_checkin_time}")

# 현재 시간이 퇴근 시간인지 확인
is_checkout_time = validate_schedule_window(1, 'out')
print(f"퇴근 시간: {is_checkout_time}")
```

## 🚨 문제 해결

### 1. 일반적인 문제

#### 서버 시작 실패
```bash
# 포트 사용 확인
netstat -an | findstr :5000

# 프로세스 종료
taskkill /F /IM python.exe

# 다시 시작
python start_server.py
```

#### 데이터베이스 연결 실패
```bash
# 데이터베이스 파일 확인
ls -la instance/

# 테이블 재생성
python reset_sync_tables.py
```

#### Outbox 이벤트 지연
```bash
# 대기 중인 이벤트 확인
python -c "
from app import app
from models_sync import OutboxEvent

with app.app_context():
    pending = OutboxEvent.query.filter_by(delivered=False).count()
    print(f'대기 중인 이벤트: {pending}개')
"

# 워커 재시작
pkill -f outbox_worker
python workers/outbox_worker.py &
```

### 2. 모니터링 알림

#### Outbox 이벤트 지연 (100개 이상)
- **원인**: 워커 성능 부족 또는 네트워크 문제
- **해결**: 워커 재시작, 배치 크기 증가

#### 동기화 실패율 높음 (10% 이상)
- **원인**: 충돌 해결 규칙 위반 또는 데이터 무결성 문제
- **해결**: 로그 확인, 충돌 해결 규칙 검토

#### 데이터베이스 연결 실패
- **원인**: DB 서버 다운 또는 연결 풀 고갈
- **해결**: DB 서버 재시작, 연결 풀 설정 조정

## 📈 성능 최적화

### 1. 배치 크기 조정

```bash
# 환경 변수로 배치 크기 설정
export OUTBOX_BATCH_SIZE=200  # 기본값: 100

# 워커 재시작
pkill -f outbox_worker
python workers/outbox_worker.py &
```

### 2. 처리 간격 조정

```bash
# 더 빠른 처리 (0.5초 간격)
export OUTBOX_INTERVAL=0.5

# 더 안정적인 처리 (2초 간격)
export OUTBOX_INTERVAL=2.0
```

### 3. 데이터베이스 최적화

```sql
-- 인덱스 추가
CREATE INDEX idx_outbox_events_delivered ON outbox_events(delivered);
CREATE INDEX idx_sync_audit_created_at ON sync_audits(created_at);

-- 오래된 데이터 정리
DELETE FROM outbox_events WHERE delivered = true AND delivered_at < NOW() - INTERVAL '7 days';
DELETE FROM sync_audits WHERE created_at < NOW() - INTERVAL '30 days';
```

## 🔒 보안 고려사항

### 1. API 보안

- **멱등성 키**: UUID v4 사용 권장
- **Rate Limiting**: 클라이언트별 요청 제한
- **인증**: JWT 토큰 기반 인증 (운영 환경)

### 2. 데이터 보안

- **암호화**: 민감한 데이터는 암호화 저장
- **백업**: 정기적인 데이터베이스 백업
- **접근 제어**: 데이터베이스 접근 권한 관리

## 📞 지원 및 문의

### 로그 위치
- 애플리케이션 로그: `logs/app.log`
- 워커 로그: `logs/outbox_worker.log`
- 시스템 로그: `logs/system.log`

### 모니터링 URL
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- 애플리케이션: http://localhost:5000

### 문제 보고
1. 로그 파일 확인
2. 메트릭 데이터 수집
3. 재현 단계 문서화
4. 개발팀에 보고

---

**마지막 업데이트**: 2024년 1월
**문서 버전**: 1.0
