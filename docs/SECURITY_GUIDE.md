# 보안 가이드

이 문서는 멀티테넌시 관리 시스템의 보안 기능과 모범 사례를 설명합니다.

## 🔐 인증 시스템

### JWT 토큰 기반 인증

#### 토큰 구조
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

#### JWT 로그인
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "securepassword123"
  }'
```

#### 보호된 API 접근
```bash
curl -X GET http://localhost:5000/api/protected/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 토큰 갱신
```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### OAuth2 소셜 로그인

#### 지원하는 제공자
- **Google OAuth2**: Gmail 계정으로 로그인
- **Kakao OAuth2**: 카카오 계정으로 로그인

#### OAuth2 로그인 플로우
```bash
# 1. 인증 URL 요청
curl -X GET http://localhost:5000/api/auth/oauth/google/login

# 2. 브라우저에서 인증 URL로 리다이렉트
# 3. OAuth 제공자에서 인증 후 콜백 URL로 리다이렉트
# 4. 콜백에서 JWT 토큰 발급
```

#### OAuth2 설정
```python
# 환경 변수 설정
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/api/auth/oauth/google/callback

KAKAO_CLIENT_ID=your_kakao_client_id
KAKAO_CLIENT_SECRET=your_kakao_client_secret
KAKAO_REDIRECT_URI=http://localhost:5000/api/auth/oauth/kakao/callback
```

### 2단계 인증 (2FA)

#### TOTP 기반 2FA
```bash
# 1. 2FA 설정
curl -X POST http://localhost:5000/api/auth/2fa/setup \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 2. QR 코드를 Google Authenticator 등으로 스캔
# 3. 2FA 활성화
curl -X POST http://localhost:5000/api/auth/2fa/enable \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "TOTP_SECRET",
    "backup_codes": ["CODE1", "CODE2", ...],
    "verification_code": "123456"
  }'

# 4. 2FA 인증 (로그인 시)
curl -X POST http://localhost:5000/api/auth/2fa/verify \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "code": "123456",
    "method": "totp"
  }'
```

#### 백업 코드 사용
```bash
curl -X POST http://localhost:5000/api/auth/2fa/verify \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "code": "BACKUP123",
    "method": "backup"
  }'
```

#### 2FA 비활성화
```bash
curl -X POST http://localhost:5000/api/auth/2fa/disable \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "your_password"
  }'
```

## 🛡️ 보안 미들웨어

### 보안 헤더
- **X-XSS-Protection**: XSS 공격 방지
- **X-Frame-Options**: 클릭재킹 방지
- **X-Content-Type-Options**: MIME 타입 스니핑 방지
- **Strict-Transport-Security**: HTTPS 강제
- **Content-Security-Policy**: 콘텐츠 보안 정책
- **Referrer-Policy**: 리퍼러 정보 제어
- **Permissions-Policy**: 권한 정책

### Rate Limiting
```python
# 기본 설정: 분당 100개 요청
RATE_LIMIT_DEFAULT = '100 per minute'

# 제외된 경로
exempt_paths = ['/health', '/metrics', '/static/']
```

### CORS 설정
```python
CORS_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5000',
    'https://your-domain.com'
]
CORS_ALLOW_CREDENTIALS = True
```

### CSRF 보호
```bash
# CSRF 토큰 요청
curl -X GET http://localhost:5000/api/security/csrf/token

# CSRF 토큰과 함께 요청
curl -X POST http://localhost:5000/api/protected/endpoint \
  -H "X-CSRF-Token: YOUR_CSRF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data": "value"}'
```

## 🔒 비밀번호 보안

### 비밀번호 정책
```python
PASSWORD_POLICY = {
    'min_length': 8,           # 최소 8자
    'max_length': 128,         # 최대 128자
    'require_uppercase': True, # 대문자 필수
    'require_lowercase': True, # 소문자 필수
    'require_digits': True,    # 숫자 필수
    'require_special_chars': False, # 특수문자 권장
    'prevent_common_passwords': True, # 일반적인 비밀번호 방지
    'prevent_sequential_chars': True, # 연속 문자 방지
    'prevent_repeated_chars': True    # 반복 문자 방지
}
```

### 비밀번호 강도 검증
```bash
curl -X POST http://localhost:5000/api/security/password/validate \
  -H "Content-Type: application/json" \
  -d '{
    "password": "MySecurePassword123!"
  }'
```

#### 응답 예시
```json
{
  "success": true,
  "result": {
    "valid": true,
    "errors": [],
    "warnings": ["특수문자를 포함하는 것을 권장합니다"],
    "score": 85
  }
}
```

## 🔐 권한 관리

### 역할 기반 접근 제어 (RBAC)
```python
# 역할별 권한
ROLES = {
    'system_admin': ['all'],
    'brand_admin': ['brand_management', 'user_management'],
    'store_manager': ['store_management', 'employee_management'],
    'employee': ['attendance', 'schedule']
}
```

### API 권한 데코레이터
```python
from security.jwt_auth import require_role, require_permission

