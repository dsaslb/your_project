# 🔐 인증 및 권한 관리 시스템

퀀텀 비즈니스 관리 시스템의 인증 및 권한 관리 모듈입니다. JWT 기반 인증, 역할 기반 접근 제어(RBAC), 보안 모니터링 등의 기능을 제공합니다.

## 주요 기능

### 🔑 사용자 인증
- **JWT 토큰 인증**: 액세스 토큰과 리프레시 토큰 기반 인증
- **비밀번호 보안**: bcrypt를 사용한 안전한 비밀번호 해시화
- **세션 관리**: 사용자 세션 추적 및 관리
- **계정 잠금**: 로그인 실패 시 자동 계정 잠금

### 🛡️ 역할 기반 접근 제어 (RBAC)
- **역할 관리**: 관리자, 매니저, 직원 등 역할 정의
- **권한 관리**: 리소스별 세부 권한 설정
- **권한 상속**: 역할별 권한 그룹 관리
- **동적 권한 검증**: 실시간 권한 확인

### 🔒 보안 기능
- **비밀번호 정책**: 강력한 비밀번호 요구사항
- **로그인 추적**: 로그인 시도 및 실패 기록
- **보안 이벤트**: 모든 보안 관련 활동 로깅
- **IP 주소 추적**: 접속 IP 주소 및 User-Agent 기록

### 📊 관리 도구
- **사용자 관리**: 사용자 생성, 수정, 잠금 해제
- **역할 관리**: 역할 및 권한 할당
- **보안 모니터링**: 실시간 보안 이벤트 추적
- **통계 대시보드**: 인증 시스템 현황 파악

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r auth/requirements.txt
```

### 2. 환경 변수 설정
```bash
# .env 파일 생성
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_TOKEN_EXPIRY_HOURS=24
JWT_REFRESH_TOKEN_EXPIRY_DAYS=7
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
PASSWORD_MIN_LENGTH=8
REQUIRE_SPECIAL_CHARS=true
REQUIRE_NUMBERS=true
REQUIRE_UPPERCASE=true
SESSION_TIMEOUT_MINUTES=60
```

### 3. 인증 시스템 초기화
```python
from auth.auth_manager import AuthManager, AuthConfig

# 인증 설정
config = AuthConfig(
    secret_key="your-secret-key",
    token_expiry_hours=24,
    refresh_token_expiry_days=7,
    max_login_attempts=5,
    lockout_duration_minutes=30,
    password_min_length=8,
    require_special_chars=True,
    require_numbers=True,
    require_uppercase=True,
    session_timeout_minutes=60
)

# 인증 관리자 초기화
auth_manager = AuthManager(config)
```

## API 엔드포인트

### 인증 관련
- `POST /api/auth/login` - 사용자 로그인
- `POST /api/auth/logout` - 사용자 로그아웃
- `POST /api/auth/refresh` - 토큰 갱신
- `GET /api/auth/validate` - 토큰 검증
- `POST /api/auth/change-password` - 비밀번호 변경
- `POST /api/auth/validate-password` - 비밀번호 정책 검증

### 사용자 관리
- `GET /api/auth/users` - 사용자 목록 조회 (권한 필요: users_manage)
- `POST /api/auth/users` - 사용자 생성 (권한 필요: users_manage)
- `POST /api/auth/users/{user_id}/unlock` - 계정 잠금 해제 (권한 필요: users_manage)

### 역할 및 권한 관리
- `GET /api/auth/roles` - 역할 목록 조회 (권한 필요: users_manage)
- `GET /api/auth/permissions` - 권한 목록 조회 (권한 필요: users_manage)

### 보안 모니터링
- `GET /api/auth/security-events` - 보안 이벤트 조회 (권한 필요: users_manage)
- `GET /api/auth/profile` - 현재 사용자 프로필 조회
- `GET /api/auth/health` - 인증 시스템 상태 확인

## 사용 예시

### 사용자 로그인
```javascript
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'Admin123!'
  })
});

const result = await response.json();
if (result.status === 'success') {
  const { access_token, refresh_token, user } = result.data;
  // 토큰을 로컬 스토리지에 저장
  localStorage.setItem('access_token', access_token);
  localStorage.setItem('refresh_token', refresh_token);
}
```

### 인증이 필요한 API 호출
```javascript
const response = await fetch('/api/auth/users', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': 'application/json'
  }
});
```

### 토큰 갱신
```javascript
const response = await fetch('/api/auth/refresh', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    refresh_token: localStorage.getItem('refresh_token')
  })
});

