# 동기화 시스템 API 문서

## 📋 개요

이 문서는 동기화 시스템의 API 엔드포인트와 사용 방법을 설명합니다.

## 🔗 기본 정보

- **Base URL**: `http://localhost:5000`
- **Content-Type**: `application/json`
- **인증**: JWT 토큰 (운영 환경)

## 📊 헬스체크 API

### GET /healthz
애플리케이션의 기본 상태를 확인합니다.

**응답 예시:**
```json
{
  "ok": true,
  "database": {
    "status": "ok"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### GET /readyz
애플리케이션이 요청을 처리할 준비가 되었는지 확인합니다.

**응답 예시:**
```json
{
  "ok": true,
  "ready": true
}
```

### GET /metrics
시스템 메트릭을 조회합니다.

**응답 예시:**
```json
{
  "outbox": {
    "total_events": 150,
    "pending_events": 5,
    "delivered_events": 140,
    "failed_events": 5
  },
  "sync": {
    "total_syncs": 1000,
    "successful_syncs": 950,
    "failed_syncs": 50
  }
}
```

## 🔄 배치 동기화 API

### POST /api/mobile/sync/batch
여러 개의 동기화 항목을 한 번에 처리합니다.

**요청 헤더:**
```
Content-Type: application/json
X-Idempotency-Key: <UUID>
```

**요청 본문:**
```json
{
  "items": [
    {
      "type": "attendance",
      "idem": "uuid-1",
      "payload": {
        "user_id": 1,
        "type": "in",
        "timestamp": "2024-01-01T09:00:00Z",
        "lat": 37.5665,
        "lng": 126.9780
      }
    },
    {
      "type": "po",
      "idem": "uuid-2",
      "payload": {
        "user_id": 1,
        "items": [
          {
            "product_id": 101,
            "quantity": 10,
            "price": 1000
          }
        ],
        "total_amount": 10000
      }
    },
    {
      "type": "inventory",
      "idem": "uuid-3",
      "payload": {
        "user_id": 1,
        "product_id": 101,
        "quantity_change": -5,
        "reason": "판매"
      }
    }
  ],
  "meta": {
    "device_id": "mobile-123",
    "branch_id": 1,
    "user_id": 1
  }
}
```

**응답 예시:**
```json
{
  "ok": true,
  "results": [
    {
      "idem": "uuid-1",
      "status": "ok"
    },
    {
      "idem": "uuid-2",
      "status": "ok"
    },
    {
      "idem": "uuid-3",
      "status": "dup"
    }
  ],
  "stats": {
    "total": 3,
    "ok": 2,
    "dup": 1,
    "error": 0
  },
  "processing_time_ms": 150
}
```

**상태 코드:**
- `ok`: 성공적으로 처리됨
- `dup`: 중복 요청 (이미 처리됨)
- `error`: 처리 실패

## 📱 모바일 대시보드 API

### GET /api/mobile/dashboard
모바일 대시보드 데이터를 조회합니다.

**응답 예시:**
```json
{
  "user": {
    "id": 1,
    "username": "사용자",
    "role": "employee"
  },
  "today_schedule": "09:00 - 18:00",
  "attendance_status": "미체크",
  "pending_orders": 3,
  "inventory_alerts": 2,
  "quick_stats": {
    "today_orders": 15,
    "pending_orders": 3,
    "today_revenue": 150000,
    "staff_on_duty": 5
  },
  "recent_activities": [
    {
      "id": 1,
      "type": "attendance",
      "title": "출근 완료",
      "message": "09:00에 출근했습니다.",
      "timestamp": "2024-01-01T09:00:00Z",
      "priority": "normal"
    }
  ],
  "quick_actions": [
    {
      "id": "attendance",
      "title": "출퇴근",
      "icon": "clock",
      "color": "orange"
    },
    {
      "id": "inventory_check",
      "title": "재고 확인",
      "icon": "package",
      "color": "green"
    }
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🔧 동기화 상태 API

### GET /api/mobile/sync/status
동기화 상태를 조회합니다.

**응답 예시:**
```json
{
  "ok": true,
  "status": {
    "total_syncs": 1000,
    "successful_syncs": 950,
    "failed_syncs": 50,
    "pending_events": 5,
    "last_sync": "2024-01-01T12:00:00Z"
  }
}
```

### GET /api/mobile/sync/health
동기화 시스템의 건강 상태를 확인합니다.

**응답 예시:**
```json
{
  "ok": true,
  "health": {
    "outbox_worker": "running",
    "database": "connected",
    "redis": "connected",
    "last_processed": "2024-01-01T12:00:00Z"
  }
}
```

## 📊 Prometheus 메트릭 API

### GET /metrics/prometheus
Prometheus 형식의 메트릭을 제공합니다.

**응답 예시:**
```
# HELP outbox_events_total Total number of outbox events
# TYPE outbox_events_total counter
outbox_events_total 150

# HELP outbox_events_pending Number of pending outbox events
# TYPE outbox_events_pending gauge
outbox_events_pending 5

# HELP sync_audit_total Total number of sync audits
# TYPE sync_audit_total counter
sync_audit_total{status="ok"} 950
sync_audit_total{status="error"} 50
```

## 🚨 오류 응답

### 일반적인 오류 코드

**400 Bad Request**
```json
{
  "error": "Invalid request format",
  "code": "INVALID_REQUEST",
  "details": "Missing required field: type"
}
```

**401 Unauthorized**
```json
{
  "error": "Authentication required",
  "code": "UNAUTHORIZED"
}
```

**429 Too Many Requests**
```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

**500 Internal Server Error**
```json
{
  "error": "Internal server error",
  "code": "INTERNAL_ERROR"
}
```

## 🔒 인증 및 보안

### JWT 토큰 (운영 환경)

**요청 헤더:**
```
Authorization: Bearer <JWT_TOKEN>
```

**토큰 클레임:**
```json
{
  "user_id": 1,
  "industry_id": 1,
  "brand_id": 1,
  "branch_id": 1,
  "role": "employee",
  "exp": 1640995200
}
```

### 멱등성 키

모든 배치 동기화 요청에는 고유한 멱등성 키가 필요합니다.

**형식:** UUID v4
**예시:** `550e8400-e29b-41d4-a716-446655440000`

## 📝 사용 예시

### 1. 출퇴근 기록 동기화

```bash
curl -X POST http://localhost:5000/api/mobile/sync/batch \
  -H "Content-Type: application/json" \
  -H "X-Idempotency-Key: $(uuidgen)" \
  -d '{
    "items": [{
      "type": "attendance",
      "idem": "attendance-001",
      "payload": {
        "user_id": 1,
        "type": "in",
        "timestamp": "2024-01-01T09:00:00Z",
        "lat": 37.5665,
        "lng": 126.9780
      }
    }],
    "meta": {
      "device_id": "mobile-123",
      "branch_id": 1,
      "user_id": 1
    }
  }'
```

### 2. 발주 데이터 동기화

```bash
curl -X POST http://localhost:5000/api/mobile/sync/batch \
  -H "Content-Type: application/json" \
  -H "X-Idempotency-Key: $(uuidgen)" \
  -d '{
    "items": [{
      "type": "po",
      "idem": "po-001",
      "payload": {
        "user_id": 1,
        "items": [
          {
            "product_id": 101,
            "quantity": 10,
            "price": 1000
          }
        ],
        "total_amount": 10000,
        "notes": "긴급 발주"
      }
    }],
    "meta": {
      "device_id": "mobile-123",
      "branch_id": 1,
      "user_id": 1
    }
  }'
