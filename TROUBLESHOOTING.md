# 🔧 문제 해결 가이드

## 모바일 앱 오류 해결

### 1. Socket.IO 연결 오류

#### 문제
```
WebSocket connection to 'ws://192.168.45.44:5000/socket.io/?EIO=4&transport=websocket' failed
```

#### 해결 방법
1. **서버가 실행 중인지 확인**
   ```bash
   python start_server.py
   ```

2. **IP 주소 확인**
   - `mobile_app/src/api/socket.ts`에서 `WS_URL` 수정
   - `localhost` 또는 실제 서버 IP 사용

3. **방화벽 확인**
   - 포트 5000이 열려있는지 확인
   - Windows Defender 방화벽 설정 확인

### 2. API 연결 오류

#### 문제
```
Failed to load resource: net::ERR_CONNECTION_REFUSED
```

#### 해결 방법
1. **서버 상태 확인**
   ```bash
   curl http://localhost:5000/healthz
   ```

2. **API URL 설정 확인**
   - `mobile_app/src/api/client.ts`에서 `BASE_URL` 수정
   - 네트워크 연결 상태 확인

### 3. React Native Web 경고

#### 문제
```
"shadow*" style props are deprecated. Use "boxShadow"
props.pointerEvents is deprecated. Use style.pointerEvents
```

#### 해결 방법
- ✅ **해결됨**: `shadow*` props를 `boxShadow`로 변경
- ✅ **해결됨**: `pointerEvents` props를 `style.pointerEvents`로 변경

### 4. 함수 import 오류

#### 문제
```
(0 , _socket.subscribeToAttendanceUpdates) is not a function
```

#### 해결 방법
- ✅ **해결됨**: `socket.ts`에서 개별 함수들 export 추가
- ✅ **해결됨**: Dashboard.tsx에서 에러 처리 추가

### 5. 대시보드 데이터 로드 실패

#### 문제
```
GET http://192.168.45.44:5000/api/mobile/dashboard net::ERR_CONNECTION_REFUSED
```

#### 해결 방법
- ✅ **해결됨**: API 클라이언트에서 서버 연결 실패 시 기본 데이터 반환
- ✅ **해결됨**: 오프라인 모드에서도 기본 대시보드 표시
- ✅ **해결됨**: 에러 처리 개선으로 사용자 경험 향상
- ✅ **해결됨**: 타임아웃 설정으로 빠른 실패 처리

### 6. WebSocket 연결 실패

#### 문제
```
WebSocket connection to 'ws://localhost:5000/socket.io/' failed
```

#### 해결 방법
- ✅ **해결됨**: Socket.IO 자동 재연결 비활성화
- ✅ **해결됨**: 서버 상태 확인 후 연결 시도
- ✅ **해결됨**: 연결 실패 시 조용한 오프라인 모드 전환

## 서버 오류 해결

### 1. 데이터베이스 연결 오류

#### 문제
```
sqlite3.OperationalError: unable to open database file
```

#### 해결 방법
```bash
# 데이터베이스 테이블 생성
python create_sync_tables.py
```

### 2. 마이그레이션 오류

#### 문제
```
CircularDependencyError: Circular dependency detected
```

#### 해결 방법
- ✅ **해결됨**: 별도 스크립트로 동기화 테이블 생성
- 기존 마이그레이션과 분리하여 처리

### 3. Outbox 워커 오류

#### 문제
```
Worker not initialized
```

#### 해결 방법
```bash
# 워커 별도 실행
python start_outbox_worker.py
```

## 네트워크 문제 해결

### 1. 로컬 네트워크 설정

#### Windows
```bash
# IP 주소 확인
ipconfig

# 방화벽 규칙 추가
netsh advfirewall firewall add rule name="Flask Server" dir=in action=allow protocol=TCP localport=5000
```

#### 모바일 앱 설정
```typescript
// mobile_app/src/api/socket.ts
const WS_URL = "ws://YOUR_IP:5000"; // 실제 IP로 변경

// mobile_app/src/api/client.ts  
const BASE_URL = "http://YOUR_IP:5000"; // 실제 IP로 변경
```

### 2. CORS 오류

#### 문제
```
Access to XMLHttpRequest at 'http://localhost:5000' from origin 'http://localhost:8081' has been blocked by CORS policy
```

#### 해결 방법
- ✅ **해결됨**: Flask 앱에서 CORS 설정 완료
- `app.py`에서 `CORS(app)` 설정 확인

## 개발 환경 설정

### 1. 필요한 패키지 설치

```bash
# 백엔드
pip install -r requirements.txt

# 모바일 앱
cd mobile_app
npm install
```

### 2. 환경 변수 설정

```bash
# 모바일 앱
cp mobile_app/env.example mobile_app/.env
# .env 파일에서 API_URL, WS_URL 수정
```

### 3. 서버 시작 순서

```bash
# 1. 데이터베이스 테이블 생성
python create_sync_tables.py

# 2. 서버 시작 (자동으로 워커도 시작)
python start_server.py

# 3. 모바일 앱 시작
cd mobile_app
npm start
```

## 테스트 방법

### 1. 서버 테스트
```bash
# 헬스체크
curl http://localhost:5000/healthz

# 동기화 시스템 테스트
python test_sync_system.py
```

### 2. 모바일 앱 테스트
```bash
# 개발 서버 시작
cd mobile_app
npm start

# 웹 브라우저에서 테스트
# http://localhost:8081
```

## 로그 확인

### 1. 서버 로그
- Flask 서버: 콘솔 출력
- Outbox 워커: 콘솔 출력
- 데이터베이스: `instance/your_program_dev.db`

### 2. 모바일 앱 로그
- 브라우저 개발자 도구 콘솔
- React Native Debugger
- Expo 개발자 도구

## 성능 최적화

### 1. 배치 크기 조정
```typescript
// mobile_app/src/services/BatchSyncService.ts
private readonly BATCH_SIZE = 50; // 필요에 따라 조정
```

### 2. 동기화 간격 조정
```typescript
private readonly SYNC_INTERVAL = 30000; // 30초, 필요에 따라 조정
```

### 3. 재시도 설정
```typescript
private readonly MAX_RETRIES = 3; // 최대 재시도 횟수
```

## 추가 도움

문제가 지속되면 다음을 확인하세요:

1. **네트워크 연결**: 인터넷 연결 상태
2. **방화벽 설정**: 포트 5000 접근 허용
3. **서버 로그**: 오류 메시지 확인
4. **브라우저 캐시**: 하드 새로고침 (Ctrl+Shift+R)
5. **Node.js 버전**: 최신 LTS 버전 사용 권장

---

💡 **팁**: 개발 중에는 `localhost`를 사용하고, 실제 디바이스 테스트 시에는 실제 IP 주소를 사용하세요.
