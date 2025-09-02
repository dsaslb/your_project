# 실시간 시스템 구현 가이드

## 개요

이 문서는 단일 진실(SOT) 원칙과 실시간 이벤트 시스템을 구현한 내용을 설명합니다.

## 시스템 아키텍처

### 1. 단일 진실(SOT) 원칙

- **데이터베이스가 진실**: 모든 데이터 변경은 DB에 먼저 저장
- **모바일은 REST API**: 모바일 앱은 REST API를 통해 데이터 쓰기
- **웹은 이벤트 수신**: 웹 프론트엔드는 Socket.IO 이벤트로 UI 갱신

### 2. 실시간 이벤트 흐름

```
모바일 앱 → REST API → DB 저장 → Socket.IO 이벤트 → 웹 프론트엔드
```

## 구현된 기능

### 백엔드 (Flask)

#### 1. 이벤트 헬퍼 (`utils/events.py`)

```python
from utils.events import emit_event, emit_branch_event

# 표준 이벤트 송출
emit_event("po:created", {
    "id": po.id,
    "branch_id": po.branch_id,
    "brand_id": po.brand_id,
    "industry_id": po.industry_id,
    "status": po.status
}, room=f"branch:{po.branch_id}")
```

**주요 특징:**
- 모든 이벤트에 `industry_id`, `brand_id`, `branch_id` 포함
- 서버 타임스탬프 자동 추가
- 버전 관리 (`v` 필드)
- 룸 기반 브로드캐스팅

#### 2. 멱등성 처리 (`utils/idempotency.py`)

```python
from utils.idempotency import require_idempotency_key

@app.route('/api/mobile/purchase_orders', methods=['POST'])
@require_idempotency_key()
def create_purchase_order():
    # 중복 요청 자동 방지
    pass
```

**주요 특징:**
- UUID 기반 멱등성 키 검증
- 중복 요청 시 즉시 성공 응답
- 오프라인 재전송 안전성 보장
- 자동 만료 키 정리 (24시간)

#### 3. 모바일 발주 API (`api/mobile/purchase_orders.py`)

**엔드포인트:**
- `POST /api/mobile/purchase_orders` - 발주 생성
- `GET /api/mobile/purchase_orders` - 발주 목록
- `GET /api/mobile/purchase_orders/<id>` - 발주 상세

**요청 형식:**
```json
{
  "branch_id": 123,
  "items": [
    {"barcode": "123456789", "name": "상품명", "qty": 5}
  ],
  "notes": "비고사항"
}
```

**헤더:**
```
X-Idempotency-Key: <uuid>
```

#### 4. 관리자 발주 API (`api/admin/purchase_orders.py`)

**엔드포인트:**
- `PUT /api/admin/purchase_orders/<id>/status` - 상태 변경
- `GET /api/admin/purchase_orders` - 발주 목록
- `GET /api/admin/purchase_orders/count` - 카운트 조회

**상태 변경 요청:**
```json
{
  "status": "approved|rejected|processing|completed",
  "notes": "상태 변경 사유"
}
```

### 프론트엔드 (Next.js/React)

#### 1. 소켓 클라이언트 (`src/lib/socket.ts`)

```typescript
import { getSocket, joinRoom, leaveRoom } from '@/lib/socket';

// 지점별 룸 조인
joinRoom(`branch:${branchId}`);
```

**주요 기능:**
- 자동 재연결
- 룸 기반 이벤트 구독
- 연결 상태 모니터링

#### 2. 배지 관리 훅 (`src/store/useBadges.ts`)

```typescript
const { badges, isConnected } = useBadges(branchId, brandId);

// 실시간 배지 업데이트
// 2초 후 백그라운드 재조회로 값 보정
```

**주요 특징:**
- 실시간 이벤트 구독
- 자동 백그라운드 재조회
- 배지 값 실시간 반영
- 정기적인 데이터 갱신 (5분마다)

#### 3. 사이드바 컴포넌트 (`src/components/Sidebar.tsx`)

```typescript
// 실시간 배지 표시
<span className="bg-orange-500 text-white text-xs px-2 py-1 rounded-full">
  {badges.poRequested}
</span>
```

