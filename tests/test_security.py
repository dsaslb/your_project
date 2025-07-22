import pytest
import jwt
import time
from app import app
from security.jwt_auth import jwt_auth
from security.oauth2_auth import oauth2_manager
from security.two_factor_auth import two_factor_auth
from security.security_middleware import security_middleware
from models_main import User, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def test_user():
    """테스트 사용자 생성"""
    user = User(
        username='testuser',
        email='test@example.com',
        role='employee'
    )
    user.set_password('testpassword123')
    db.session.add(user)
    db.session.commit()
    return user

class TestJWTAuthentication:
    """JWT 인증 테스트"""
    
    def test_jwt_token_generation(self, test_user):
        """JWT 토큰 생성 테스트"""
        tokens = jwt_auth.generate_tokens(test_user)
        
        assert 'access_token' in tokens
        assert 'refresh_token' in tokens
        assert 'token_type' in tokens
        assert 'expires_in' in tokens
        assert tokens['token_type'] == 'Bearer'
    
    def test_jwt_token_verification(self, test_user):
        """JWT 토큰 검증 테스트"""
        tokens = jwt_auth.generate_tokens(test_user)
        access_token = tokens['access_token']
        
        # 유효한 토큰 검증
        payload = jwt_auth.verify_token(access_token)
        assert payload is not None
        assert payload['user_id'] == test_user.id
        assert payload['username'] == test_user.username
        assert payload['role'] == test_user.role
    
    def test_jwt_token_refresh(self, test_user):
        """JWT 토큰 갱신 테스트"""
        tokens = jwt_auth.generate_tokens(test_user)
        refresh_token = tokens['refresh_token']
        
        # 토큰 갱신
        new_tokens = jwt_auth.refresh_access_token(refresh_token)
        assert new_tokens is not None
        assert 'access_token' in new_tokens
        assert 'token_type' in new_tokens
    
    def test_jwt_invalid_token(self):
        """잘못된 JWT 토큰 테스트"""
        invalid_token = "invalid.token.here"
        payload = jwt_auth.verify_token(invalid_token)
        assert payload is None
    
    def test_jwt_expired_token(self, test_user):
        """만료된 JWT 토큰 테스트"""
        # 만료된 토큰 생성
        expired_payload = {
            'user_id': test_user.id,
            'username': test_user.username,
            'role': test_user.role,
            'exp': time.time() - 3600,  # 1시간 전
            'iat': time.time() - 7200,
            'type': 'access'
        }
        
        expired_token = jwt.encode(
            expired_payload, 
            jwt_auth.secret_key, 
            algorithm=jwt_auth.algorithm
        )
        
        payload = jwt_auth.verify_token(expired_token)
        assert payload is None

class TestOAuth2Authentication:
    """OAuth2 인증 테스트"""
    
    def test_oauth_provider_registration(self):
        """OAuth 제공자 등록 테스트"""
        # Google OAuth2 제공자 테스트
        google_provider = oauth2_manager.get_provider('google')
        if google_provider:
            assert google_provider.client_id is not None
            assert google_provider.client_secret is not None
            assert google_provider.redirect_uri is not None
    
    def test_oauth_authorization_url(self):
        """OAuth 인증 URL 생성 테스트"""
        google_provider = oauth2_manager.get_provider('google')
        if google_provider:
            auth_url = google_provider.get_authorization_url("test_state")
            assert auth_url.startswith("https://accounts.google.com")
            assert "client_id" in auth_url
            assert "redirect_uri" in auth_url
            assert "response_type=code" in auth_url
    
    def test_oauth_user_info_normalization(self):
        """OAuth 사용자 정보 정규화 테스트"""
        # Google 사용자 정보 예시
        google_user_info = {
            'id': '123456789',
            'email': 'test@gmail.com',
            'name': 'Test User',
            'picture': 'https://example.com/photo.jpg'
        }
        
        normalized = oauth2_manager._normalize_user_info('google', google_user_info)
        assert normalized['id'] == '123456789'
        assert normalized['email'] == 'test@gmail.com'
        assert normalized['name'] == 'Test User'
        assert normalized['provider'] == 'google'
        
        # Kakao 사용자 정보 예시
        kakao_user_info = {
            'id': 987654321,
            'kakao_account': {
                'email': 'test@kakao.com'
            },
            'properties': {
                'nickname': '카카오사용자',
                'profile_image': 'https://example.com/kakao.jpg'
            }
        }
        
        normalized = oauth2_manager._normalize_user_info('kakao', kakao_user_info)
        assert normalized['id'] == 987654321
        assert normalized['email'] == 'test@kakao.com'
        assert normalized['name'] == '카카오사용자'
        assert normalized['provider'] == 'kakao'

