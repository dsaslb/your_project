# API 명세 (API Reference)

---

## 인증/보안

| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| /api/auth/login | POST | 로그인 (JWT/OAuth2) |
| /api/auth/logout | POST | 로그아웃 |
| /api/auth/refresh | POST | 토큰 갱신 |
| /api/auth/2fa/setup | POST | 2FA 설정 |

---

## 브랜드/지점/직원 관리

| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| /api/admin/brands | GET/POST | 브랜드 목록/생성 |
| /api/admin/brands/<id> | GET/PUT/DELETE | 브랜드 상세/수정/삭제 |
| /api/admin/branches | GET/POST | 지점 목록/생성 |
| /api/admin/branches/<id> | GET/PUT/DELETE | 지점 상세/수정/삭제 |
| /api/admin/employees | GET/POST | 직원 목록/생성 |
| /api/admin/employees/<id> | GET/PUT/DELETE | 직원 상세/수정/삭제 |

---

## 플러그인 마켓/설치/관리

| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| /api/admin/plugins/market | GET | 마켓 플러그인 목록/검색 |
| /api/admin/plugins/installed | GET | 설치된 플러그인 목록 |
| /api/admin/plugins/install | POST | 플러그인 설치 |
| /api/admin/plugins/update | POST | 플러그인 업데이트 |
| /api/admin/plugins/uninstall | POST | 플러그인 삭제 |

---

## 결제/매출

| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| /api/admin/payments/checkout | POST | Stripe 결제 생성 |
| /api/admin/payments/history | GET | 결제 내역 조회 |
| /api/admin/payments/webhook | POST | Stripe Webhook 처리 |

---

## 통계/리포트

| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| /api/admin/stats/summary | GET | 주요 통계 요약 |
| /api/admin/stats/timeseries | GET | 기간별 시계열 통계 |
| /api/admin/stats/plugin | GET | 플러그인별 통계 |

---

## 알림/마케팅

| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| /api/admin/notifications/send | POST | 알림(이메일/SMS/푸시) 발송 |
| /api/admin/notifications/history | GET | 알림 발송 내역 조회 |

---

## 운영/모니터링/자동화

| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| /api/admin/ops/status | GET | 전체 서비스/컨테이너 상태 |
| /api/admin/ops/logs | GET | 장애/복구 로그 |
| /api/admin/ops/alerts | GET | 장애 알림 |

---

## AI/성능 최적화

| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| /api/ai/performance/predict | GET | 미래 부하/리소스 예측 |
| /api/ai/performance/anomaly | GET | 실시간 이상 탐지 |
| /api/ai/performance/auto-optimize | POST | AI 기반 자동 최적화 |

---

## 예시 요청/응답

### 브랜드 생성
```http
POST /api/admin/brands
Content-Type: application/json

{
  "name": "새 브랜드",
  "description": "설명"
}
```

### 결제 생성
```http
POST /api/admin/payments/checkout
Content-Type: application/json

{
  "amount": 100,
  "description": "서비스 결제"
}
```

### 알림 발송
```http
POST /api/admin/notifications/send
Content-Type: application/json

{
  "type": "email",
  "to": "user@example.com",
  "subject": "테스트 알림",
  "message": "안녕하세요!"
}
``` 