**배지 색상:**
- 🟠 주황: 대기중 (requested)
- 🔵 파랑: 처리중 (processing)
- 🟢 초록: 완료 (completed)
- 🟣 보라: 업데이트 알림

### 모바일 앱 (Expo/React Native)

#### 1. 안전한 POST 유틸리티 (`src/utils/safePost.ts`)

```typescript
import { safePost, flushQueue } from '../utils/safePost';

// 안전한 발주 생성
await safePost(apiClient, '/api/mobile/purchase_orders', orderData);
```

**주요 기능:**
- 자동 멱등성 키 생성
- 오프라인 시 AsyncStorage 큐 저장
- 네트워크 복구 시 자동 재전송
- 재시도 횟수 제한 (최대 3회)
- 24시간 이내 작업만 유지

#### 2. 발주 생성 화면 (`src/screens/PurchaseOrder.tsx`)

**주요 기능:**
- 상품 선택 및 수량 조정
- 오프라인 큐 상태 표시
- 큐 수동 처리 버튼
- 실시간 폼 검증

## 이벤트 네이밍 규칙

### 표준 이벤트

| 도메인 | 이벤트명 | 설명 | Payload 예시 |
|--------|----------|------|--------------|
| 발주 | `po:created` | 발주 생성 | `{id, branch_id, status, user_id}` |
| 발주 | `po:status` | 상태 변경 | `{id, old_status, new_status, branch_id}` |
| 출퇴근 | `attendance:update` | 출퇴근 기록 | `{user_id, branch_id, type, timestamp}` |
| 재고 | `inventory:update` | 재고 변경 | `{product_id, branch_id, old_qty, new_qty}` |
| 스케줄 | `schedule:update` | 스케줄 변경 | `{schedule_id, branch_id, changes}` |
| 주문 | `order:update` | 주문 상태 변경 | `{order_id, branch_id, status}` |

### 이벤트 Payload 구조

```json
{
  "v": 1,
  "ts": "2024-01-01T12:00:00Z",
  "id": 123,
  "branch_id": 456,
  "brand_id": 789,
  "industry_id": 101,
  "status": "requested",
  "user_id": 999
}
```

## 권한 스코프

### 필수 필드

모든 이벤트 payload에는 다음 필드가 반드시 포함되어야 합니다:

- `industry_id`: 업종 ID
- `brand_id`: 브랜드 ID  
- `branch_id`: 지점 ID

### 룸 기반 접근 제어

```typescript
// 지점별 룸
joinRoom(`branch:${branchId}`);

// 브랜드별 룸
joinRoom(`brand:${brandId}`);

// 업종별 룸
joinRoom(`industry:${industryId}`);
```

## 오프라인 처리

### 모바일 앱

1. **네트워크 실패 시**: 요청을 AsyncStorage 큐에 저장
2. **재연결 시**: `flushQueue()` 자동 실행
3. **수동 처리**: 사용자가 "큐 처리하기" 버튼 클릭

### 큐 관리

- **저장소**: AsyncStorage (React Native)
- **만료**: 24시간 이내 작업만 유지
- **재시도**: 최대 3회
- **우선순위**: FIFO (선입선출)

## 성능 최적화

### 1. 배지 업데이트 전략

- **즉시 반영**: 이벤트 수신 시 즉시 배지 값 변경
- **백그라운드 보정**: 2초 후 API 재조회로 값 정확성 확보
- **정기 갱신**: 5분마다 전체 배지 데이터 갱신

### 2. 이벤트 필터링

```typescript
// 지점별 이벤트만 처리
if (data.branch_id === branchId) {
  // 이벤트 처리
}
```

### 3. 메모리 관리

- 컴포넌트 언마운트 시 이벤트 리스너 자동 제거
- 룸 자동 해제
- 인터벌 타이머 정리

## 보안 고려사항

### 1. 멱등성 키

- UUID v4 형식 검증
- 사용자별 키 추적
- IP 주소 기록
- 자동 만료 (24시간)

### 2. 권한 검증

- 모든 API 엔드포인트에 인증 데코레이터 적용
- 브랜드/지점 스코프 검증
- 사용자 역할 기반 접근 제어