class TestTwoFactorAuthentication:
    """2단계 인증 테스트"""
    
    def test_totp_secret_generation(self):
        """TOTP 시크릿 키 생성 테스트"""
        secret = two_factor_auth.generate_totp_secret()
        assert len(secret) == 32
        assert secret.isalnum()
    
    def test_totp_qr_code_generation(self, test_user):
        """TOTP QR 코드 생성 테스트"""
        secret = two_factor_auth.generate_totp_secret()
        qr_code = two_factor_auth.generate_totp_qr_code(test_user, secret)
        
        assert qr_code is not None
        assert qr_code.startswith("data:image/png;base64,")
    
    def test_totp_code_verification(self):
        """TOTP 코드 검증 테스트"""
        secret = two_factor_auth.generate_totp_secret()
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        # 유효한 코드 검증
        assert two_factor_auth.verify_totp_code(secret, code) is True
        
        # 잘못된 코드 검증
        assert two_factor_auth.verify_totp_code(secret, "000000") is False
    
    def test_backup_codes_generation(self):
        """백업 코드 생성 테스트"""
        backup_codes = two_factor_auth.generate_backup_codes(5)
        
        assert len(backup_codes) == 5
        for code in backup_codes:
            assert len(code) == 8
            assert code.isalnum()
    
    def test_2fa_setup(self, test_user):
        """2FA 설정 테스트"""
        setup_data = two_factor_auth.setup_totp(test_user)
        
        assert setup_data is not None
        assert 'secret' in setup_data
        assert 'qr_code' in setup_data
        assert 'backup_codes' in setup_data
        assert len(setup_data['backup_codes']) == 10
    
    def test_2fa_enable_disable(self, test_user):
        """2FA 활성화/비활성화 테스트"""
        # 2FA 설정
        setup_data = two_factor_auth.setup_totp(test_user)
        secret = setup_data['secret']
        backup_codes = setup_data['backup_codes']
        
        # TOTP 코드 생성
        totp = pyotp.TOTP(secret)
        verification_code = totp.now()
        
        # 2FA 활성화
        assert two_factor_auth.enable_totp(test_user, secret, backup_codes) is True
        assert test_user.two_factor_enabled is True
        assert test_user.two_factor_method == 'totp'
        
        # 2FA 비활성화
        assert two_factor_auth.disable_2fa(test_user) is True
        assert test_user.two_factor_enabled is False
        assert test_user.two_factor_method is None

