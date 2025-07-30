# Your Program API 참조 문서

## 📋 목차

1. [API 개요](#api-개요)
2. [인증 및 권한](#인증-및-권한)
3. [통합 API (포트 8000)](#통합-api-포트-8000)
4. [AI/ML API (포트 8001)](#aiml-api-포트-8001)
5. [데이터 분석 API (포트 8002)](#데이터-분석-api-포트-8002)
6. [블록체인 API (포트 8003)](#블록체인-api-포트-8003)
7. [IoT 플랫폼 API (포트 8004)](#iot-플랫폼-api-포트-8004)
8. [보안 모니터링 API (포트 8007)](#보안-모니터링-api-포트-8007)
9. [성능 모니터링 API](#성능-모니터링-api)
10. [에러 코드 및 응답](#에러-코드-및-응답)
11. [SDK 및 클라이언트 라이브러리](#sdk-및-클라이언트-라이브러리)
12. [예제 및 튜토리얼](#예제-및-튜토리얼)

---

## API 개요

### 플랫폼 아키텍처

Your Program은 마이크로서비스 아키텍처를 기반으로 하며, 각 서비스는 독립적인 API를 제공합니다.

```
API 게이트웨이 (포트 8000) - 중앙 집중식 API 접근점
├── AI/ML 플랫폼 (포트 8001)
├── 데이터 분석 (포트 8002)  
├── 블록체인 (포트 8003)
├── IoT 플랫폼 (포트 8004)
├── 모바일 백엔드 (포트 8006)
└── 보안 모니터링 (포트 8007)
```

### 기본 설정

#### Base URLs
```
프로덕션: https://api.yourprogram.com
개발환경: http://localhost:8000
테스트: https://test-api.yourprogram.com
```

#### HTTP 헤더
```http
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>
X-API-Version: 1.0
X-Request-ID: <UUID> (선택사항)
```

#### 응답 형식
모든 API는 일관된 JSON 응답 형식을 사용합니다:

```json
{
  "status": "success|error|warning",
  "message": "설명 메시지",
  "data": {}, 
  "timestamp": "2024-01-19T10:30:00Z",
  "request_id": "uuid-here"
}
```

---

## 인증 및 권한

### JWT 토큰 기반 인증

#### 토큰 발급
```http
POST /auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123",
  "remember_me": false
}
```

**응답:**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 123,
      "username": "user@example.com",
      "role": "admin",
      "permissions": ["read:all", "write:monitoring"]
    }
  }
}
```

#### 토큰 갱신
```http
POST /auth/refresh
Authorization: Bearer <REFRESH_TOKEN>
```

#### 권한 레벨
```
admin: 모든 API 접근 가능
operator: 모니터링 및 분석 API 접근
developer: 개발 관련 API 접근  
user: 기본 사용자 API 접근
readonly: 읽기 전용 API 접근
```

---

## 통합 API (포트 8000)

### 시스템 상태 및 헬스 체크

#### 전체 시스템 상태 조회
```http
GET /health
```

**응답:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-19T10:30:00Z",
  "systems": {
    "api_gateway": {
      "status": "healthy",
      "response_time": 25,
      "cpu_usage": 45.2,
      "memory_usage": 67.8
    },
    "ai_ml_platform": {
      "status": "healthy", 
      "response_time": 340,
      "active_models": 3,
      "prediction_requests": 1234
    },
    "security_monitor": {
      "status": "healthy",
      "threats_detected": 0,
      "events_processed": 47
    }
  }
}
```

#### 특정 서비스 상태 조회
```http
GET /health/{service_name}
```

**파라미터:**
- `service_name`: api_gateway, ai_ml, data_analysis, blockchain, iot, security

### 시스템 메트릭

#### 전체 시스템 메트릭 조회
```http
GET /metrics
Authorization: Bearer <TOKEN>
```

**쿼리 파라미터:**
- `start_time`: ISO 8601 형식 시작 시간
- `end_time`: ISO 8601 형식 종료 시간
- `interval`: 데이터 간격 (1m, 5m, 1h, 1d)
- `metrics`: 조회할 메트릭 (cpu,memory,network,disk)

**응답:**
```json
{
  "status": "success",
  "data": {
    "time_range": {
      "start": "2024-01-19T09:00:00Z",
      "end": "2024-01-19T10:00:00Z",
      "interval": "5m"
    },
    "metrics": {
      "cpu_usage": [
        {"timestamp": "2024-01-19T09:00:00Z", "value": 45.2},
        {"timestamp": "2024-01-19T09:05:00Z", "value": 47.8}
      ],
      "memory_usage": [
        {"timestamp": "2024-01-19T09:00:00Z", "value": 67.8},
        {"timestamp": "2024-01-19T09:05:00Z", "value": 69.1}
      ]
    }
  }
}
```

### 서비스 관리

#### 서비스 재시작
```http
POST /services/{service_name}/restart
Authorization: Bearer <TOKEN>
```

#### 서비스 설정 업데이트
```http
PUT /services/{service_name}/config
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "max_workers": 4,
  "timeout": 30,
  "retry_count": 3
}
```

---

## AI/ML API (포트 8001)

### 모델 관리

#### 모델 목록 조회
```http
GET /models
Authorization: Bearer <TOKEN>
```

**응답:**
```json
{
  "status": "success",
  "data": {
    "models": [
      {
        "id": "model_001",
        "name": "사용자 추천 모델",
        "version": "v2.1",
        "status": "active",
        "accuracy": 94.2,
        "created_at": "2024-01-15T10:00:00Z",
        "last_trained": "2024-01-18T14:30:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 10
  }
}
```

#### 새 모델 훈련
```http
POST /models/train
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "name": "고객 이탈 예측 모델",
  "algorithm": "random_forest",
  "dataset": "customer_data.csv",
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 10,
    "min_samples_split": 5
  },
  "validation_method": "k_fold",
  "k_folds": 5
}
```

### 모델 추론

#### 실시간 예측
```http
POST /models/{model_id}/predict
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "features": {
    "age": 25,
    "income": 50000,
    "usage_hours": 120,
    "last_activity": "2024-01-18"
  }
}
```

**응답:**
```json
{
  "status": "success",
  "data": {
    "prediction": {
      "churn_probability": 0.234,
      "confidence": 0.872,
      "response_time_ms": 15
    },
    "model_info": {
      "id": "model_001",
      "version": "v2.1",
      "accuracy": 94.2
    }
  }
}
```

#### 배치 예측
```http
POST /models/{model_id}/predict/batch
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "data": [
    {"age": 25, "income": 50000, "usage_hours": 120},
    {"age": 35, "income": 75000, "usage_hours": 200}
  ]
}
```

### 모델 성능 모니터링

#### 모델 성능 메트릭 조회
```http
GET /models/{model_id}/metrics
Authorization: Bearer <TOKEN>
```

**쿼리 파라미터:**
- `start_date`: 시작 날짜 (YYYY-MM-DD)
- `end_date`: 종료 날짜 (YYYY-MM-DD)
- `metric_type`: accuracy, precision, recall, f1_score

---

## 데이터 분석 API (포트 8002)

### 대시보드 관리

#### 대시보드 목록 조회
```http
GET /dashboards
Authorization: Bearer <TOKEN>
```

#### 새 대시보드 생성
```http
POST /dashboards
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "name": "월간 매출 분석",
  "description": "월별 매출 동향 및 분석 대시보드",
  "tags": ["매출", "월간", "KPI"],
  "sharing": "team",
  "template": "sales_analysis"
}
```

### 차트 및 시각화

#### 차트 생성
```http
POST /charts
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "type": "line_chart",
  "title": "월간 매출 트렌드",
  "data_source": {
    "type": "database",
    "connection": "postgresql_main",
    "query": "SELECT month, revenue FROM sales_data WHERE year = 2024"
  },
  "config": {
    "x_axis": "month",
    "y_axis": "revenue",
    "color_scheme": "auto"
  }
}
```

### SQL 쿼리 실행

#### 쿼리 실행
```http
POST /query/execute
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "query": "SELECT DATE_TRUNC('month', created_at) as month, COUNT(*) as new_customers FROM customers WHERE created_at >= '2024-01-01' GROUP BY month ORDER BY month",
  "connection": "postgresql_main",
  "limit": 1000
}
```

**응답:**
```json
{
  "status": "success",
  "data": {
    "columns": ["month", "new_customers"],
    "rows": [
      ["2024-01-01T00:00:00Z", 150],
      ["2024-02-01T00:00:00Z", 175]
    ],
    "execution_time_ms": 245,
    "row_count": 2
  }
}
```

---

## 블록체인 API (포트 8003)

### 네트워크 정보

#### 블록체인 상태 조회
```http
GET /blockchain/status
Authorization: Bearer <TOKEN>
```

**응답:**
```json
{
  "status": "success",
  "data": {
    "network_status": "healthy",
    "current_block": 15247,
    "connected_nodes": 5,
    "average_block_time": 3.2,
    "pending_transactions": 23,
    "gas_price_gwei": 20
  }
}
```

### 트랜잭션 관리

#### 새 트랜잭션 생성
```http
POST /blockchain/transactions
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "type": "data_storage",
  "to_address": "0x742d35Cc6Ef90Ad8E47c2F5165E72E2e77c7E8e2",
  "data": {
    "document_hash": "0x1234567890abcdef",
    "metadata": {
      "file_name": "contract.pdf",
      "timestamp": "2024-01-19T10:30:00Z"
    }
  },
  "gas_limit": 21000,
  "gas_price": 20
}
```

#### 트랜잭션 상태 조회
```http
GET /blockchain/transactions/{transaction_hash}
Authorization: Bearer <TOKEN>
```

### 스마트 컨트랙트

#### 컨트랙트 배포
```http
POST /blockchain/contracts/deploy
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "contract_code": "pragma solidity ^0.8.0; contract MyContract { ... }",
  "constructor_params": [],
  "gas_limit": 1000000
}
```

#### 컨트랙트 함수 호출
```http
POST /blockchain/contracts/{contract_address}/call
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "function_name": "getValue",
  "parameters": ["param1", "param2"],
  "gas_limit": 50000
}
```

---

## IoT 플랫폼 API (포트 8004)

### 디바이스 관리

#### 디바이스 목록 조회
```http
GET /devices
Authorization: Bearer <TOKEN>
```

**쿼리 파라미터:**
- `status`: online, offline, warning, error
- `type`: sensor, actuator, gateway
- `location`: 디바이스 위치 필터

**응답:**
```json
{
  "status": "success",
  "data": {
    "devices": [
      {
        "id": "device_001",
        "name": "온도센서-01",
        "type": "sensor",
        "status": "online",
        "location": "서버실 A동 2층",
        "last_seen": "2024-01-19T10:28:00Z",
        "battery_level": 85,
        "latest_data": {
          "temperature": 23.5,
          "humidity": 65.2
        }
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 20
  }
}
```

#### 새 디바이스 등록
```http
POST /devices
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "name": "온도센서-02",
  "type": "sensor",
  "model": "DHT22",
  "location": "서버실 B동 1층",
  "connection": {
    "protocol": "mqtt",
    "broker": "mqtt.yourserver.com",
    "port": 1883,
    "topic": "sensors/temperature/02"
  },
  "authentication": {
    "device_id": "auto_generate",
    "api_key": "generate"
  }
}
```

### 디바이스 데이터

#### 센서 데이터 조회
```http
GET /devices/{device_id}/data
Authorization: Bearer <TOKEN>
```

**쿼리 파라미터:**
- `start_time`: ISO 8601 형식 시작 시간
- `end_time`: ISO 8601 형식 종료 시간
- `limit`: 최대 레코드 수 (기본값: 100)
- `fields`: 조회할 필드 (온도, 습도 등)

#### 디바이스 제어
```http
POST /devices/{device_id}/control
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "command": "set_temperature",
  "parameters": {
    "target_temperature": 24,
    "mode": "auto"
  }
}
```

### 자동화 규칙

#### 자동화 규칙 생성
```http
POST /automation/rules
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "name": "온도 제어 자동화",
  "description": "온도가 30도 초과 시 에어컨 가동",
  "trigger": {
    "device_id": "temp_sensor_01",
    "condition": "temperature > 30",
    "duration": "5m"
  },
  "actions": [
    {
      "device_id": "aircon_01",
      "command": "power_on",
      "parameters": {"temperature": 24}
    },
    {
      "type": "notification",
      "message": "높은 온도 감지로 에어컨을 가동했습니다."
    }
  ]
}
```

---

## 보안 모니터링 API (포트 8007)

### 보안 상태

#### 전체 보안 상태 조회
```http
GET /security/status
Authorization: Bearer <TOKEN>
```

**응답:**
```json
{
  "status": "success",
  "data": {
    "threat_level": "low",
    "active_threats": 0,
    "events_last_24h": 47,
    "blocked_attacks": 12,
    "security_alerts": 3,
    "last_scan": "2024-01-19T09:45:00Z",
    "system_health": "healthy"
  }
}
```

### 보안 이벤트

#### 보안 이벤트 조회
```http
GET /security/events
Authorization: Bearer <TOKEN>
```

**쿼리 파라미터:**
- `limit`: 결과 수 제한 (1-1000, 기본값: 100)
- `threat_type`: sql_injection, xss, path_traversal, brute_force
- `severity`: critical, high, medium, low
- `start_time`: 시작 시간 (ISO 8601)
- `end_time`: 종료 시간 (ISO 8601)
- `source_ip`: 소스 IP 주소

**응답:**
```json
{
  "status": "success",
  "data": {
    "events": [
      {
        "id": "evt_001",
        "timestamp": "2024-01-19T10:23:45Z",
        "threat_type": "sql_injection",
        "severity": "high",
        "source_ip": "192.168.1.100",
        "target": "/api/users",
        "payload": "' OR '1'='1' --",
        "user_agent": "curl/7.68.0",
        "blocked": true,
        "score": 85
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 100
  }
}
```

#### 보안 이벤트 등록
```http
POST /security/events
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "event_type": "suspicious_login",
  "source_ip": "203.0.113.1",
  "target": "/auth/login",
  "payload": "multiple_failed_attempts",
  "user_agent": "Mozilla/5.0...",
  "additional_data": {
    "username": "admin",
    "attempts": 5
  }
}
```

### 보안 감사

#### 보안 감사 실행
```http
POST /security/audit
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "scope": ["system", "network", "application"],
  "immediate": true
}
```

**응답:**
```json
{
  "status": "success",
  "data": {
    "audit_id": "audit_001",
    "status": "running",
    "estimated_completion": "2024-01-19T10:35:00Z",
    "scope": ["system", "network", "application"]
  }
}
```

#### 감사 결과 조회
```http
GET /security/audit/{audit_id}
Authorization: Bearer <TOKEN>
```

### IP 관리

#### IP 블랙리스트 조회
```http
GET /security/blacklist
Authorization: Bearer <TOKEN>
```

#### IP 블랙리스트 추가
```http
POST /security/blacklist
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "ip_address": "203.0.113.1",
  "reason": "Multiple failed login attempts",
  "duration": 86400,
  "auto_added": false
}
```

---

## 성능 모니터링 API

### 성능 메트릭

#### 실시간 성능 데이터 조회
```http
GET /performance/metrics/realtime
Authorization: Bearer <TOKEN>
```

**응답:**
```json
{
  "status": "success",
  "data": {
    "timestamp": "2024-01-19T10:30:00Z",
    "system_metrics": {
      "cpu_percent": 78.5,
      "memory_percent": 65.2,
      "disk_usage_percent": 45.0,
      "network_io": {
        "bytes_sent": 1024000,
        "bytes_recv": 2048000
      }
    },
    "application_metrics": {
      "response_time_ms": 95,
      "throughput_rpm": 1234,
      "error_rate": 0.1,
      "active_connections": 145,
      "queue_size": 12
    }
  }
}
```

### 성능 최적화

#### 최적화 규칙 조회
```http
GET /performance/optimization/rules
Authorization: Bearer <TOKEN>
```

#### 수동 최적화 실행
```http
POST /performance/optimization/execute
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "rule_name": "memory_cleanup",
  "force": false
}
```

---

## 에러 코드 및 응답

### HTTP 상태 코드

| 코드 | 의미 | 설명 |
|------|------|------|
| 200 | OK | 요청 성공 |
| 201 | Created | 리소스 생성 성공 |
| 400 | Bad Request | 잘못된 요청 형식 |
| 401 | Unauthorized | 인증 실패 |
| 403 | Forbidden | 권한 없음 |
| 404 | Not Found | 리소스를 찾을 수 없음 |
| 429 | Too Many Requests | 요청 제한 초과 |
| 500 | Internal Server Error | 서버 내부 오류 |
| 503 | Service Unavailable | 서비스 일시 불가 |

### 에러 응답 형식

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_REQUEST",
    "message": "잘못된 요청 형식입니다.",
    "details": {
      "field": "email",
      "issue": "이메일 형식이 올바르지 않습니다."
    }
  },
  "timestamp": "2024-01-19T10:30:00Z",
  "request_id": "req_123456"
}
```

### 주요 에러 코드

```
AUTHENTICATION_FAILED: 인증 실패
INVALID_TOKEN: 토큰이 유효하지 않음
PERMISSION_DENIED: 권한 없음
RATE_LIMIT_EXCEEDED: 요청 제한 초과
RESOURCE_NOT_FOUND: 리소스를 찾을 수 없음
VALIDATION_ERROR: 입력 데이터 검증 실패
SERVICE_UNAVAILABLE: 서비스 일시 불가
INTERNAL_ERROR: 서버 내부 오류
```

---

## SDK 및 클라이언트 라이브러리

### Python SDK

#### 설치
```bash
pip install your-program-sdk
```

#### 기본 사용법
```python
from your_program import YourProgramClient

# 클라이언트 초기화
client = YourProgramClient(
    base_url="https://api.yourprogram.com",
    api_key="your-api-key"
)

# 시스템 상태 확인
status = client.health.get_status()
print(f"시스템 상태: {status.overall_status}")

# AI 모델 예측
prediction = client.ai.predict(
    model_id="model_001",
    features={
        "age": 25,
        "income": 50000
    }
)
print(f"예측 결과: {prediction.churn_probability}")

# 보안 이벤트 조회
events = client.security.get_events(
    limit=10,
    severity="high"
)
for event in events:
    print(f"위협 유형: {event.threat_type}, IP: {event.source_ip}")
```

### JavaScript SDK

#### 설치
```bash
npm install @your-program/sdk
```

#### 기본 사용법
```javascript
import { YourProgramClient } from '@your-program/sdk';

// 클라이언트 초기화
const client = new YourProgramClient({
  baseUrl: 'https://api.yourprogram.com',
  apiKey: 'your-api-key'
});

// 시스템 상태 확인
const status = await client.health.getStatus();
console.log(`시스템 상태: ${status.overall_status}`);

// 실시간 메트릭 구독
client.metrics.subscribe('realtime', (data) => {
  console.log(`CPU: ${data.cpu_percent}%, 메모리: ${data.memory_percent}%`);
});

// 대시보드 생성
const dashboard = await client.analytics.createDashboard({
  name: '매출 분석',
  template: 'sales_analysis'
});
```

### cURL 예제

#### 인증 토큰 발급
```bash
curl -X POST https://api.yourprogram.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "password123"
  }'
```

#### API 호출 (토큰 사용)
```bash
curl -X GET https://api.yourprogram.com/health \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json"
```

---

## 예제 및 튜토리얼

### 1. 기본 모니터링 대시보드 구축

#### 단계 1: 인증
```python
import requests

# 토큰 발급
auth_response = requests.post('https://api.yourprogram.com/auth/login', {
    'username': 'admin@company.com',
    'password': 'secure_password'
})
token = auth_response.json()['data']['access_token']

headers = {'Authorization': f'Bearer {token}'}
```

#### 단계 2: 시스템 메트릭 조회
```python
# 실시간 메트릭 조회
metrics = requests.get(
    'https://api.yourprogram.com/metrics',
    headers=headers,
    params={
        'interval': '5m',
        'metrics': 'cpu,memory,network'
    }
).json()

print(f"CPU 사용률: {metrics['data']['metrics']['cpu_usage'][-1]['value']}%")
```

#### 단계 3: 대시보드 생성
```python
# 새 대시보드 생성
dashboard = requests.post(
    'https://api.yourprogram.com/dashboards',
    headers=headers,
    json={
        'name': '실시간 시스템 모니터링',
        'description': 'CPU, 메모리, 네트워크 실시간 모니터링',
        'template': 'system_monitoring'
    }
).json()

dashboard_id = dashboard['data']['id']
print(f"대시보드 생성 완료: {dashboard_id}")
```

### 2. AI 모델 훈련 및 배포

#### 단계 1: 데이터 준비
```python
# 훈련 데이터 업로드
files = {'file': open('customer_data.csv', 'rb')}
upload_response = requests.post(
    'https://api.yourprogram.com/data/upload',
    headers=headers,
    files=files
)
dataset_id = upload_response.json()['data']['dataset_id']
```

#### 단계 2: 모델 훈련
```python
# 모델 훈련 시작
training_job = requests.post(
    'https://api.yourprogram.com/models/train',
    headers=headers,
    json={
        'name': '고객 이탈 예측 모델',
        'algorithm': 'random_forest',
        'dataset_id': dataset_id,
        'hyperparameters': {
            'n_estimators': 100,
            'max_depth': 10
        }
    }
).json()

job_id = training_job['data']['job_id']
print(f"훈련 작업 시작: {job_id}")
```

#### 단계 3: 모델 배포
```python
# 훈련 완료 후 모델 배포
deploy_response = requests.post(
    f'https://api.yourprogram.com/models/{model_id}/deploy',
    headers=headers,
    json={
        'environment': 'production',
        'instances': 3,
        'auto_scaling': True
    }
)

if deploy_response.status_code == 200:
    print("모델 배포 완료")
```

### 3. 보안 모니터링 설정

#### 단계 1: 알림 설정
```python
# 보안 알림 설정
alert_config = requests.put(
    'https://api.yourprogram.com/security/alerts/config',
    headers=headers,
    json={
        'threat_levels': {
            'critical': 'immediate',
            'high': '5_minutes',
            'medium': '1_hour'
        },
        'notification_channels': {
            'email': 'security@company.com',
            'slack': '#security-alerts'
        }
    }
)
```

#### 단계 2: IP 화이트리스트 관리
```python
# 신뢰할 수 있는 IP 추가
whitelist_response = requests.post(
    'https://api.yourprogram.com/security/whitelist',
    headers=headers,
    json={
        'ip_addresses': [
            '192.168.1.0/24',  # 내부 네트워크
            '203.0.113.10'     # 파트너 사무실
        ],
        'description': '내부 및 파트너 네트워크'
    }
)
```

### 4. IoT 디바이스 자동화

#### 단계 1: 디바이스 등록
```python
# 새 센서 등록
device_response = requests.post(
    'https://api.yourprogram.com/devices',
    headers=headers,
    json={
        'name': '회의실 온도센서',
        'type': 'sensor',
        'location': '본사 5층 회의실 A',
        'connection': {
            'protocol': 'mqtt',
            'topic': 'sensors/meeting_room_a/temperature'
        }
    }
)

device_id = device_response.json()['data']['device_id']
```

#### 단계 2: 자동화 규칙 생성
```python
# 온도 제어 자동화 규칙 생성
automation_rule = requests.post(
    'https://api.yourprogram.com/automation/rules',
    headers=headers,
    json={
        'name': '회의실 온도 자동 제어',
        'trigger': {
            'device_id': device_id,
            'condition': 'temperature > 26 OR temperature < 20',
            'duration': '3m'
        },
        'actions': [
            {
                'device_id': 'aircon_meeting_room_a',
                'command': 'adjust_temperature',
                'parameters': {'target': 23}
            }
        ]
    }
)
```

---

**이 API 참조 문서는 Your Program 플랫폼의 모든 기능에 대한 개발자 가이드입니다. 추가 질문이나 지원이 필요한 경우 개발팀에 문의해 주세요.**

**문서 버전**: 1.0.0  
**최종 업데이트**: 2024년 1월 19일  
**지원 이메일**: api-support@yourcompany.com  
**개발자 포털**: https://developers.yourprogram.com 