const result = await response.json();
if (result.status === 'success') {
  const { access_token, refresh_token } = result.data;
  localStorage.setItem('access_token', access_token);
  localStorage.setItem('refresh_token', refresh_token);
}
```

### 사용자 생성
```javascript
const response = await fetch('/api/auth/users', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'newuser',
    email: 'user@example.com',
    password: 'SecurePass123!',
    full_name: '새 사용자',
    role: 'employee'
  })
});
```

## 인증 기능 상세

### JWT 토큰 구조
- **액세스 토큰**: 24시간 유효, API 접근용
- **리프레시 토큰**: 7일 유효, 토큰 갱신용
- **페이로드**: 사용자 ID, 사용자명, 역할, 만료 시간

### 비밀번호 정책
- **최소 길이**: 8자 이상
- **대문자**: 최소 1개 포함
- **숫자**: 최소 1개 포함
- **특수문자**: 최소 1개 포함
- **해시화**: bcrypt 알고리즘 사용

### 계정 보안
- **로그인 시도 제한**: 5회 실패 시 계정 잠금
- **잠금 해제**: 관리자가 수동으로 해제
- **세션 관리**: 활성 세션 추적
- **IP 추적**: 접속 IP 주소 기록

### 역할 및 권한
- **관리자 (admin)**: 모든 권한
- **매니저 (manager)**: 매장 관리, 직원 관리 권한
- **직원 (employee)**: 기본 업무 권한

### 기본 권한 목록
- `dashboard_read`: 대시보드 조회
- `users_manage`: 사용자 관리
- `stores_manage`: 매장 관리
- `inventory_manage`: 재고 관리
- `orders_manage`: 주문 관리
- `reports_view`: 보고서 조회
- `settings_manage`: 설정 관리

## 프론트엔드 통합

### 인증 페이지 접근
```
http://localhost:3000/auth
```

### 주요 기능
- **사용자 관리**: 사용자 목록, 생성, 계정 잠금 해제
- **역할 관리**: 역할 목록 및 권한 확인
- **권한 관리**: 시스템 권한 목록
- **보안 이벤트**: 실시간 보안 이벤트 모니터링
- **비밀번호 변경**: 사용자 비밀번호 변경

### 인증 상태 관리
```javascript
// 로그인 상태 확인
const checkAuthStatus = async () => {
  try {
    const response = await fetch('/api/auth/validate', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    if (response.ok) {
      const result = await response.json();
      return result.data;
    }
    return null;
  } catch (error) {
    return null;
  }
};

// 권한 확인
const checkPermission = (userPermissions, requiredPermission) => {
  return userPermissions.includes(requiredPermission);
};
```

## 보안 모니터링

### 보안 이벤트 유형
- **login_success**: 로그인 성공
- **login_failed**: 로그인 실패
- **logout**: 로그아웃
- **password_change_success**: 비밀번호 변경 성공
- **password_change_failed**: 비밀번호 변경 실패
- **account_locked**: 계정 잠금

### 이벤트 심각도
- **info**: 일반 정보
- **warning**: 경고
- **error**: 오류
- **critical**: 치명적 오류

### 모니터링 지표
- 총 사용자 수
- 활성 세션 수
- 역할 및 권한 수
- 보안 이벤트 통계

## 개발 가이드라인

### 새로운 권한 추가
```python
# 권한 생성
permission_id = auth_manager.create_permission(
    name='custom_permission',
    description='사용자 정의 권한',
    resource='custom_resource',
    action='custom_action'
)

# 역할에 권한 추가
role = auth_manager.get_role_by_name('manager')
role.permissions.append('custom_permission')
auth_manager._save_role(role)
```

### 사용자 정의 인증 로직
```python
# 사용자 정의 인증 검증
def custom_auth_check(user_id, resource, action):
    user = auth_manager.get_user_by_id(user_id)
    if not user:
        return False
    
    permissions = auth_manager.get_user_permissions(user_id)
    required_permission = f"{resource}_{action}"
    
    return required_permission in permissions
```

### 보안 이벤트 로깅
```python
# 사용자 정의 보안 이벤트 로깅
auth_manager._log_security_event(
    user_id="user123",
    event_type="custom_event",
    ip_address="192.168.1.1",
    user_agent="Custom App/1.0",
    details={"action": "custom_action", "result": "success"},
    severity="info"
)
```

## 문제 해결

### 일반적인 문제
1. **토큰 만료**: 리프레시 토큰으로 새로운 액세스 토큰 발급
2. **권한 오류**: 사용자 역할 및 권한 확인
3. **계정 잠금**: 관리자가 계정 잠금 해제
4. **비밀번호 오류**: 비밀번호 정책 확인

### 로그 확인
```bash
# 인증 로그
tail -f logs/auth.log

# 보안 이벤트 로그
tail -f logs/security.log
```

### 성능 최적화
- 토큰 만료 시간 조정
- 세션 정리 주기 설정
- 데이터베이스 인덱스 최적화
- 캐싱 전략 적용

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 