class TestSecurityMiddleware:
    """보안 미들웨어 테스트"""
    
    def test_password_strength_validation(self):
        """비밀번호 강도 검증 테스트"""
        # 강한 비밀번호
        strong_password = "MySecurePassword123!"
        result = security_middleware.validate_password_strength(strong_password)
        assert result['valid'] is True
        assert len(result['errors']) == 0
        assert result['score'] >= 80
        
        # 약한 비밀번호
        weak_password = "123"
        result = security_middleware.validate_password_strength(weak_password)
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert result['score'] < 50
        
        # 일반적인 비밀번호
        common_password = "password"
        result = security_middleware.validate_password_strength(common_password)
        assert result['valid'] is False
        assert any("일반적인 비밀번호" in error for error in result['errors'])
    
    def test_csrf_token_generation(self):
        """CSRF 토큰 생성 테스트"""
        token = security_middleware.generate_csrf_token()
        assert len(token) == 64  # 32바이트 hex = 64자
        assert token.isalnum()
    
    def test_csrf_token_validation(self):
        """CSRF 토큰 검증 테스트"""
        token = security_middleware.generate_csrf_token()
        session_token = token
        
        # 유효한 토큰 검증
        assert security_middleware.validate_csrf_token(token, session_token) is True
        
        # 잘못된 토큰 검증
        assert security_middleware.validate_csrf_token(token, "wrong_token") is False
    
    def test_input_sanitization(self):
        """입력 데이터 정제 테스트"""
        # HTML 태그가 포함된 입력
        dirty_input = "<script>alert('xss')</script>Hello World"
        sanitized = security_middleware.sanitize_input(dirty_input)
        
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized
        assert "Hello World" in sanitized
        
        # SQL 인젝션 시도
        sql_input = "'; DROP TABLE users; --"
        sanitized = security_middleware.sanitize_input(sql_input)
        
        assert "';" not in sanitized
        assert "DROP TABLE" not in sanitized
        assert "--" not in sanitized

class TestSecurityAPI:
    """보안 API 테스트"""
    
    def test_jwt_login_api(self, client, test_user):
        """JWT 로그인 API 테스트"""
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpassword123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'tokens' in data
        assert 'user' in data
    
    def test_jwt_login_invalid_credentials(self, client):
        """잘못된 자격증명으로 JWT 로그인 테스트"""
        response = client.post('/api/auth/login', json={
            'username': 'wronguser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_protected_api_without_token(self, client):
        """토큰 없이 보호된 API 접근 테스트"""
        response = client.get('/api/protected/profile')
        assert response.status_code == 401
    
    def test_protected_api_with_token(self, client, test_user):
        """토큰과 함께 보호된 API 접근 테스트"""
        # 먼저 로그인하여 토큰 획득
        login_response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpassword123'
        })
        tokens = login_response.get_json()['tokens']
        
        # 토큰과 함께 보호된 API 호출
        response = client.get('/api/protected/profile', headers={
            'Authorization': f"Bearer {tokens['access_token']}"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'profile' in data
    
    def test_password_validation_api(self, client):
        """비밀번호 검증 API 테스트"""
        response = client.post('/api/security/password/validate', json={
            'password': 'MySecurePassword123!'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'result' in data
        assert data['result']['valid'] is True
    
    def test_csrf_token_api(self, client):
        """CSRF 토큰 API 테스트"""
        response = client.get('/api/security/csrf/token')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'csrf_token' in data

class TestSecurityHeaders:
    """보안 헤더 테스트"""
    
    def test_security_headers_present(self, client):
        """보안 헤더 존재 확인 테스트"""
        response = client.get('/')
        
        # XSS 보호 헤더
        assert 'X-XSS-Protection' in response.headers
        assert response.headers['X-XSS-Protection'] == '1; mode=block'
        
        # 클릭재킹 방지 헤더
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'DENY'
        
        # MIME 타입 스니핑 방지 헤더
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        
        # Content Security Policy 헤더
        assert 'Content-Security-Policy' in response.headers
        
        # Referrer Policy 헤더
        assert 'Referrer-Policy' in response.headers
        assert response.headers['Referrer-Policy'] == 'strict-origin-when-cross-origin'

class TestRateLimiting:
    """Rate Limiting 테스트"""
    
    def test_rate_limiting_basic(self, client):
        """기본 Rate Limiting 테스트"""
        # 여러 요청을 빠르게 보내기
        responses = []
        for _ in range(105):  # 기본 제한(100)을 초과
            response = client.get('/api/status')
            responses.append(response.status_code)
        
        # 일부 요청이 429 (Too Many Requests) 상태를 반환해야 함
        assert 429 in responses
    
    def test_rate_limiting_exempt_paths(self, client):
        """Rate Limiting 제외 경로 테스트"""
        # 제외된 경로는 Rate Limiting이 적용되지 않아야 함
        for _ in range(10):
            response = client.get('/health')
            assert response.status_code == 200  # 항상 성공해야 함 