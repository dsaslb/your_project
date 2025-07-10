# 🏗️ 레스토랑 관리 시스템 마이크로서비스 아키텍처

## 📋 개요

레스토랑 관리 시스템을 마이크로서비스 아키텍처로 전환하여 확장성, 유지보수성, 성능을 향상시켰습니다.

## 🏛️ 아키텍처 구조

```
┌─────────────────┐
│   API Gateway   │ ← 모든 요청의 진입점
│   (Port: 5000)  │
└─────────────────┘
         │
         ├─── User Service (5001) - 사용자 관리, 인증
         ├─── Staff Service (5002) - 직원 관리, 근태
         ├─── Inventory Service (5003) - 재고 관리
         ├─── Order Service (5004) - 주문 관리
         ├─── Analytics Service (5005) - 데이터 분석
         ├─── IoT Service (5006) - IoT 기기 관리
         ├─── Notification Service (5007) - 알림 관리
         └─── AI Service (5008) - AI 예측, 분석
```

## 🚀 서비스별 상세 정보

### 1. API Gateway Service (Port: 5000)
- **역할**: 모든 요청의 진입점, 라우팅, 로드 밸런싱
- **기능**: 
  - 요청 라우팅
  - 인증 토큰 검증
  - 로깅 및 모니터링
  - 서비스 상태 확인
- **기술**: Flask, requests

### 2. User Service (Port: 5001)
- **역할**: 사용자 관리, 인증, 권한 관리
- **기능**:
  - 사용자 등록/수정/삭제
  - 로그인/로그아웃
  - JWT 토큰 관리
  - 권한 검증
- **기술**: Flask, JWT, SQLite

### 3. IoT Service (Port: 5006)
- **역할**: IoT 기기 관리, 데이터 수집, 제어
- **기능**:
  - IoT 기기 상태 모니터링
  - 실시간 데이터 수집
  - 기기 제어
  - 알림 생성
- **기술**: Flask, threading, SQLite

### 4. Staff Service (Port: 5002)
- **역할**: 직원 관리, 근태 관리, 스케줄링
- **기능**:
  - 직원 정보 관리
  - 출퇴근 기록
  - 근무 스케줄 관리
  - 급여 계산
- **기술**: Flask, SQLite

### 5. Inventory Service (Port: 5003)
- **역할**: 재고 관리, 발주 관리
- **기능**:
  - 재고 현황 관리
  - 자동 발주
  - 재고 알림
  - 공급업체 관리
- **기술**: Flask, SQLite

### 6. Order Service (Port: 5004)
- **역할**: 주문 관리, 결제 처리
- **기능**:
  - 주문 생성/수정/취소
  - 결제 처리
  - 주문 상태 추적
  - 매출 통계
- **기술**: Flask, SQLite

### 7. Analytics Service (Port: 5005)
- **역할**: 데이터 분석, 리포트 생성
- **기능**:
  - 매출 분석
  - 고객 분석
  - 성과 분석
  - 리포트 생성
- **기술**: Flask, pandas, SQLite

### 8. Notification Service (Port: 5007)
- **역할**: 알림 관리, 웹소켓 통신
- **기능**:
  - 실시간 알림
  - 이메일/SMS 발송
  - 웹소켓 연결 관리
  - 알림 설정
- **기술**: Flask, WebSocket, SQLite

### 9. AI Service (Port: 5008)
- **역할**: AI 예측, 머신러닝
- **기능**:
  - 매출 예측
  - 재고 예측
  - 고객 행동 분석
  - 최적화 제안
- **기술**: Flask, TensorFlow, SQLite

## 🛠️ 인프라 구성

### 데이터베이스
- **PostgreSQL**: 메인 데이터베이스 (Port: 5432)
- **Redis**: 캐싱 및 세션 저장 (Port: 6379)
- **SQLite**: 각 서비스별 로컬 데이터베이스

### 네트워크
- **Docker Network**: microservices-network
- **서비스 간 통신**: HTTP REST API
- **외부 접근**: API Gateway를 통한 단일 진입점

## 🚀 실행 방법

### 1. Docker Compose로 실행
```bash
cd microservices
docker-compose up --build -d
```

### 2. 개별 서비스 실행
```bash
# API Gateway
cd gateway-service
python app.py

# User Service
cd user-service
python app.py

# IoT Service
cd iot-service
python app.py
```

### 3. Windows 배치 파일 실행
```bash
start-microservices.bat
```

## 📊 모니터링

### 서비스 상태 확인
```bash
# 모든 서비스 상태
docker-compose ps

# 특정 서비스 로그
docker-compose logs -f gateway
docker-compose logs -f user
docker-compose logs -f iot
```

### 헬스 체크
- API Gateway: http://localhost:5000/health
- User Service: http://localhost:5001/health
- IoT Service: http://localhost:5006/health
- 모든 서비스: http://localhost:5000/api/services/status

## 🔧 개발 가이드

### 새로운 서비스 추가
1. `microservices/` 디렉토리에 새 서비스 폴더 생성
2. `app.py`, `requirements.txt`, `Dockerfile` 생성
3. `docker-compose.yml`에 서비스 추가
4. API Gateway의 라우팅 규칙 추가

### API 테스트
```bash
# 사용자 로그인
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# IoT 기기 상태 조회
curl http://localhost:5000/api/iot/devices

# 서비스 상태 확인
curl http://localhost:5000/api/services/status
```

## 🔒 보안

### 인증
- JWT 토큰 기반 인증
- 토큰 만료 시간: 24시간
- 세션 관리

### 권한 관리
- 역할 기반 접근 제어 (RBAC)
- 서비스별 권한 검증
- API Gateway에서 토큰 검증

## 📈 성능 최적화

### 캐싱
- Redis를 통한 세션 및 데이터 캐싱
- API 응답 캐싱

### 로드 밸런싱
- API Gateway에서 요청 분산
- 서비스별 독립적 스케일링

### 데이터베이스 최적화
- 서비스별 데이터베이스 분리
- 인덱스 최적화
- 쿼리 최적화

## 🔄 CI/CD 파이프라인

### 빌드 프로세스
1. 코드 변경 감지
2. 자동 테스트 실행
3. Docker 이미지 빌드
4. 컨테이너 배포
5. 헬스 체크

### 배포 전략
- Blue-Green 배포
- 롤링 업데이트
- 무중단 배포

## 📝 로깅 및 모니터링

### 로깅
- 구조화된 로그 (JSON 형식)
- 서비스별 로그 수집
- 중앙 집중식 로그 관리

### 모니터링
- 서비스 헬스 체크
- 성능 메트릭 수집
- 알림 시스템

## 🚀 다음 단계

### Phase 10-2: Kubernetes 배포
- Kubernetes 클러스터 구성
- Helm 차트 생성
- 자동 스케일링 설정

### Phase 10-3: 고급 모니터링
- Prometheus + Grafana 설정
- 분산 추적 (Jaeger)
- 로그 집계 (ELK Stack)

### Phase 10-4: 보안 강화
- mTLS 설정
- API Rate Limiting
- 보안 스캔 자동화

---

## 📞 지원

문제가 발생하거나 질문이 있으시면 개발팀에 문의해주세요. 