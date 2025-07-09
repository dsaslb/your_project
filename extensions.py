from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# 데이터베이스
db = SQLAlchemy()
migrate = Migrate()

# 로그인 매니저
login_manager = LoginManager()

# 요청 제한 (메모리 저장소 명시적 설정)
limiter = Limiter(
    key_func=get_remote_address, 
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # 메모리 저장소 명시적 설정
)

# 캐싱
cache = Cache()

# CSRF 보호
csrf = CSRFProtect()


def init_extensions(app):
    """모든 확장 기능을 초기화합니다."""
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
