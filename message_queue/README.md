# 메시지 큐 시스템

메시지 큐는 비동기 작업 처리, 이벤트 관리, Pub/Sub, 마이크로서비스 통신을 위한 핵심 컴포넌트입니다.

## 주요 기능

- 큐 생성/삭제/조회
- 메시지 발행/소비/완료
- 우선순위 큐, 데드 레터 큐, 이벤트 스트림 지원
- 구독(Pub/Sub) 관리
- 메시지 TTL, 재시도, 만료, 데드레터 처리
- 실시간 큐 통계 및 모니터링
- SQLite 기반 데이터 영속성

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 설정
```bash
# .env 예시
MESSAGE_QUEUE_DATA_DIR=data/message_queue
```

### 3. 데이터 디렉토리 생성
```bash
mkdir -p data/message_queue
```

## 사용법 예시

### 1. 큐 생성
```python
from message_queue.queue_manager import QueueManager, QueueConfig, QueueType
config = QueueConfig(data_dir="data/message_queue")
manager = QueueManager(config)
queue_id = manager.create_queue("작업 큐", QueueType.STANDARD)
```

### 2. 메시지 발행
```python
msg_id = manager.publish_message(queue_id, topic="task", payload={"job": "send_email"})
```

### 3. 메시지 소비
```python
msg = manager.consume_message(queue_id)
if msg:
    # 작업 처리 후
    manager.complete_message(msg.message_id, success=True)
```

### 4. 구독 등록
```python
sub_id = manager.subscribe(queue_id, topic="task")
```

## REST API 엔드포인트

- `GET /api/message-queue/health` : 시스템 상태 확인
- `GET /api/message-queue/stats` : 큐 통계 조회
- `GET /api/message-queue/queues` : 큐 목록 조회
- `POST /api/message-queue/queues` : 큐 생성
- `DELETE /api/message-queue/queues/<queue_id>` : 큐 삭제
- `POST /api/message-queue/messages` : 메시지 발행
- `POST /api/message-queue/messages/consume` : 메시지 소비
- `POST /api/message-queue/messages/<message_id>/complete` : 메시지 완료 처리
- `POST /api/message-queue/subscriptions` : 구독 등록
- `POST /api/message-queue/subscriptions/<subscription_id>/cancel` : 구독 해제

## 데이터베이스 스키마

- **queues**: 큐 정보
- **messages**: 메시지 정보
- **subscriptions**: 구독 정보

## 큐 타입
- `standard`: 일반 큐
- `priority`: 우선순위 큐
- `dead_letter`: 데드 레터 큐
- `event_stream`: 이벤트 스트림

## 확장 기능
- 메시지 암호화/복호화
- 배치 처리, 예약 메시지
- 모니터링/알림 연동
- 대용량 분산 큐(추후 확장)

## 문제 해결
- 큐가 가득 찼을 때: max_size 조정 필요
- 메시지 TTL 만료: 자동 삭제됨
- 데드레터 큐: 재시도 초과 메시지 자동 이동

## 라이선스
MIT