# 🔒 보안 시스템

퀀텀 비즈니스 관리 시스템의 보안 모듈입니다. 사용자 인증, 권한 관리, 보안 모니터링 등의 기능을 제공합니다.

## 주요 기능

### 🔐 인증 및 권한 관리
- **JWT 토큰 기반 인증**: 안전한 토큰 기반 인증 시스템
- **역할 기반 접근 제어 (RBAC)**: 사용자 역할에 따른 권한 관리
- **세션 관리**: 사용자 세션 생성, 검증, 무효화
- **비밀번호 보안**: bcrypt를 사용한 안전한 비밀번호 해싱

### 🛡️ 보안 모니터링
- **로그인 시도 추적**: 실패한 로그인 시도 모니터링
- **계정 잠금**: 과도한 로그인 시도 시 계정 자동 잠금
- **보안 이벤트 로깅**: 모든 보안 관련 이벤트 기록
- **실시간 알림**: 의심스러운 활동 감지 시 알림

### 📊 보안 통계
- **활성 세션 수**: 현재 로그인된 사용자 수
- **보안 점수**: 시스템 전반의 보안 상태 점수
- **이벤트 통계**: 24시간 내 보안 이벤트 통계
- **실패 로그인**: 24시간 내 실패한 로그인 시도 수

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r security/requirements.txt
```

### 2. 환경 변수 설정
```bash
# .env 파일 생성
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
PASSWORD_MIN_LENGTH=8
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
SESSION_TIMEOUT_MINUTES=60
```

### 3. 보안 시스템 초기화
```python
from security.security_manager import SecurityManager, SecurityConfig

# 보안 설정
config = SecurityConfig(
    jwt_secret="your-secret-key",
    jwt_expiration_hours=24,
    password_min_length=8,
    max_login_attempts=5,
    lockout_duration_minutes=30,
    session_timeout_minutes=60
)

# 보안 관리자 초기화
security_manager = SecurityManager(config)
```

## API 엔드포인트

### 인증 관련
- `POST /api/security/login` - 사용자 로그인
- `POST /api/security/logout` - 사용자 로그아웃
- `POST /api/security/validate-token` - 토큰 유효성 검증
- `POST /api/security/change-password` - 비밀번호 변경
- `POST /api/security/validate-password` - 비밀번호 강도 검증

### 세션 관리 (관리자만)
- `GET /api/security/sessions` - 활성 세션 조회
- `DELETE /api/security/sessions/{session_id}` - 세션 무효화
- `POST /api/security/cleanup` - 만료된 세션 정리

### 보안 이벤트 (관리자만)
- `GET /api/security/events` - 보안 이벤트 조회
- `PUT /api/security/events/{event_id}/status` - 이벤트 상태 업데이트
- `GET /api/security/stats` - 보안 통계 조회

### 시스템 상태
- `GET /api/security/health` - 보안 시스템 상태 확인

## 사용 예시

### 로그인
```javascript
const response = await fetch('/api/security/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});

const data = await response.json();
// 토큰 저장
localStorage.setItem('auth_token', data.token);
localStorage.setItem('session_id', data.session_id);
```

### 인증이 필요한 API 호출
```javascript
const response = await fetch('/api/security/sessions', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
    'X-Session-ID': localStorage.getItem('session_id')
  }
});
```

### 비밀번호 변경
```javascript
const response = await fetch('/api/security/change-password', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
  },
  body: JSON.stringify({
    current_password: 'oldpassword',
    new_password: 'newpassword123'
  })
});
```

## 보안 기능 상세

### 비밀번호 정책
- 최소 8자 이상
- 대문자, 소문자, 숫자, 특수문자 포함 권장
- 비밀번호 강도 점수 시스템 (0-100점)

### 계정 보호
- 5회 연속 로그인 실패 시 계정 잠금
- 30분 후 자동 잠금 해제
- IP 주소 기반 로그인 시도 추적

### 세션 관리
- 60분 비활성 시 세션 자동 만료
- 동시 세션 지원
- 세션 무효화 기능

### 보안 이벤트
- 로그인 성공/실패
- 비밀번호 변경
- 세션 생성/무효화
- 의심스러운 활동 감지

## 프론트엔드 통합

### 보안 페이지 접근
```
http://localhost:3000/security
```

### 주요 기능
- **보안 대시보드**: 실시간 보안 통계 표시
- **이벤트 모니터링**: 보안 이벤트 실시간 조회
- **세션 관리**: 활성 세션 관리 및 무효화
- **로그인/로그아웃**: 사용자 인증 관리
- **비밀번호 변경**: 안전한 비밀번호 변경

## 모니터링 및 알림

### 보안 점수 계산
- 실패한 로그인 시도: -2점/시도
- 잠긴 계정: -5점/계정
- 치명적 보안 이벤트: -10점/이벤트

### 권장 보안 점수
- **90-100점**: 우수
- **70-89점**: 양호
- **50-69점**: 주의
- **0-49점**: 위험

## 개발 가이드라인

### 새로운 보안 기능 추가
1. `SecurityManager` 클래스에 메서드 추가
2. API 엔드포인트 구현
3. 프론트엔드 컴포넌트 개발
4. 테스트 코드 작성

### 보안 이벤트 추가
```python
security_manager.log_security_event(
    user_id=user_id,
    event_type='custom_event',
    description='사용자 정의 이벤트',
    ip_address=request.remote_addr,
    user_agent=request.headers.get('User-Agent', ''),
    severity='medium'
)
```

## 문제 해결

### 일반적인 문제
1. **토큰 만료**: 로그인 페이지로 리다이렉트
2. **권한 부족**: 403 에러 반환
3. **계정 잠금**: 30분 후 재시도
4. **세션 만료**: 자동 로그아웃

### 로그 확인
```bash
# 보안 이벤트 로그
tail -f logs/security.log

# 애플리케이션 로그
tail -f logs/app.log
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 