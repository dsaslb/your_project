import os
from datetime import timedelta

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# 환경 인식: FLASK_ENV 값으로 .env 파일 선택
env = os.getenv("FLASK_ENV", "development")
env_file = f".env.{env}"
if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    load_dotenv(".env.development")  # Fallback


class Config:
    """기본 설정 클래스"""

    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///restaurant_dev.sqlite3"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = bool(int(os.getenv("DEBUG", "0")))

    # 파일 업로드 설정
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16MB
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

    # 이메일 설정
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")

    # 로깅 설정
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # 기본값 INFO
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

    # Slack 알림 설정
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
    SLACK_ENABLED = bool(os.getenv("SLACK_ENABLED", "0"))

    # 보안 헤더
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "SAMEORIGIN",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    }

    # 캐시 설정
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

    # 세션 설정
    PERMANENT_SESSION_LIFETIME = int(
        os.getenv("PERMANENT_SESSION_LIFETIME", 3600)
    )  # 1시간
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # CSRF 설정
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get("CSRF_SECRET_KEY", "csrf-key")

    # Rate limiting
    RATELIMIT_DEFAULT = "10 per minute"

    # 대시보드 모드 설정
    # 'solo': 1인 사장님 버전 (모든 메뉴 표시)
    # 'franchise': 그룹/프랜차이즈 버전 (최고관리자 메뉴만 표시)
    DASHBOARD_MODE = os.environ.get("DASHBOARD_MODE", "solo")

    # 알림 설정
    NOTIFICATION_ENABLED = (
        os.environ.get("NOTIFICATION_ENABLED", "true").lower() == "true"
    )

    # 개발/운영 환경 구분
    DEBUG = os.environ.get("FLASK_ENV") == "development"

    # 보안 설정
    SESSION_COOKIE_SECURE = (
        os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    )
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # API 설정
    API_RATE_LIMIT = os.environ.get("API_RATE_LIMIT", "100 per minute")

    # 백업 설정
    BACKUP_ENABLED = os.environ.get("BACKUP_ENABLED", "true").lower() == "true"
    BACKUP_RETENTION_DAYS = int(os.environ.get("BACKUP_RETENTION_DAYS", 30))

    # 통계/리포트 설정
    STATS_ENABLED = os.environ.get("STATS_ENABLED", "true").lower() == "true"

    # 다국어 설정
    LANGUAGES = ["ko", "en"]
    DEFAULT_LANGUAGE = "ko"

    # 테마 설정
    THEME = os.environ.get("THEME", "default")  # 'default', 'dark', 'modern'

    # 기능 토글
    FEATURES = {
        "attendance_tracking": True,
        "payroll_management": True,
        "inventory_management": True,
        "order_management": True,
        "cleaning_schedule": True,
        "notification_system": True,
        "report_generation": True,
        "user_management": True,
        "approval_system": True,
        "analytics_dashboard": True,
        "mobile_support": True,
        "api_access": True,
        "backup_restore": True,
        "audit_logging": True,
        "multi_branch": True,
        "franchise_mode": DASHBOARD_MODE == "franchise",
    }


class DevelopmentConfig(Config):
    """개발 환경 설정"""

    DEBUG = True
    TESTING = False

    # 개발 환경에서는 보안 헤더 완화
    SECURITY_HEADERS = {}

    # 개발 환경에서는 HTTP 쿠키 허용
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # 개발용 로깅 - 상세한 디버그 정보
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    LOG_FILE = os.getenv("LOG_FILE", "logs/restaurant_dev.log")

    DASHBOARD_MODE = "solo"  # 개발 시에는 1인 사장님 모드


class ProductionConfig(Config):
    """운영 환경 설정"""

    DEBUG = False
    TESTING = False

    # 운영 환경 보안 강화
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"

    # 운영용 로깅 - WARNING 이상만 기록
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
    LOG_FILE = os.getenv("LOG_FILE", "logs/restaurant_prod.log")

    DASHBOARD_MODE = os.environ.get("DASHBOARD_MODE", "franchise")  # 운영 시 기본값


class TestConfig(Config):
    """테스트 환경 설정"""

    TESTING = True
    DEBUG = True

    # In-memory-db
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # CSRF protection disabled for tests
    WTF_CSRF_ENABLED = False

    # Reduce password hashing rounds for speed
    BCRYPT_LOG_ROUNDS = 4

    # Secret key for JWT
    JWT_SECRET_KEY = "test-secret-key"

    # 테스트용 보안 헤더 완화
    SECURITY_HEADERS = {}

    # 테스트용 로깅 - 디버그 정보 포함
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    LOG_FILE = os.getenv("LOG_FILE", "logs/restaurant_test.log")

    DASHBOARD_MODE = "solo"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # 또는 테스트용 DB URL
    WTF_CSRF_ENABLED = False


# 설정 매핑
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "test": TestConfig,
    "default": DevelopmentConfig,
    "testing": TestingConfig,
}

# COOKIE_SECURE 설정 (app.py에서 import용)
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "False").lower() == "true"