```

### 3. 재고 변경 동기화

```bash
curl -X POST http://localhost:5000/api/mobile/sync/batch \
  -H "Content-Type: application/json" \
  -H "X-Idempotency-Key: $(uuidgen)" \
  -d '{
    "items": [{
      "type": "inventory",
      "idem": "inventory-001",
      "payload": {
        "user_id": 1,
        "product_id": 101,
        "quantity_change": -5,
        "reason": "판매",
        "notes": "고객 판매"
      }
    }],
    "meta": {
      "device_id": "mobile-123",
      "branch_id": 1,
      "user_id": 1
    }
  }'
```

## 🔄 충돌 해결 규칙

### 출퇴근 데이터
- **서버 시간 우선**: 클라이언트 시간 무시
- **스케줄 윈도우**: 출근 06:00-10:00, 퇴근 17:00-23:00
- **중복 방지**: 같은 날 같은 타입 중복 처리 불가

### 발주 데이터
- **Last Write Wins**: 승인 전까지는 마지막 요청 우선
- **승인 후 보호**: 승인된 발주는 관리자만 수정 가능

### 재고 데이터
- **Last Write Wins**: 승인 전까지는 마지막 요청 우선
- **승인 후 보호**: 승인된 재고는 관리자만 수정 가능

## 📈 성능 고려사항

### 배치 크기 권장사항
- **최적 배치 크기**: 50-100개 항목
- **최대 배치 크기**: 200개 항목
- **처리 시간**: 평균 100-500ms

### 요청 제한
- **Rate Limit**: 초당 10회 요청
- **Burst Limit**: 최대 50회 요청
- **Timeout**: 30초

---

**마지막 업데이트**: 2024년 1월
**문서 버전**: 1.0