@app.route("/api/admin/users")
@jwt_required
@require_role(['admin', 'system_admin'])
def admin_users():
    """관리자 전용 사용자 목록"""
    pass

@app.route("/api/modules/manage")
@jwt_required
@require_permission('module_management')
def manage_modules():
    """모듈 관리 권한 필요"""
    pass
```

## 📊 보안 모니터링

### 보안 이벤트 로깅
```python
from security.security_middleware import security_middleware

# 보안 이벤트 로깅
security_middleware.log_security_event('failed_login', {
    'username': 'testuser',
    'ip_address': '192.168.1.100',
    'user_agent': 'Mozilla/5.0...'
})
```

### 로그인 시도 제한
```python
LOGIN_ATTEMPT_LIMIT = 5      # 최대 5회 시도
LOGIN_ATTEMPT_WINDOW = 300   # 5분 제한
ACCOUNT_LOCKOUT_DURATION = 1800  # 30분 잠금
```

## 🔧 보안 설정

### 환경별 설정
```python
# 개발 환경
class DevelopmentConfig(SecurityConfig):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    STRICT_TRANSPORT_SECURITY = None

# 프로덕션 환경
class ProductionConfig(SecurityConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    STRICT_TRANSPORT_SECURITY = 'max-age=31536000; includeSubDomains'
```

### 필수 환경 변수
```bash
# JWT 설정
JWT_SECRET_KEY=your-super-secret-jwt-key

# OAuth2 설정
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
KAKAO_CLIENT_ID=your_kakao_client_id
KAKAO_CLIENT_SECRET=your_kakao_client_secret

# 이메일 설정 (2FA용)
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# SMS 설정 (2FA용)
SMS_API_KEY=your_sms_api_key
SMS_SECRET_KEY=your_sms_secret_key
```

## 🚨 보안 모범 사례

### 1. 토큰 관리
- **액세스 토큰**: 1시간 만료
- **리프레시 토큰**: 7일 만료
- **토큰 저장**: HttpOnly 쿠키 또는 메모리
- **토큰 전송**: HTTPS만 사용

### 2. 비밀번호 보안
- **최소 길이**: 8자 이상
- **복잡성**: 대문자, 소문자, 숫자 포함
- **정기 변경**: 90일마다 권장
- **해시 알고리즘**: bcrypt 사용

### 3. 세션 관리
- **세션 만료**: 1시간
- **세션 고정 방지**: 로그인 시 세션 재생성
- **동시 세션 제한**: 필요시 설정

### 4. API 보안
- **HTTPS 강제**: 모든 API 통신
- **Rate Limiting**: API 남용 방지
- **입력 검증**: 모든 사용자 입력 검증
- **SQL 인젝션 방지**: 파라미터화된 쿼리 사용

### 5. 파일 업로드 보안
- **파일 타입 제한**: 허용된 확장자만
- **파일 크기 제한**: 최대 10MB
- **바이러스 스캔**: 업로드된 파일 검사
- **안전한 저장**: 웹 루트 외부 저장

### 6. 로그 및 모니터링
- **보안 이벤트 로깅**: 모든 보안 관련 이벤트
- **실시간 모니터링**: 비정상 활동 감지
- **알림 시스템**: 보안 위협 시 즉시 알림
- **로그 보관**: 90일간 보관

## 🔍 보안 테스트

### 자동화된 보안 테스트
```bash
# 보안 테스트 실행
pytest tests/test_security.py -v

# 특정 보안 기능 테스트
pytest tests/test_security.py::TestJWTAuthentication -v
pytest tests/test_security.py::TestTwoFactorAuthentication -v
```

### 수동 보안 테스트
```bash
# JWT 토큰 검증 테스트
curl -X GET http://localhost:5000/api/protected/profile \
  -H "Authorization: Bearer INVALID_TOKEN"

# Rate Limiting 테스트
for i in {1..110}; do
  curl -X GET http://localhost:5000/api/status
done

# CSRF 보호 테스트
curl -X POST http://localhost:5000/api/protected/endpoint \
  -H "Content-Type: application/json" \
  -d '{"data": "value"}'
```

## 📋 보안 체크리스트

### 초기 설정
- [ ] JWT_SECRET_KEY 변경
- [ ] OAuth2 클라이언트 ID/Secret 설정
- [ ] 이메일/SMS 설정 (2FA용)
- [ ] HTTPS 인증서 설정
- [ ] 방화벽 설정

### 정기 점검
- [ ] 보안 로그 검토
- [ ] 사용자 권한 검토
- [ ] 비밀번호 정책 준수 확인
- [ ] 보안 업데이트 적용
- [ ] 백업 데이터 보안 확인

### 모니터링
- [ ] 로그인 실패 패턴 모니터링
- [ ] API 사용량 모니터링
- [ ] 비정상 접근 패턴 감지
- [ ] 시스템 리소스 모니터링
- [ ] 보안 이벤트 알림 설정

이 가이드를 따라 시스템의 보안을 강화하고 안전한 서비스를 제공할 수 있습니다. 