### 3. 이벤트 스코프

- 룸 기반 이벤트 송출
- 권한이 있는 사용자만 해당 룸 조인
- 크로스 브랜드 데이터 접근 방지

## 모니터링 및 로깅

### 1. 이벤트 로깅

```python
logger.info(f"발주 생성 완료: ID {po.id}, 사용자 {user_id}, 지점 {branch_id}")
logger.info(f"발주 상태 변경: ID {po_id}, {old_status} → {new_status}")
```

### 2. 소켓 연결 상태

```typescript
console.log("🔌 웹소켓 연결됨:", socket?.id);
console.log("🔌 웹소켓 연결 해제:", reason);
```

### 3. 오프라인 큐 상태

```typescript
console.log(`📥 오프라인 큐에 작업 추가: ${url} (총 ${queue.length}개)`);
console.log(`✅ 오프라인 큐 처리 완료: ${processedCount}개 성공, ${remaining.length}개 남음`);
```

## 배포 및 설정

### 1. 환경변수

**프론트엔드:**
```bash
# .env.local
NEXT_PUBLIC_WS_URL=ws://localhost:5000
NEXT_PUBLIC_API_URL=http://localhost:5000
```

**백엔드:**
```bash
# .env
FLASK_ENV=production
JWT_SECRET_KEY=your-secret-key
```

### 2. 데이터베이스 마이그레이션

```bash
# IdempotencyKey 테이블 생성
flask db upgrade
```

### 3. 의존성 설치

**프론트엔드:**
```bash
npm install socket.io-client
```

**모바일 앱:**
```bash
npm install @react-native-async-storage/async-storage uuid
```

## 테스트

### 1. API 테스트

```bash
# 발주 생성 (멱등성 키 포함)
curl -X POST http://localhost:5000/api/mobile/purchase_orders \
  -H "Content-Type: application/json" \
  -H "X-Idempotency-Key: $(uuidgen)" \
  -d '{"branch_id": 1, "items": [{"barcode": "123", "name": "테스트", "qty": 1}]}'
```

### 2. 웹소켓 테스트

```javascript
// 브라우저 콘솔에서
const socket = io('ws://localhost:5000');
socket.on('po:created', (data) => console.log('발주 생성:', data));
```

### 3. 오프라인 테스트

1. 모바일 앱에서 발주 생성
2. 네트워크 연결 해제
3. 발주 재시도 (큐에 저장됨)
4. 네트워크 복구
5. 큐 자동 처리 확인

## 문제 해결

### 1. 웹소켓 연결 실패

- 방화벽 설정 확인
- CORS 설정 확인
- 포트 번호 확인

### 2. 이벤트 수신 안됨

- 룸 조인 상태 확인
- 브랜치 ID 일치 여부 확인
- 소켓 연결 상태 확인

### 3. 멱등성 키 오류

- UUID 형식 검증
- 데이터베이스 연결 확인
- 테이블 스키마 확인

## 향후 개선 사항

### 1. 고급 기능

- 이벤트 히스토리 저장
- 실시간 알림 시스템
- 웹푸시 알림
- 오프라인 동기화 개선

### 2. 성능 최적화

- 이벤트 배치 처리
- 메모리 캐싱
- 데이터베이스 인덱싱
- 로드 밸런싱

### 3. 모니터링 강화

- 실시간 대시보드
- 성능 메트릭
- 오류 추적
- 사용자 행동 분석

## 결론

이 구현을 통해 다음과 같은 이점을 얻을 수 있습니다:

1. **실시간성**: 즉시 UI 업데이트로 사용자 경험 향상
2. **안정성**: 멱등성 키로 중복 요청 방지
3. **오프라인 지원**: 네트워크 불안정 상황에서도 안전한 데이터 전송
4. **확장성**: 룸 기반 이벤트로 효율적인 리소스 관리
5. **일관성**: 단일 진실 원칙으로 데이터 무결성 보장

이 시스템은 현대적인 웹/모바일 애플리케이션에서 요구되는 실시간성과 안정성을 모두 제공합니다.

