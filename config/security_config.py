"""
보안 설정 파일
JWT, OAuth2, 2FA, 보안 미들웨어 설정
"""

import os
from datetime import timedelta

class SecurityConfig:
    """보안 설정 클래스"""
    
    # JWT 설정
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-super-secret-jwt-key-change-this-in-production')
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    
    # OAuth2 설정
    # Google OAuth2
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5000/api/auth/oauth/google/callback')
    
    # Kakao OAuth2
    KAKAO_CLIENT_ID = os.environ.get('KAKAO_CLIENT_ID', '')
    KAKAO_CLIENT_SECRET = os.environ.get('KAKAO_CLIENT_SECRET', '')
    KAKAO_REDIRECT_URI = os.environ.get('KAKAO_REDIRECT_URI', 'http://localhost:5000/api/auth/oauth/kakao/callback')
    
    # 2FA 설정
    TOTP_ISSUER = os.environ.get('TOTP_ISSUER', 'Your Program')
    TOTP_WINDOW = 30  # TOTP 시간 윈도우 (초)
    BACKUP_CODES_COUNT = 10  # 백업 코드 개수
    
    # SMS 설정 (2FA용)
    SMS_API_KEY = os.environ.get('SMS_API_KEY', '')
    SMS_SECRET_KEY = os.environ.get('SMS_SECRET_KEY', '')
    SMS_FROM_NUMBER = os.environ.get('SMS_FROM_NUMBER', '')
    
    # 이메일 설정 (2FA용)
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', '')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
    EMAIL_USE_TLS = True
    
    # Rate Limiting 설정
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_DEFAULT = '100 per minute'
    RATE_LIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
    
    # CORS 설정
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5000',
        'https://your-domain.com'
    ]
    CORS_ALLOW_CREDENTIALS = True
    
    # 보안 헤더 설정
    SECURITY_HEADERS = {
        'X_XSS_PROTECTION': '1; mode=block',
        'X_FRAME_OPTIONS': 'DENY',
        'X_CONTENT_TYPE_OPTIONS': 'nosniff',
        'STRICT_TRANSPORT_SECURITY': 'max-age=31536000; includeSubDomains',
        'CONTENT_SECURITY_POLICY': [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "img-src 'self' data: https:",
            "font-src 'self' https://cdn.jsdelivr.net",
            "connect-src 'self' ws: wss:",
            "frame-ancestors 'none'"
        ],
        'REFERRER_POLICY': 'strict-origin-when-cross-origin',
        'PERMISSIONS_POLICY': 'geolocation=(), microphone=(), camera=()'
    }
    
    # 비밀번호 정책
    PASSWORD_POLICY = {
        'min_length': 8,
        'max_length': 128,
        'require_uppercase': True,
        'require_lowercase': True,
        'require_digits': True,
        'require_special_chars': False,  # 권장사항
        'prevent_common_passwords': True,
        'prevent_sequential_chars': True,
        'prevent_repeated_chars': True
    }
    
    # 세션 설정
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_MAX_AGE = 3600  # 1시간
    
    # 로그인 시도 제한
    LOGIN_ATTEMPT_LIMIT = 5  # 최대 로그인 시도 횟수
    LOGIN_ATTEMPT_WINDOW = 300  # 제한 시간 (초)
    ACCOUNT_LOCKOUT_DURATION = 1800  # 계정 잠금 시간 (초)
    
    # API 키 설정
    API_KEY_HEADER = 'X-API-Key'
    API_KEY_LENGTH = 32
    
    # 감사 로그 설정
    AUDIT_LOG_ENABLED = True
    AUDIT_LOG_LEVEL = 'INFO'
    AUDIT_LOG_RETENTION_DAYS = 90
    
    # 암호화 설정
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', 'your-encryption-key-change-this')
    ENCRYPTION_ALGORITHM = 'AES-256-GCM'
    
    # 파일 업로드 보안
    ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    UPLOAD_PATH = '/secure/uploads'
    
    # SQL 인젝션 방지
    SQL_INJECTION_PROTECTION = True
    PARAMETERIZED_QUERIES_ONLY = True
    
    # XSS 방지
    XSS_PROTECTION = True
    INPUT_SANITIZATION = True
    
    # CSRF 보호
    CSRF_PROTECTION = True
    CSRF_TOKEN_EXPIRES = 3600  # 1시간
    
    # 보안 모니터링
    SECURITY_MONITORING_ENABLED = True
    ALERT_EMAIL = os.environ.get('SECURITY_ALERT_EMAIL', 'security@your-domain.com')
    
    @classmethod
    def get_oauth_config(cls, provider: str) -> dict:
        """OAuth 제공자별 설정 반환"""
        configs = {
            'google': {
                'client_id': cls.GOOGLE_CLIENT_ID,
                'client_secret': cls.GOOGLE_CLIENT_SECRET,
                'redirect_uri': cls.GOOGLE_REDIRECT_URI,
                'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'userinfo_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
                'scope': 'openid email profile'
            },
            'kakao': {
                'client_id': cls.KAKAO_CLIENT_ID,
                'client_secret': cls.KAKAO_CLIENT_SECRET,
                'redirect_uri': cls.KAKAO_REDIRECT_URI,
                'auth_url': 'https://kauth.kakao.com/oauth/authorize',
                'token_url': 'https://kauth.kakao.com/oauth/token',
                'userinfo_url': 'https://kapi.kakao.com/v2/user/me',
                'scope': ''
            }
        }
        return configs.get(provider, {})
    
    @classmethod
    def is_production(cls) -> bool:
        """프로덕션 환경 여부 확인"""
        return os.environ.get('FLASK_ENV') == 'production'
    
    @classmethod
    def get_secret_key(cls) -> str:
        """시크릿 키 반환"""
        if cls.is_production():
            return os.environ.get('SECRET_KEY', cls.JWT_SECRET_KEY)
        return cls.JWT_SECRET_KEY
    
    @classmethod
    def validate_config(cls) -> list:
        """설정 유효성 검증"""
        errors = []
        
        # 필수 설정 검증
        if not cls.JWT_SECRET_KEY or cls.JWT_SECRET_KEY == 'your-super-secret-jwt-key-change-this-in-production':
            errors.append("JWT_SECRET_KEY가 설정되지 않았습니다")
        
        if cls.is_production():
            if not cls.GOOGLE_CLIENT_ID:
                errors.append("프로덕션 환경에서 GOOGLE_CLIENT_ID가 설정되지 않았습니다")
            
            if not cls.KAKAO_CLIENT_ID:
                errors.append("프로덕션 환경에서 KAKAO_CLIENT_ID가 설정되지 않았습니다")
        
        # 비밀번호 정책 검증
        if cls.PASSWORD_POLICY['min_length'] < 6:
            errors.append("최소 비밀번호 길이는 6자 이상이어야 합니다")
        
        if cls.PASSWORD_POLICY['max_length'] < cls.PASSWORD_POLICY['min_length']:
            errors.append("최대 비밀번호 길이는 최소 길이보다 커야 합니다")
        
        return errors

# 환경별 설정
class DevelopmentConfig(SecurityConfig):
    """개발 환경 설정"""
    DEBUG = True
    TESTING = False
    
    # 개발 환경에서는 보안 설정을 완화
    SESSION_COOKIE_SECURE = False
    STRICT_TRANSPORT_SECURITY = None
    
    # 개발용 OAuth 리다이렉트 URI
    GOOGLE_REDIRECT_URI = 'http://localhost:5000/api/auth/oauth/google/callback'
    KAKAO_REDIRECT_URI = 'http://localhost:5000/api/auth/oauth/kakao/callback'

class ProductionConfig(SecurityConfig):
    """프로덕션 환경 설정"""
    DEBUG = False
    TESTING = False
    
    # 프로덕션 환경에서는 모든 보안 설정 활성화
    SESSION_COOKIE_SECURE = True
    STRICT_TRANSPORT_SECURITY = 'max-age=31536000; includeSubDomains'
    
    # 프로덕션용 OAuth 리다이렉트 URI
    GOOGLE_REDIRECT_URI = 'https://your-domain.com/api/auth/oauth/google/callback'
    KAKAO_REDIRECT_URI = 'https://your-domain.com/api/auth/oauth/kakao/callback'

class TestingConfig(SecurityConfig):
    """테스트 환경 설정"""
    DEBUG = True
    TESTING = True
    
    # 테스트용 설정
    JWT_SECRET_KEY = 'test-secret-key'
    SESSION_COOKIE_SECURE = False
    RATE_LIMIT_ENABLED = False

# 설정 매핑
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_config(env: str = None) -> SecurityConfig:
    """환경에 따른 설정 반환"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class() 